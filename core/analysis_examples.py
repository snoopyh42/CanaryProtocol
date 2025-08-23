#!/usr/bin/env python3
"""
Analysis Quality Examples for Canary Protocol
Good vs Bad examples to improve AI-generated analysis
"""

ANALYSIS_EXAMPLES = {
    "political_stability": {
        "good": """
## 🏛️ POLITICAL & INSTITUTIONAL STABILITY (187 words)

The Supreme Court's decision in **[Smith v. Election Board](https://example.com/case)** this week upheld state voter ID requirements but struck down provisions requiring proof of citizenship for federal elections. This mixed ruling affects an estimated 2.3 million voters across 15 states.

Congress passed a continuing resolution extending government funding through December 15, avoiding a shutdown but highlighting ongoing partisan gridlock over immigration enforcement and defense spending. The 72-hour negotiation period saw unprecedented coordination between House leadership and moderate Democrats.

The Justice Department's investigation into state election processes expanded to include Arizona and Georgia, following complaints about ballot access restrictions. **[DOJ announces probe](https://example.com/doj)** reported potential violations of the Voting Rights Act affecting mail-in ballot deadlines.

Federal courts blocked implementation of Executive Order 14821 regarding sanctuary city funding, with three circuit courts issuing preliminary injunctions. The **[ruling affects $2.1 billion](https://example.com/funding)** in federal grants to 23 municipalities.
""",
        
        "bad": """
## 🏛️ POLITICAL & INSTITUTIONAL STABILITY

Things are getting really bad in politics. The Supreme Court made some decisions that could be terrible for democracy. There's a lot of fighting in Congress and people are worried about elections being stolen.

The government might shut down which would be catastrophic. Courts are blocking things left and right. Cities are losing money. Everything seems to be falling apart and heading toward chaos.

This reminds me of what happened in other countries before they had civil wars. We should all be very concerned about where this is heading.
"""
    },
    
    "safety_assessment": {
        "good": """
**LGBTQ+ Persons:** 🟠 MIXED (68 words)
The **[Tennessee legislature's SB-301](https://example.com/tn-law)** restricting gender-affirming care for minors faces federal court challenge, with preliminary injunction expected by September 1. Conversely, **[California's AB-957](https://example.com/ca-law)** strengthened anti-discrimination protections in healthcare and housing. Corporate support remains strong, with 847 companies signing anti-discrimination pledges, though 12 states have enacted restrictive legislation this year.

**Political Progressives:** 🟢 SAFE (71 words)
No significant targeting or persecution documented this week. **[FBI hate crime data](https://example.com/fbi-data)** shows politically motivated violence decreased 12% year-over-year. Progressive advocacy groups report normal operation levels across all states. Campaign finance restrictions in **[Texas HB-1847](https://example.com/tx-finance)** apply equally to all political organizations. Social media harassment remains at baseline levels per platform reporting.
""",
        
        "bad": """
**LGBTQ+ Persons:** 🔴 UNSAFE
Everything is terrible for LGBTQ+ people. Laws are being passed everywhere to hurt them. It's getting worse every day and they should probably leave the country.

**Political Progressives:** 🔴 UNSAFE
Conservatives are coming after progressives and it's really dangerous. They're trying to silence everyone who disagrees with them. Democracy is dying.
"""
    },
    
    "economic_indicators": {
        "good": """
## 📊 ECONOMIC STABILITY INDICATORS (142 words)

The VIX volatility index closed at 28.3 (+4.2 from last week), indicating elevated market anxiety but remaining below the 30 threshold that signals severe fear. **[S&P 500 declined 2.1%](https://example.com/market)** following Federal Reserve commentary on inflation persistence.

Housing market stress indicators show **[mortgage applications down 18%](https://example.com/housing)** year-over-year, with the 30-year fixed rate reaching 7.1%. However, employment remains stable with **[unemployment at 3.8%](https://example.com/employment)**, within historical normal ranges.

Consumer Price Index data released Wednesday showed **[core inflation at 4.1%](https://example.com/cpi)**, exceeding Federal Reserve targets but decelerating from last quarter's 4.7%. Energy costs drove most increases, with gasoline up 12% month-over-month due to refinery maintenance and geopolitical tensions.

Dollar strength index (DXY) gained 1.8% against major currencies, suggesting continued safe-haven demand despite domestic economic concerns.
""",
        
        "bad": """
## 📊 ECONOMIC STABILITY INDICATORS

The economy is collapsing and everyone should be worried. Stock markets are crashing and inflation is out of control. People can't afford houses anymore and jobs are disappearing.

The dollar is either too strong or too weak, nobody knows. Everything costs too much and it's getting worse every day. This is probably leading to a Great Depression.
"""
    }
}

def show_examples():
    """Display good vs bad analysis examples"""
    print("📊 CANARY PROTOCOL ANALYSIS QUALITY EXAMPLES")
    print("=" * 60)
    
    for category, examples in ANALYSIS_EXAMPLES.items():
        print(f"\n{category.upper().replace('_', ' ')}")
        print("-" * 40)
        
        print("\n✅ GOOD EXAMPLE:")
        print(examples["good"])
        
        print("\n❌ BAD EXAMPLE:")
        print(examples["bad"])
        
        print("\n" + "="*60)

QUALITY_GUIDELINES = """
📝 ANALYSIS QUALITY GUIDELINES

✅ GOOD ANALYSIS CHARACTERISTICS:
1. **Specific and Factual**: Includes numbers, dates, names, bill numbers
2. **Source Attribution**: Links to verifiable sources with titles
3. **Balanced Assessment**: Acknowledges both positive and negative developments
4. **Measurable Impact**: Quantifies effects (percentages, dollar amounts, population affected)
5. **Appropriate Tone**: Professional, measured, neither alarmist nor dismissive
6. **Actionable Information**: Provides context for decision-making
7. **Word Count Compliance**: Stays within specified ranges

❌ BAD ANALYSIS CHARACTERISTICS:
1. **Vague Language**: "Things are bad," "everything is terrible"
2. **No Sources**: Claims without attribution or links
3. **Emotional Language**: "Catastrophic," "collapsing," "chaos"
4. **Speculation**: Predicting civil war or societal collapse
5. **Hyperbolic Assessments**: Overuse of extreme status ratings
6. **Missing Context**: No comparison to baselines or historical norms
7. **Rambling Content**: Exceeds word limits or lacks focus

🎯 IMPROVEMENT STRATEGIES:
- Replace emotional words with specific descriptors
- Add quantitative data wherever possible
- Include authoritative source links
- Compare current situation to historical norms
- Use conditional language for uncertain outcomes
- Focus on actionable intelligence over opinion
"""

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("Show: (1) Examples, (2) Guidelines, (3) Both: ")
    
    if choice in ["1", "3"]:
        show_examples()
    
    if choice in ["2", "3"]:
        print(QUALITY_GUIDELINES)
