#!/bin/bash
# Enhanced backup script for Smart Canary Protocol
# Integrates with production data management systems

# Source common functions if available, otherwise define locally
if [ -f "$(dirname "$0")/common.sh" ]; then
    source "$(dirname "$0")/common.sh"
else
    # Define essential functions locally
    log_info() {
        echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S'): $1"
    }
    
    log_error() {
        echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S'): $1" >&2
    }
    
    log_warning() {
        echo "[WARNING] $(date '+%Y-%m-%d %H:%M:%S'): $1"
    }
    
    create_directory() {
        mkdir -p "$1" 2>/dev/null || {
            log_error "Failed to create directory: $1"
            exit 1
        }
    }
fi

# Configuration
BACKUP_DIR="data/backups"
DATE=$(date +%Y%m%d_%H%M%S)
MAX_BACKUPS=30
COMPRESS_BACKUPS=true

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR" || {
    log_error "Failed to create backup directory: $BACKUP_DIR"
    exit 1
}

log_info "Starting enhanced backup process"

# 1. Database backup with integrity check
log_info "Backing up database..."
if [ -f "data/canary_protocol.db" ]; then
    # Create database backup
    sqlite3 data/canary_protocol.db ".backup $BACKUP_DIR/canary_protocol_$DATE.db"
    
    # Verify backup integrity
    if sqlite3 "$BACKUP_DIR/canary_protocol_$DATE.db" "PRAGMA integrity_check;" | grep -q "ok"; then
        log_info "Database backup verified successfully"
    else
        log_error "Database backup integrity check failed"
        exit 1
    fi
else
    log_warning "Database file not found, skipping database backup"
fi

# 2. Configuration backup
log_info "Backing up configuration..."
if [ -d "config" ]; then
    tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" config/ --exclude="config/.env" --exclude="config/subscribers.txt" 2>/dev/null || true
fi

# 3. Log backup (compressed)
log_info "Backing up logs..."
if [ -d "logs" ] && [ "$(ls -A logs/)" ]; then
    tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" logs/ 2>/dev/null || true
fi

# 4. Migration files backup
log_info "Backing up migration files..."
if [ -d "migrations" ] && [ "$(ls -A migrations/)" ]; then
    tar -czf "$BACKUP_DIR/migrations_$DATE.tar.gz" migrations/ 2>/dev/null || true
fi

# 5. Create comprehensive backup manifest
log_info "Creating backup manifest..."
python3 -c "
import sys
import os
import json
from datetime import datetime
from pathlib import Path

sys.path.append('core')

# Create backup manifest
manifest = {
    'backup_date': '$DATE',
    'backup_timestamp': datetime.now().isoformat(),
    'backup_type': 'full',
    'files': {},
    'system_info': {}
}

# Add file information
backup_dir = Path('$BACKUP_DIR')
for backup_file in backup_dir.glob('*$DATE*'):
    if backup_file.is_file():
        manifest['files'][backup_file.name] = {
            'size_bytes': backup_file.stat().st_size,
            'type': backup_file.suffix
        }

# Add system information
try:
    from adaptive_intelligence import CanaryIntelligence
    from smart_feedback import FeedbackSystem
    
    if os.path.exists('data/canary_protocol.db'):
        intelligence = CanaryIntelligence('data/canary_protocol.db')
        feedback = FeedbackSystem('data/canary_protocol.db')
        
        manifest['system_info'] = {
            'intelligence_patterns': len(intelligence.learning_patterns) if hasattr(intelligence, 'learning_patterns') else 0,
            'feedback_entries': 'available',
            'database_size_mb': round(os.path.getsize('data/canary_protocol.db') / (1024*1024), 2)
        }
except Exception as e:
    manifest['system_info']['error'] = str(e)

# Save manifest
with open('$BACKUP_DIR/backup_manifest_$DATE.json', 'w') as f:
    json.dump(manifest, f, indent=2)

print('Backup manifest created')
"

# 6. Run backup verification
log_info "Verifying backup integrity..."
if [ -f "$BACKUP_DIR/canary_protocol_$DATE.db" ]; then
    python3 core/backup_verification.py --integrity-only "$BACKUP_DIR/canary_protocol_$DATE.db" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_info "Backup verification passed"
    else
        log_warning "Backup verification had issues - check manually"
    fi
fi

# 7. Cleanup old backups
log_info "Cleaning up old backups (keeping last $MAX_BACKUPS)..."
find "$BACKUP_DIR" -name "canary_protocol_*.db" -type f | sort -r | tail -n +$((MAX_BACKUPS + 1)) | xargs rm -f 2>/dev/null || true
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "*.json" -mtime +90 -delete 2>/dev/null || true

# 8. Calculate backup statistics
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/canary_protocol_*.db 2>/dev/null | wc -l)

log_info "✅ Enhanced backup completed successfully"
log_info "📊 Backup Statistics:"
log_info "   - Backup directory: $BACKUP_DIR"
log_info "   - Total size: $BACKUP_SIZE"
log_info "   - Database backups: $BACKUP_COUNT"
log_info "   - Latest backup: canary_protocol_$DATE.db"
