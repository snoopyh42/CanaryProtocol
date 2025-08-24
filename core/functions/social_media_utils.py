#!/usr/bin/env python3
"""
Social Media utilities for Canary Protocol
Handles X/Twitter integration and social media analysis
"""

from typing import Dict, List, Any, Optional, Tuple
try:
    from .utils import log_error, log_info
except ImportError:
    from utils import log_error, log_info


def get_social_media_analysis(x_monitor: Optional[Any] = None) -> Dict[str, Any]:
    """Get social media analysis from X/Twitter monitoring"""
    if not x_monitor:
        return {
            'status': 'disabled',
            'analysis': 'Social media monitoring not configured',
            'urgency_boost': 0,
            'trends': [],
            'sentiment': 'neutral'
        }
    
    try:
        # Get social media trends and analysis
        trends = x_monitor.get_trending_topics()
        sentiment = x_monitor.analyze_political_sentiment()
        urgency_boost = x_monitor.get_urgency_boost_from_social()
        
        # Generate summary
        analysis_text = _format_social_analysis(trends, sentiment)
        
        return {
            'status': 'active',
            'analysis': analysis_text,
            'urgency_boost': urgency_boost,
            'trends': trends[:5],  # Top 5 trends
            'sentiment': sentiment.get('overall', 'neutral')
        }
        
    except Exception as e:
        log_error(f"Social media analysis error: {e}")
        return {
            'status': 'error',
            'analysis': f'Social media analysis unavailable: {str(e)}',
            'urgency_boost': 0,
            'trends': [],
            'sentiment': 'neutral'
        }


def _format_social_analysis(trends: List[Dict[str, Any]], sentiment: Dict[str, Any]) -> str:
    """Format social media analysis for inclusion in digest"""
    if not trends and not sentiment:
        return "No significant social media trends detected."
    
    analysis_parts = []
    
    # Add trending topics
    if trends:
        analysis_parts.append("**Trending Political Topics:**")
        for i, trend in enumerate(trends[:3], 1):
            topic = trend.get('topic', 'Unknown')
            volume = trend.get('tweet_volume', 0)
            analysis_parts.append(f"{i}. {topic} ({volume:,} mentions)")
    
    # Add sentiment analysis
    if sentiment:
        overall_sentiment = sentiment.get('overall', 'neutral')
        confidence = sentiment.get('confidence', 0)
        analysis_parts.append(f"\n**Overall Sentiment:** {overall_sentiment.title()} (confidence: {confidence:.1%})")
        
        # Add specific sentiment breakdowns if available
        if 'categories' in sentiment:
            for category, score in sentiment['categories'].items():
                if score > 0.6:  # Only show significant sentiment
                    analysis_parts.append(f"- {category.title()}: {score:.1%}")
    
    return "\n".join(analysis_parts) if analysis_parts else "Social media analysis inconclusive."


def initialize_x_monitor() -> Optional[Any]:
    """Initialize X/Twitter monitor if available and configured"""
    try:
        from x_monitor import XMonitor
        
        # Check if X API credentials are available
        import os
        if not os.getenv('X_BEARER_TOKEN'):
            log_info("X/Twitter monitoring disabled - no API credentials")
            return None
        
        monitor = XMonitor()
        log_info("X/Twitter monitoring initialized successfully")
        return monitor
        
    except ImportError:
        log_info("Social media monitoring module not available")
        return None
    except Exception as e:
        log_error(f"Failed to initialize X/Twitter monitoring: {e}")
        return None


def get_social_urgency_boost(x_monitor: Optional[Any] = None) -> int:
    """Get urgency boost from social media analysis"""
    if not x_monitor:
        return 0
    
    try:
        boost = x_monitor.get_urgency_boost_from_social()
        log_info(f"Social media urgency boost: +{boost}")
        return boost
    except Exception as e:
        log_error(f"Error getting social urgency boost: {e}")
        return 0


def format_social_media_section(social_analysis: Dict[str, Any]) -> str:
    """Format social media analysis for email/digest inclusion"""
    if social_analysis['status'] == 'disabled':
        return ""
    
    if social_analysis['status'] == 'error':
        return f"\n\n## 📱 SOCIAL MEDIA TRENDS\n*{social_analysis['analysis']}*"
    
    analysis = social_analysis['analysis']
    if not analysis or analysis == "No significant social media trends detected.":
        return ""
    
    # Format for inclusion in digest
    section = f"\n\n## 📱 SOCIAL MEDIA TRENDS\n{analysis}"
    
    # Add urgency note if there's a boost
    if social_analysis['urgency_boost'] > 0:
        section += f"\n\n*Social media activity contributed +{social_analysis['urgency_boost']} to urgency assessment*"
    
    return section


def is_social_monitoring_enabled() -> bool:
    """Check if social media monitoring is enabled and configured"""
    try:
        import os
        from x_monitor import XMonitor
        
        # Check for API credentials
        if not os.getenv('X_BEARER_TOKEN'):
            return False
        
        # Try to initialize (this will validate credentials)
        monitor = XMonitor()
        return True
        
    except Exception:
        return False
