#!/bin/bash
# Weekly Intelligent Digest with Learning

cd /home/ahansen/CanaryProtocol
source venv/bin/activate
export PATH="/home/ahansen/CanaryProtocol/venv/bin:$PATH"

echo "$(date): Starting weekly intelligent digest" >> logs/canary_cron.log

# Show weekly data summary
echo "$(date): Weekly data collection summary:" >> logs/canary_cron.log
python3 core/classes/daily_silent_collector.py --summary >> logs/canary_cron.log 2>&1

# Run the full intelligent analysis
python3 core/canary_protocol.py >> logs/canary_cron.log 2>&1

echo "$(date): Weekly intelligent digest completed" >> logs/canary_cron.log
