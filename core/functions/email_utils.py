#!/usr/bin/env python3
"""
Email utilities for Canary Protocol
Handles email formatting, sending, and template management
"""

import smtplib
import markdown2
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import List, Dict, Any, Optional
try:
    from .utils import log_error, load_file_lines
except ImportError:
    from utils import log_error, load_file_lines


def load_subscribers(filename: str = "config/subscribers.txt") -> List[str]:
    """Load email subscribers from file"""
    return load_file_lines(filename)


def build_email_content(summary_text: str, top_links_html: str, 
                       economic_data: Optional[List[Dict[str, Any]]] = None) -> str:
    """Build HTML email content from summary and links"""
    
    try:
        top_links = json.loads(top_links_html)
    except Exception:
        top_links = []

    # Add economic indicators to summary if available
    if economic_data:
        try:
            from economic_monitor import format_economic_summary
            economic_section = format_economic_summary(economic_data)
            summary_text = f"{summary_text}\n\n{economic_section}"
        except ImportError:
            pass

    summary_html = markdown2.markdown(summary_text)
    today = datetime.now().strftime("%B %d, %Y")

    # Build email components
    banner_block = _build_banner_block(today)
    legend_block = _build_legend_block()
    top_links_block = _build_links_block(top_links)
    footer_block = _build_footer_block()

    # Load email template
    template = _load_email_template()
    
    return template.format(
        banner_block=banner_block,
        legend_block=legend_block,
        summary_block=summary_html,
        top_links_block=top_links_block,
        footer_block=footer_block
    )


def _build_banner_block(date_str: str) -> str:
    """Build email banner block"""
    return f"""
    <div style='background-color:#003366; color:white; padding: 10px; text-align:center; font-size: 24px; font-weight: bold;'>
        The Canary Protocol Weekly Digest — {date_str}
    </div>
    """


def _build_legend_block() -> str:
    """Build legend block for safety indicators"""
    return """
    <div style='text-align:center; margin-bottom: 20px;'>
        <strong>Sentiment Legend:</strong>
        🟢 SAFE | 🟠 MIXED | 🔴 UNSAFE
    </div>
    <hr style='margin-top: 20px; margin-bottom: 20px; border: none; border-top: 2px solid #003366;'>
    """


def _build_links_block(links: List[Dict[str, str]]) -> str:
    """Build top links block"""
    links_html = ""
    for link in links:
        links_html += f"""
        <div style='margin-bottom: 12px;'>
            <div style='font-size: 14px;'>
                <a href='{link['url']}' target='_blank' style='color: #0066cc; text-decoration: none;'>
                    {link['title']}
                </a>
            </div>
        </div>
        """
    return links_html


def _build_footer_block() -> str:
    """Build email footer block"""
    return """
    <div style='text-align:center; font-size: 12px; color: #666; margin-top: 40px;'>
        Stay alert. Stay informed. 🕊️
    </div>
    """


def _load_email_template() -> str:
    """Load email template from config directory"""
    template_path = "config/email_template.html"
    try:
        with open(template_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        log_error(f"Email template not found at {template_path}")
        # Fallback to a basic template
        return """
        <html>
        <body>
        <h2>Smart Canary Protocol Alert</h2>
        {banner_block}
        {legend_block}
        {summary_block}
        {top_links_block}
        {footer_block}
        </body>
        </html>
        """


def send_email(subject: str, html_content: str, gmail_user: str, gmail_password: str,
               test_mode: bool = False) -> bool:
    """Send email to subscribers"""
    
    if test_mode:
        _display_email_preview(subject, html_content)
        return True
        
    try:
        # Validate email configuration
        if not gmail_user or not gmail_password:
            log_error("Email credentials not configured - check GMAIL_USER and GMAIL_APP_PASSWORD")
            return False
            
        subscribers = load_subscribers()
        if not subscribers:
            log_error("No subscribers to send to.")
            return False

        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = ", ".join(subscribers)
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, subscribers, msg.as_string())
            print(f"✅ Email sent to {len(subscribers)} subscribers")
            return True
            
    except Exception as e:
        log_error(f"Email sending error: {e}")
        return False


def _display_email_preview(subject: str, html_content: str) -> None:
    """Display email preview in test mode"""
    import re
    
    print("\n" + "="*60)
    print("EMAIL (TEST MODE - NOT SENT)")
    print("="*60)
    print(f"Subject: {subject}")
    print(f"To: {load_subscribers()}")
    print("\nHTML Content Preview:")
    print("-" * 40)
    
    # Convert HTML to readable text for preview
    text_content = re.sub('<[^<]+?>', '', html_content)
    text_content = re.sub(r'\n\s*\n', '\n\n', text_content)
    print(text_content[:2000] + "..." if len(text_content) > 2000 else text_content)
    print("="*60)
