#!/bin/bash

echo "🧠 COMPLETE SMART CANARY PROTOCOL SETUP"
echo "======================================="
echo ""
echo "This script sets up:"
echo "• ✅ Adaptive intelligence features"
echo "• ✅ User feedback system"  
echo "• ✅ Hybrid learning approach (daily collection + weekly digests)"
echo "• ✅ Emergency detection"
echo "• ✅ Learning dashboard"
echo ""

# Check Python version
echo "📋 Checking Python environment..."
python3 --version
if ! python3 -c "import sqlite3; print('SQLite3 available')"; then
    echo "❌ Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Install additional requirements for smart features
echo "📦 Installing smart learning packages..."
pip3 install numpy scikit-learn matplotlib seaborn --quiet

# Initialize smart databases
echo "🗄️  Initializing adaptive intelligence database..."
python3 -c "
import sys
import os
sys.path.append('core')
sys.path.append('core/classes')
os.makedirs('data', exist_ok=True)
from adaptive_intelligence import AdaptiveIntelligence
intelligence = AdaptiveIntelligence('data/canary_protocol.db')
print('✅ Adaptive intelligence database initialized in data/ directory')
"

echo "🗄️  Initializing feedback system database..."
python3 -c "
import sys
import os
sys.path.append('core')
sys.path.append('core/classes')
os.makedirs('data', exist_ok=True)
from smart_feedback import FeedbackSystem
feedback = FeedbackSystem('data/canary_protocol.db')
print('✅ Feedback system database initialized in data/ directory')
"

# Create the daily silent collection cron job
echo "📅 Setting up hybrid learning system..."

# Create wrapper script for daily collection
cat > scripts/run_daily_collection.sh << 'EOF'
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
./canary collect >> logs/daily_collection.log 2>&1

# Check for emergency triggers
if ./canary collect --check-emergency | grep -q "EMERGENCY"; then
    echo "$(date): Emergency trigger detected" >> logs/daily_collection.log
    # Optional: Send emergency notification
    # ./canary run --emergency >> logs/daily_collection.log 2>&1
fi

echo "$(date): Daily collection completed" >> logs/daily_collection.log
EOF

chmod +x scripts/run_daily_collection.sh

# Update the weekly cron job to use collected data
cat > scripts/run_weekly_intelligent_digest.sh << 'EOF'
#!/bin/bash
# Weekly Intelligent Digest with Learning

cd /home/ahansen/CanaryProtocol
source venv/bin/activate
export PATH="/home/ahansen/CanaryProtocol/venv/bin:$PATH"

echo "$(date): Starting weekly intelligent digest" >> logs/canary_cron.log

# Show weekly data summary
echo "$(date): Weekly data collection summary:" >> logs/canary_cron.log
./canary collect --summary >> logs/canary_cron.log 2>&1

# Run the full intelligent analysis
./canary run >> logs/canary_cron.log 2>&1

echo "$(date): Weekly intelligent digest completed" >> logs/canary_cron.log
EOF

chmod +x scripts/run_weekly_intelligent_digest.sh

# Add both cron jobs
echo "🕒 Setting up cron jobs..."

# Get current crontab
crontab -l > temp_cron 2>/dev/null || touch temp_cron

# Check if cron jobs already exist
DAILY_EXISTS=$(grep -c "daily_silent_collector.py" temp_cron 2>/dev/null || echo "0")
WEEKLY_EXISTS=$(grep -c "canary_protocol.py" temp_cron 2>/dev/null || echo "0")

if [ "$DAILY_EXISTS" -gt "0" ] && [ "$WEEKLY_EXISTS" -gt "0" ]; then
    echo "✅ Cron jobs already exist - skipping setup"
    echo "   • Daily collection: Already configured"
    echo "   • Weekly digest: Already configured"
    rm temp_cron
else
    echo "📝 Installing cron jobs..."
    
    # Remove any existing Canary Protocol entries (clean duplicates)
    grep -v "Canary Protocol" temp_cron > temp_cron_clean 2>/dev/null || touch temp_cron_clean
    grep -v "daily_silent_collector.py" temp_cron_clean > temp_cron_clean2 2>/dev/null || touch temp_cron_clean2
    grep -v "canary_protocol.py" temp_cron_clean2 > temp_cron_final 2>/dev/null || touch temp_cron_final
    
    # Add daily collection (8 AM every day, silent)
    {
        echo "# Canary Protocol - Daily Silent Data Collection"
        echo "0 8 * * * cd $CANARY_ROOT && ./canary collect >> logs/canary_cron.log 2>&1"
        echo ""
        echo "# Canary Protocol - Weekly Intelligent Digest"
        echo "0 9 * * 1 cd $CANARY_ROOT && ./canary run >> logs/canary_cron.log 2>&1"
    } >> temp_cron_final
    
    # Install the new crontab
    crontab temp_cron_final
    rm temp_cron temp_cron_clean temp_cron_clean2 temp_cron_final
    
    echo " Cron jobs installed:"
    echo "   • Daily collection: 8 AM every day (silent)"
    echo "   • Weekly digest: 9 AM every Sunday (with emails)"
