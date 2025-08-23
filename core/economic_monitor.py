#!/usr/bin/env python3
"""
Enhanced Economic Monitoring Module for Canary Protocol
"""

import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def get_market_indicators():
    """Fetch key market indicators that signal economic instability"""
    indicators = []
    
    try:
        # VIX (Fear Index) - High volatility indicates market fear
        vix = yf.Ticker("^VIX")
        vix_data = vix.history(period="5d")
        latest_vix = vix_data['Close'].iloc[-1]
        
        if latest_vix > 30:
            vix_status = "HIGH FEAR"
            concern_level = "high"
        elif latest_vix > 20:
            vix_status = "ELEVATED CONCERN" 
            concern_level = "medium"
        else:
            vix_status = "CALM"
            concern_level = "low"
            
        indicators.append({
            "indicator": "VIX Fear Index",
            "value": f"{latest_vix:.2f}",
            "status": vix_status,
            "concern_level": concern_level
        })
        
        # USD/Gold ratio - Flight to safety indicator
        gold = yf.Ticker("GC=F")
        gold_data = gold.history(period="5d")
        gold_change = ((gold_data['Close'].iloc[-1] / gold_data['Close'].iloc[0]) - 1) * 100
        
        if gold_change > 5:
            gold_status = "STRONG FLIGHT TO SAFETY"
            concern_level = "high"
        elif gold_change > 2:
            gold_status = "MODERATE SAFE HAVEN BUYING"
            concern_level = "medium"
        else:
            gold_status = "STABLE"
            concern_level = "low"
            
        indicators.append({
            "indicator": "Gold Price Movement (5d)",
            "value": f"{gold_change:+.2f}%",
            "status": gold_status,
            "concern_level": concern_level
        })
        
        # Dollar Index - Currency strength
        dxy = yf.Ticker("DX=F")
        dxy_data = dxy.history(period="5d")
        dxy_change = ((dxy_data['Close'].iloc[-1] / dxy_data['Close'].iloc[0]) - 1) * 100
        
        if abs(dxy_change) > 3:
            dxy_status = "HIGH VOLATILITY"
            concern_level = "medium"
        else:
            dxy_status = "STABLE"
            concern_level = "low"
            
        indicators.append({
            "indicator": "US Dollar Index (5d)",
            "value": f"{dxy_change:+.2f}%", 
            "status": dxy_status,
            "concern_level": concern_level
        })
        
    except Exception as e:
        indicators.append({
            "indicator": "Market Data",
            "value": "N/A",
            "status": f"Error fetching data: {str(e)[:50]}",
            "concern_level": "medium"
        })
    
    return indicators

def get_crypto_indicators():
    """Monitor cryptocurrency as alternative store of value"""
    try:
        btc = yf.Ticker("BTC-USD")
        btc_data = btc.history(period="5d")
        btc_change = ((btc_data['Close'].iloc[-1] / btc_data['Close'].iloc[0]) - 1) * 100
        
        if btc_change > 15:
            status = "STRONG ALTERNATIVE ASSET DEMAND"
            concern_level = "medium"
        elif btc_change < -15:
            status = "RISK-OFF SENTIMENT"
            concern_level = "medium"
        else:
            status = "STABLE"
            concern_level = "low"
            
        return {
            "indicator": "Bitcoin (5d trend)",
            "value": f"{btc_change:+.2f}%",
            "status": status,
            "concern_level": concern_level
        }
    except:
        return {
            "indicator": "Bitcoin",
            "value": "N/A",
            "status": "Data unavailable",
            "concern_level": "low"
        }

def format_economic_summary(indicators):
    """Format economic indicators for inclusion in digest"""
    summary = "## Economic Stability Indicators\n\n"
    
    high_concern = [i for i in indicators if i['concern_level'] == 'high']
    medium_concern = [i for i in indicators if i['concern_level'] == 'medium']
    
    if high_concern:
        summary += "### 🔴 HIGH CONCERN INDICATORS:\n"
        for indicator in high_concern:
            summary += f"- **{indicator['indicator']}**: {indicator['value']} - {indicator['status']}\n"
        summary += "\n"
    
    if medium_concern:
        summary += "### 🟠 MEDIUM CONCERN INDICATORS:\n"
        for indicator in medium_concern:
            summary += f"- **{indicator['indicator']}**: {indicator['value']} - {indicator['status']}\n"
        summary += "\n"
    
    low_concern = [i for i in indicators if i['concern_level'] == 'low']
    if low_concern:
        summary += "### 🟢 STABLE INDICATORS:\n"
        for indicator in low_concern:
            summary += f"- **{indicator['indicator']}**: {indicator['value']} - {indicator['status']}\n"
    
    return summary

if __name__ == "__main__":
    # Test the economic monitoring
    market_data = get_market_indicators()
    crypto_data = get_crypto_indicators()
    all_indicators = market_data + [crypto_data]
    
    print(format_economic_summary(all_indicators))
