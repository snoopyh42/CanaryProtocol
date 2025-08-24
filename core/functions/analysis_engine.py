#!/usr/bin/env python3
"""
Analysis Engine for Canary Protocol
Handles AI analysis and prompt generation
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
try:
    from .utils import log_error, log_info
except ImportError:
    from utils import log_error, log_info


def build_analysis_prompt(headlines: List[Dict[str, str]], economic_data: List[Dict[str, Any]], 
                         urgency_level: str = "LOW") -> str:
    """Build the comprehensive analysis prompt for AI"""
    
    # Include economic data in analysis
    economic_context = _build_economic_context(economic_data)
    joined_text = "\n".join([f"{h.get('title', 'No title')} - {h.get('url', 'No URL')}" for h in headlines])
    
    return f"""You are an expert political and economic analyst specializing in U.S. stability assessment. Your role is to provide objective, fact-based analysis for citizens monitoring potential risks.

ANALYSIS FRAMEWORK:
Current urgency level: {urgency_level}
Economic context: {economic_context}

INSTRUCTIONS:
1. Focus ONLY on U.S. domestic events and their direct impacts
2. Prioritize developments that affect civil liberties, democratic institutions, or economic stability
3. Use factual, measured language - avoid sensationalism but don't downplay genuine risks
4. Include clickable markdown links: **[article title](URL)** for all sources

REQUIRED SECTIONS:

## 🏛️ POLITICAL & INSTITUTIONAL STABILITY (150-250 words)
Analyze changes to:
- Democratic processes and voting rights
- Constitutional protections and civil liberties  
- Government emergency powers or extraordinary measures
- Supreme Court decisions affecting fundamental rights

## 📊 ECONOMIC STABILITY INDICATORS (100-200 words)
Assess:
- Market volatility and financial system stress
- Currency/inflation concerns affecting daily life
- Employment and housing market changes
- Economic policies impacting middle class

## 🛡️ SAFETY ASSESSMENT BY GROUP
For each group, provide: Status (🟢 SAFE | 🟠 MIXED | 🔴 UNSAFE) + brief explanation

**LGBTQ+ Persons:**
Status + recent policy/legal changes affecting rights and safety

**Political Progressives:**
Status + assessment of political climate and potential targeting

**Neurodivergent Individuals:**
Status + education, healthcare, and discrimination policy changes

**California Residents:**
Status + federal vs state conflicts, economic impacts, natural disasters

## 📈 TREND ANALYSIS (100-150 words)
- Week-over-week changes in key indicators
- Emerging patterns requiring attention
- Comparison to historical precedents if relevant

## 🎯 KEY TAKEAWAYS (75-125 words)
3-5 bullet points of most important developments for monitoring

Headlines to analyze:
{joined_text}

RESPONSE FORMAT: Use clear markdown headers, bullet points, and **bold links** to sources. Be thorough but concise.

FALLBACK INSTRUCTIONS FOR MISSING DATA:
- If fewer than 10 headlines available: Focus on quality over quantity, acknowledge limited data
- If no economic data: State "Economic indicators unavailable" and focus on news analysis
- If headlines lack URLs: Reference source name only, no markdown links
- If urgency level is unclear: Default to MEDIUM and explain uncertainty
- If group safety cannot be assessed: Mark as 🟠 MIXED with explanation of data limitations
- If no trend data available: Focus on current snapshot rather than changes over time

