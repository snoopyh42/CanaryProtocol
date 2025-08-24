#!/bin/bash
# Backup learning data - Creates bundled tar.gz archive

BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
TEMP_DIR="temp_backup_$DATE"
BUNDLE_NAME="canary_backup_$DATE"

mkdir -p "$BACKUP_DIR"
mkdir -p "$TEMP_DIR/$BUNDLE_NAME"

# Create bundle directory structure
mkdir -p "$TEMP_DIR/$BUNDLE_NAME/data"
mkdir -p "$TEMP_DIR/$BUNDLE_NAME/config"
mkdir -p "$TEMP_DIR/$BUNDLE_NAME/logs"

# Backup the database
cp data/canary_protocol.db "$TEMP_DIR/$BUNDLE_NAME/data/" 2>/dev/null || true

# Backup custom configuration files
cp config/config.yaml "$TEMP_DIR/$BUNDLE_NAME/config/" 2>/dev/null || true
cp config/.env "$TEMP_DIR/$BUNDLE_NAME/config/" 2>/dev/null || true
cp config/email_template.html "$TEMP_DIR/$BUNDLE_NAME/config/" 2>/dev/null || true
cp config/subscribers.txt "$TEMP_DIR/$BUNDLE_NAME/config/" 2>/dev/null || true

# Backup logs
cp -r logs/* "$TEMP_DIR/$BUNDLE_NAME/logs/" 2>/dev/null || true

# Create learning summary
python3 -c "
import sys
sys.path.append('core')
sys.path.append('core/classes')
from adaptive_intelligence import AdaptiveIntelligence
from smart_feedback import FeedbackSystem

intelligence = AdaptiveIntelligence('data/canary_protocol.db')
feedback = FeedbackSystem('data/canary_protocol.db')

with open('$TEMP_DIR/$BUNDLE_NAME/learning_summary.txt', 'w') as f:
    f.write('LEARNING DATA BACKUP - $DATE\n')
    f.write('=' * 40 + '\n\n')
    f.write(intelligence.get_intelligence_report())
    f.write('\n\n')
    f.write(feedback.get_feedback_summary())
" 2>/dev/null || echo "Warning: Could not generate learning summary"

# Create backup metadata
cat > "$TEMP_DIR/$BUNDLE_NAME/backup_info.txt" << EOF
Backup Created: $DATE
Backup Type: Full System Backup
Contents:
- Database: data/canary_protocol.db
- Configuration files (custom only)
- All log files
- Learning summary report

To restore this backup:
./canary restore file $BUNDLE_NAME.tar.gz
EOF

# Create the compressed bundle
cd "$TEMP_DIR"
tar -czf "../$BACKUP_DIR/$BUNDLE_NAME.tar.gz" "$BUNDLE_NAME"
cd ..

# Generate SHA256 checksum
sha256sum "$BACKUP_DIR/$BUNDLE_NAME.tar.gz" > "$BACKUP_DIR/$BUNDLE_NAME.sha256"

# Clean up temporary directory
rm -rf "$TEMP_DIR"

echo "✅ Learning data backed up to $BACKUP_DIR/$BUNDLE_NAME.tar.gz"
echo "✅ SHA256 checksum saved to $BACKUP_DIR/$BUNDLE_NAME.sha256"
