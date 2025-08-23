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
sys.path.append('core')
from adaptive_intelligence import CanaryIntelligence
from smart_feedback import FeedbackSystem

intelligence = CanaryIntelligence('data/canary_protocol.db')
feedback = FeedbackSystem('data/canary_protocol.db')

with open('$BACKUP_DIR/learning_summary_$DATE.txt', 'w') as f:
    f.write('LEARNING DATA BACKUP - $DATE\n')
    f.write('=' * 40 + '\n\n')
    f.write(intelligence.get_intelligence_report())
    f.write('\n\n')
    f.write(feedback.get_feedback_summary())
"

echo "✅ Learning data backed up to $BACKUP_DIR/"
