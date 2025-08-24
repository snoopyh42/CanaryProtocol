#!/bin/bash
# Canary Protocol - Cron Job Reset Utility
# Safely removes and reinstalls all Canary Protocol cron jobs

# Source common functions
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/common.sh"

# Set up error handling
set -e
trap 'cleanup_temp_files' EXIT

# Cleanup function for temporary files
cleanup_temp_files() {
    rm -f temp_cron temp_cron_1 temp_cron_2 temp_cron_clean temp_cron_final
}

# Main execution
main() {
    echo -e "${BLUE}🔄 CANARY PROTOCOL CRON RESET${NC}"
    echo "============================="
    echo ""
    
    init_environment
    
    # Backup current crontab
    log_info "Backing up current crontab"
    local backup_file
    backup_file="cron_backup_$(date +%Y%m%d_%H%M%S).txt"
    crontab -l > "$backup_file" 2>/dev/null || touch "$backup_file"
    log_debug "Crontab backed up to $backup_file"
    
    # Get current crontab
    crontab -l > temp_cron 2>/dev/null || touch temp_cron
    
    # Count existing entries
    local daily_count
    local weekly_count
    local comment_count
    daily_count=$(grep -c "daily_silent_collector.py" temp_cron 2>/dev/null || echo "0")
    weekly_count=$(grep -c "canary_protocol.py" temp_cron 2>/dev/null || echo "0")
    comment_count=$(grep -c "# Canary Protocol" temp_cron 2>/dev/null || echo "0")
    
    # Ensure counts are single integers
    daily_count=$(echo "$daily_count" | head -n1 | tr -d '\n')
    weekly_count=$(echo "$weekly_count" | head -n1 | tr -d '\n')
    comment_count=$(echo "$comment_count" | head -n1 | tr -d '\n')
    
    log_info "Found existing entries:"
    echo "   • Daily collection jobs: $daily_count"
    echo "   • Weekly digest jobs: $weekly_count"
    echo "   • Comment lines: $comment_count"
    
    if [[ "$daily_count" -eq 0 && "$weekly_count" -eq 0 && "$comment_count" -eq 0 ]]; then
        log_info "No Canary Protocol cron jobs found - nothing to clean"
    else
        log_info "Cleaning existing entries"
        
        # Remove all Canary Protocol related entries
        grep -v "Canary Protocol" temp_cron > temp_cron_1 2>/dev/null || touch temp_cron_1
        grep -v "daily_silent_collector.py" temp_cron_1 > temp_cron_2 2>/dev/null || touch temp_cron_2
        grep -v "canary_protocol.py" temp_cron_2 > temp_cron_clean 2>/dev/null || touch temp_cron_clean
        
        # Install cleaned crontab
        crontab temp_cron_clean
        log_info "Removed all existing Canary Protocol cron jobs"
    fi
    
    log_info "Installing fresh cron jobs"
    
    # Get the cleaned crontab
    crontab -l > temp_cron_final 2>/dev/null || touch temp_cron_final
    
    # Add the two cron jobs with dynamic paths
    {
        echo "# Canary Protocol - Daily Silent Data Collection"
        echo "0 8 * * * cd $CANARY_ROOT && python3 core/classes/daily_silent_collector.py >> logs/canary_cron.log 2>&1"
        echo ""
        echo "# Canary Protocol - Weekly Intelligent Digest"
        echo "0 9 * * 1 cd $CANARY_ROOT && python3 core/canary_protocol.py >> logs/canary_cron.log 2>&1"
    } >> temp_cron_final
    
    # Install the final crontab
    if crontab temp_cron_final; then
        log_info "Fresh cron jobs installed successfully"
        echo "   • Daily collection: 8 AM every day"
        echo "   • Weekly digest: 9 AM every Monday"
    else
        log_error "Failed to install cron jobs"
        exit 1
    fi
    
    echo ""
    log_info "Current cron status:"
    crontab -l | grep -A1 "Canary Protocol" || log_warn "No Canary Protocol jobs found in crontab"
    
    echo ""
    echo -e "${GREEN}🔄 Cron reset completed successfully!${NC}"
}

# Run main function
main "$@"
