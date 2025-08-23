#!/bin/bash

# Canary Protocol - Cron Job Reset Utility
# Safely removes and reinstalls all Canary Protocol cron jobs

echo "🔄 CANARY PROTOCOL CRON RESET"
echo "============================="
echo ""

# Backup current crontab
echo "💾 Backing up current crontab..."
crontab -l > cron_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || touch cron_backup_$(date +%Y%m%d_%H%M%S).txt

# Get current crontab
crontab -l > temp_cron 2>/dev/null || touch temp_cron

# Count existing entries
DAILY_COUNT=$(grep -c "run_daily_collection.sh" temp_cron 2>/dev/null || echo "0")
WEEKLY_COUNT=$(grep -c "run_weekly_intelligent_digest.sh" temp_cron 2>/dev/null || echo "0")
COMMENT_COUNT=$(grep -c "Canary Protocol" temp_cron 2>/dev/null || echo "0")

echo "📊 Found existing entries:"
echo "   • Daily collection jobs: $DAILY_COUNT"
echo "   • Weekly digest jobs: $WEEKLY_COUNT"
echo "   • Comment lines: $COMMENT_COUNT"

if [ "$DAILY_COUNT" -eq 0 ] && [ "$WEEKLY_COUNT" -eq 0 ] && [ "$COMMENT_COUNT" -eq 0 ]; then
    echo "✅ No Canary Protocol cron jobs found - nothing to clean"
else
    echo ""
    echo "🧹 Cleaning existing entries..."
    
    # Remove all Canary Protocol related entries
    grep -v "Canary Protocol" temp_cron > temp_cron_1 2>/dev/null || touch temp_cron_1
    grep -v "run_daily_collection.sh" temp_cron_1 > temp_cron_2 2>/dev/null || touch temp_cron_2
    grep -v "run_weekly_intelligent_digest.sh" temp_cron_2 > temp_cron_clean 2>/dev/null || touch temp_cron_clean
    
    # Install cleaned crontab
    crontab temp_cron_clean
    
    echo "✅ Removed all existing Canary Protocol cron jobs"
fi

echo ""
echo "🔧 Installing fresh cron jobs..."

# Get the cleaned crontab
crontab -l > temp_cron_final 2>/dev/null || touch temp_cron_final

# Add the two cron jobs
echo "# Canary Protocol - Daily Silent Data Collection" >> temp_cron_final
echo "0 8 * * * /home/ahansen/CanaryProtocol/scripts/run_daily_collection.sh" >> temp_cron_final
echo "# Canary Protocol - Weekly Intelligent Digest" >> temp_cron_final
echo "0 9 * * 0 /home/ahansen/CanaryProtocol/scripts/run_weekly_intelligent_digest.sh" >> temp_cron_final

# Install the final crontab
crontab temp_cron_final

# Cleanup temp files
rm -f temp_cron temp_cron_1 temp_cron_2 temp_cron_clean temp_cron_final

echo "✅ Fresh cron jobs installed:"
echo "   • Daily collection: 8 AM every day"
echo "   • Weekly digest: 9 AM every Sunday"

echo ""
echo "📋 Current cron status:"
crontab -l | grep -A1 "Canary Protocol"

echo ""
echo "🔄 Cron reset completed successfully!"
