#!/bin/bash
# Daily learning check for Canary Protocol

echo "🧠 Daily Learning Check - $(date)"
echo "=============================="

# Show recent learning progress
python3 -c "
import sys
sys.path.append('core/classes')
from adaptive_intelligence import AdaptiveIntelligence
from smart_feedback import FeedbackSystem

intelligence = AdaptiveIntelligence('data/canary_protocol.db')
feedback = FeedbackSystem('data/canary_protocol.db')

print(intelligence.get_intelligence_report())
print(feedback.get_feedback_summary())
"

# Check for feedback opportunities
echo ""
echo "💭 Feedback Reminder:"
echo "If you've read recent digests, consider providing feedback:"
echo "  ./canary feedback"
