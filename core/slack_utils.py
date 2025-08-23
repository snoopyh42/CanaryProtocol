#!/usr/bin/env python3
"""
Slack utilities for Canary Protocol
Handles Slack message formatting and sending
"""

import requests
import re
from datetime import datetime
from typing import List, Dict, Any
try:
    from .utils import log_error
except ImportError:
    from utils import log_error


def format_slack_message(summary_text: str) -> str:
    """Format summary text for Slack markdown"""
    slack_text = summary_text
    
    # Convert markdown headers to Slack format
    slack_text = re.sub(r'^#### (.*)$', r'*\1*', slack_text, flags=re.MULTILINE)
    slack_text = re.sub(r'^### (.*)$', r'*\1*', slack_text, flags=re.MULTILINE)
    slack_text = re.sub(r'^## (.*)$', r'*\1*', slack_text, flags=re.MULTILINE)
    slack_text = re.sub(r'^# (.*)$', r'*\1*', slack_text, flags=re.MULTILINE)
    
    # Convert bullet points and formatting
    slack_text = slack_text.replace("\n- ", "\n• ")
    slack_text = slack_text.replace("**", "*")
    slack_text = slack_text.replace("\n\n", "\n")
    
    return slack_text


def build_slack_blocks(summary_text: str) -> List[Dict[str, Any]]:
    """Build Slack blocks for rich formatting"""
    slack_text = format_slack_message(summary_text)
    
    blocks = [
        {
            "type": "section", 
            "text": {
                "type": "mrkdwn", 
                "text": f"*Canary Protocol Weekly Digest - {datetime.now().strftime('%B %d, %Y')}*"
            }
        },
        {"type": "divider"}
    ]

    # Split content into chunks for Slack's message limits
    chunk_size = 2900
    current_chunk = ""
    
    for line in slack_text.splitlines():
        # Start new section for headers
        if line.startswith("*") and line.endswith("*") and current_chunk:
            blocks.append({
                "type": "section", 
                "text": {"type": "mrkdwn", "text": current_chunk.strip()}
            })
            blocks.append({"type": "divider"})
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

    # Add final chunk if it exists
    if current_chunk.strip():
        blocks.append({
            "type": "section", 
            "text": {"type": "mrkdwn", "text": current_chunk.strip()}
        })

    return blocks


def send_to_slack(summary_text: str, webhook_url: str, test_mode: bool = False) -> bool:
    """Send message to Slack webhook"""
    
    if test_mode:
        _display_slack_preview(summary_text)
        return True
        
    if not webhook_url:
        log_error("Slack webhook URL missing.")
        return False

    try:
        blocks = build_slack_blocks(summary_text)
        slack_payload = {"blocks": blocks}

        response = requests.post(webhook_url, json=slack_payload)
        if response.status_code != 200:
            log_error(f"Slack webhook error: {response.status_code} {response.text}")
            return False
            
        print("✅ Message sent to Slack")
        return True
        
    except Exception as e:
        log_error(f"Slack send error: {e}")
        return False


def _display_slack_preview(summary_text: str) -> None:
    """Display Slack message preview in test mode"""
    print("\n" + "="*60)
    print("SLACK MESSAGE (TEST MODE - NOT SENT)")
    print("="*60)
    formatted_text = format_slack_message(summary_text)
    print(formatted_text[:1000] + "..." if len(formatted_text) > 1000 else formatted_text)
    print("="*60)