fi

echo "✅ Cron jobs installed:"
echo "   • Daily collection: 8 AM every day (silent)"
echo "   • Weekly digest: 9 AM every Sunday (with emails)"

# Create emergency analysis option
cat > scripts/emergency_analysis.sh << 'EOF'
#!/bin/bash
# Emergency Analysis Trigger

echo "🚨 EMERGENCY ANALYSIS MODE"
echo "========================="

cd /home/ahansen/CanaryProtocol
source venv/bin/activate
export PATH="/home/ahansen/CanaryProtocol/venv/bin:$PATH"

# Show recent emergency triggers
echo "Recent emergency triggers:"
./canary collect --check-emergency

echo ""
echo "Running immediate analysis..."

# Run immediate analysis with emergency flag
./canary run --emergency --verbose

echo ""
echo "Emergency analysis completed."
EOF

chmod +x scripts/emergency_analysis.sh

# Create monitoring dashboard
cat > scripts/learning_dashboard.sh << 'EOF'
#!/bin/bash
# Learning Progress Dashboard

echo "🧠 CANARY PROTOCOL LEARNING DASHBOARD"
echo "====================================="
echo ""

cd /home/ahansen/CanaryProtocol

# Daily collection summary
echo "📊 RECENT DATA COLLECTION:"
./canary collect --summary
echo ""

# Learning intelligence
echo "🎯 ADAPTIVE INTELLIGENCE:"
./canary dashboard
echo ""

# User feedback summary
echo "📝 USER FEEDBACK:"
./canary feedback-summary
echo ""

# Recent emergency triggers
echo "🚨 EMERGENCY TRIGGERS:"
./canary collect --check-emergency
echo ""

# Recent logs
echo "📋 RECENT ACTIVITY:"
echo "Daily Collection (last 5 entries):"
tail -n 5 logs/daily_collection.log 2>/dev/null || echo "No daily collection log found"
echo ""
echo "Weekly Digest (last 5 entries):"
tail -n 5 logs/canary_cron.log 2>/dev/null || echo "No weekly digest log found"
EOF

chmod +x scripts/learning_dashboard.sh

# Create daily learning check script
cat > scripts/daily_learning_check.sh << 'EOF'
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
EOF

chmod +x scripts/daily_learning_check.sh

# Create learning data backup script
cat > scripts/backup_learning_data.sh << 'EOF'
#!/bin/bash
# Backup learning data

BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup the database with learning data
cp data/canary_protocol.db "$BACKUP_DIR/canary_protocol_$DATE.db"

# Backup logs
cp -r logs "$BACKUP_DIR/logs_$DATE" 2>/dev/null || true

# Create learning summary
python3 -c "
import sys
sys.path.append('core/classes')
from adaptive_intelligence import AdaptiveIntelligence
from smart_feedback import FeedbackSystem

intelligence = AdaptiveIntelligence('data/canary_protocol.db')
feedback = FeedbackSystem('data/canary_protocol.db')

with open('$BACKUP_DIR/learning_summary_$DATE.txt', 'w') as f:
    f.write('LEARNING DATA BACKUP - $DATE\n')
    f.write('=' * 40 + '\n\n')
    f.write(intelligence.get_intelligence_report())
    f.write('\n\n')
    f.write(feedback.get_feedback_summary())
"

echo "✅ Learning data backed up to $BACKUP_DIR/"
EOF

chmod +x scripts/backup_learning_data.sh

# Test the system
echo ""
echo "🧪 Testing the smart system..."
./canary collect --verbose

echo ""
echo "✅ COMPLETE SMART CANARY PROTOCOL SETUP FINISHED!"
echo "================================================="
echo ""
echo "🎯 What's Now Running:"
echo "   • Daily silent data collection (8 AM) - no emails"
echo "   • Weekly intelligent analysis (Sunday 9 AM) - with emails"
echo "   • Emergency detection system"
echo "   • Adaptive learning from every digest"
echo ""
echo "🔧 Available Commands:"
echo "   scripts/learning_dashboard.sh      - View complete learning status"
echo "   scripts/emergency_analysis.sh      - Run emergency analysis"
echo "   scripts/daily_learning_check.sh    - Quick learning progress check"
echo "   scripts/backup_learning_data.sh    - Backup all learning data"
echo "   ./canary feedback - Provide user feedback"
echo ""
echo "📊 Log Files:"
echo "   logs/daily_collection.log         - Daily collection activity"
echo "   logs/canary_cron.log             - Weekly digest activity"
echo ""
echo "📈 Learning Timeline:"
echo "   Week 1-2: Basic pattern establishment"
echo "   Week 3-4: Pattern recognition active"
echo "   Month 2+: High accuracy predictions"
echo ""
echo "🚀 Next Steps:"
echo "1. Wait for daily collection to run tomorrow at 8 AM"
echo "2. Check learning progress: scripts/learning_dashboard.sh"
echo "3. Provide feedback after next Sunday's digest"
echo "4. Watch your Canary Protocol get smarter every day!"
echo ""
echo "🧠 Your Canary Protocol is now a learning system!"
