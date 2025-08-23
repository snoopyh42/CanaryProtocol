#!/bin/bash
# Emergency Analysis Trigger

echo "🚨 EMERGENCY ANALYSIS MODE"
echo "========================="

cd /home/ahansen/CanaryProtocol
source venv/bin/activate
export PATH="/home/ahansen/CanaryProtocol/venv/bin:$PATH"

# Show recent emergency triggers
echo "Recent emergency triggers:"
python3 core/daily_silent_collector.py --check-emergency

echo ""
echo "Running immediate analysis..."

# Run immediate analysis with emergency flag
python3 core/canary_protocol.py --emergency --verbose

echo ""
echo "Emergency analysis completed."