QUALITY STANDARDS:
- Each section must meet minimum word count or explain why it cannot
- Include confidence level in assessments when data is limited
- Distinguish between confirmed facts and reasonable inferences
- Always include at least one specific, measurable detail per section when possible"""


def _build_economic_context(economic_data: List[Dict[str, Any]]) -> str:
    """Build economic context string from economic indicators"""
    if not economic_data:
        return ""
    
    # Handle case where economic_data might contain strings or other types
    valid_indicators = []
    for item in economic_data:
        if isinstance(item, dict):
            valid_indicators.append(item)
        elif isinstance(item, str):
            # Skip string items that might have been passed incorrectly
            continue
    
    if not valid_indicators:
        return ""
    
    high_concern_econ = [e for e in valid_indicators if e.get('concern_level') == 'high']
    if high_concern_econ:
        return f"\n\nCurrent economic concerns: {', '.join([e['indicator'] + ': ' + e['status'] for e in high_concern_econ])}"
    return ""


def call_openai_analysis(openai_client, prompt: str, model: str = "gpt-4o", 
                        temperature: float = 0.2, max_tokens: int = 3000) -> str:
    """Make OpenAI API call with retry logic and error handling"""
    
    if not openai_client:
        log_error("OpenAI client not initialized")
        return "Error: OpenAI client not available"
    
    # Import RetryHandler from utils
    try:
        from utils import RetryHandler
    except ImportError:
        # Fallback without retry logic
        try:
            response = openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            log_error(f"OpenAI API call failed: {e}")
            return f"Error: Failed to generate analysis - {str(e)}"
    
    retry_handler = RetryHandler(max_retries=3, base_delay=2.0)
    
    def make_api_call():
        return openai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert political and economic analyst with 20+ years experience monitoring U.S. stability. You provide objective, factual analysis for informed citizens. Your assessments are measured, evidence-based, and actionable."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
    
    try:
        response = retry_handler.execute_with_retry(make_api_call)
        return response.choices[0].message.content.strip()
    except Exception as e:
        log_error(f"OpenAI API call failed after retries: {e}")
        # Return a more informative fallback summary
        return f"Analysis temporarily unavailable due to API limitations. Headlines processed: {len(prompt.split('Title:')) - 1 if 'Title:' in prompt else 'multiple'}. Please check logs for details."


def analyze_headlines_with_ai(openai_client, headlines: List[Dict[str, str]], 
                             economic_data: List[Dict[str, Any]] = None, 
                             urgency_level: str = "LOW", ai_config: Dict[str, Any] = None) -> str:
    """Main function to analyze headlines using AI"""
    
    if not headlines:
        return "Summary not available."
    
    # Use provided AI config or defaults
    config = ai_config or {}
    model = config.get('model', 'gpt-4o')
    temperature = config.get('temperature', 0.2)
    max_tokens = config.get('max_tokens', 3000)
    
    # Build the analysis prompt
    prompt = build_analysis_prompt(headlines, economic_data or [], urgency_level)
    
    # Make the API call
    return call_openai_analysis(openai_client, prompt, model, temperature, max_tokens)


def calculate_urgency_score(headlines: List[Dict[str, str]], economic_data: List[Dict[str, Any]], 
                           keywords: List[str], scoring_config: Dict[str, Any]) -> Tuple[int, str]:
    """Calculate urgency score based on headlines and economic data"""
    
    # Get scoring weights from config
    high_urgency_weight = scoring_config.get('high_urgency_keywords', 3)
    medium_urgency_weight = scoring_config.get('medium_urgency_keywords', 2)
    low_urgency_weight = scoring_config.get('low_urgency_keywords', 1)
    max_score = scoring_config.get('max_urgency_score', 10)
    urgent_threshold = scoring_config.get('urgent_analysis_score', 7.0)
    critical_threshold = scoring_config.get('critical_analysis_score', 4.0)
    
    urgency_score = 0
    all_text = " ".join([h.get('title', '') for h in headlines]).lower()
    
    # Analyze against configured keywords
    for keyword in keywords:
        if keyword.lower() in all_text:
            # Different weights based on keyword importance
            if any(term in keyword.lower() for term in ['crisis', 'crash', 'violence', 'fraud', 'martial', 'collapse']):
                urgency_score += high_urgency_weight
            elif any(term in keyword.lower() for term in ['recession', 'unemployment', 'discrimination', 'inflation']):
                urgency_score += medium_urgency_weight
            else:
                urgency_score += low_urgency_weight
    
    # Factor in economic indicators
    for indicator in economic_data:
        if indicator.get('concern_level') == 'high':
            urgency_score += medium_urgency_weight
        elif indicator.get('concern_level') == 'medium':
            urgency_score += low_urgency_weight
    
    # Cap at maximum score and determine level using configured thresholds
    urgency_score = min(urgency_score, max_score)
    
    if urgency_score >= urgent_threshold:
        return 10, "HIGH"
    elif urgency_score >= critical_threshold:
        return 5, "MEDIUM"
    else:
        return 1, "LOW"
