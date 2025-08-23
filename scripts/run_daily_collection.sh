#!/bin/bash
# Daily Silent Data Collection for Canary Protocol

# Navigate to the Canary Protocol directory
cd /home/ahansen/CanaryProtocol

# Activate virtual environment
source venv/bin/activate

# Set up environment
export PATH="/home/ahansen/CanaryProtocol/venv/bin:$PATH"

# Run daily collection with timestamp
echo "$(date): Starting daily collection" >> logs/daily_collection.log

# Run the collector
python3 core/daily_silent_collector.py >> logs/daily_collection.log 2>&1

# Check for emergency triggers
if python3 core/daily_silent_collector.py --check-emergency | grep -q "EMERGENCY"; then
    echo "$(date): Emergency trigger detected" >> logs/daily_collection.log
    # Optional: Send emergency notification
    # python3 core/canary_protocol.py --emergency >> logs/daily_collection.log 2>&1
fi

echo "$(date): Daily collection completed" >> logs/daily_collection.log
