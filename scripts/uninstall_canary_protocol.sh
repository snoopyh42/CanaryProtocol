#!/bin/bash
# Uninstall Smart Canary Protocol
# Removes cron jobs, optionally removes data and configurations

# Source common functions
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/common.sh"

# Set up error handling
set -e
trap 'cleanup "uninstall_canary_protocol"' EXIT

# Main execution
main() {
    echo -e "${RED}🗑️  SMART CANARY PROTOCOL UNINSTALL${NC}"
    echo "======================================"
    echo ""
    
    log_info "Starting Smart Canary Protocol uninstall process"
    
    # Check if already running
    if ! create_lock "uninstall_canary_protocol"; then
        log_error "Uninstall process already running, exiting"
        exit 1
    fi
    
    # Setup environment
    if ! setup_python_env; then
        log_error "Failed to setup Python environment"
        exit 1
    fi
    
    echo "⚠️  This will remove Smart Canary Protocol components from your system."
    echo ""
    echo "What would you like to remove?"
    echo ""
    echo "1) Remove cron jobs only (keep data and configs)"
    echo "2) Remove cron jobs and system files (keep user data)"
    echo "3) Complete removal (including all data and configs)"
    echo "4) Cancel uninstall"
    echo ""
    
    read -r -p "Enter choice (1-4): " choice
    
    case $choice in
        1)
            uninstall_cron_jobs
            ;;
        2)
            uninstall_cron_jobs
            uninstall_system_files
            ;;
        3)
            uninstall_cron_jobs
            uninstall_system_files
            uninstall_user_data
            ;;
        4)
            echo "❌ Uninstall cancelled"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice"
            exit 1
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}✅ Smart Canary Protocol uninstall completed${NC}"
}

uninstall_cron_jobs() {
    echo ""
    log_info "Removing cron jobs..."
    
    # Get current crontab
    crontab -l > temp_cron 2>/dev/null || touch temp_cron
    
    # Count existing entries
    daily_count=$(grep -c "daily_silent_collector.py" temp_cron 2>/dev/null || echo "0")
    weekly_count=$(grep -c "canary_protocol.py" temp_cron 2>/dev/null || echo "0")
    comment_count=$(grep -c "# Canary Protocol" temp_cron 2>/dev/null || echo "0")
    
    if [[ "$daily_count" -eq 0 && "$weekly_count" -eq 0 && "$comment_count" -eq 0 ]]; then
        log_info "No Canary Protocol cron jobs found"
    else
        # Remove all Canary Protocol related entries
        grep -v "Canary Protocol" temp_cron > temp_cron_1 2>/dev/null || touch temp_cron_1
        grep -v "daily_silent_collector.py" temp_cron_1 > temp_cron_2 2>/dev/null || touch temp_cron_2
        grep -v "canary_protocol.py" temp_cron_2 > temp_cron_clean 2>/dev/null || touch temp_cron_clean
        
        # Install cleaned crontab
        crontab temp_cron_clean
        
        # Clean up temp files
        rm -f temp_cron temp_cron_1 temp_cron_2 temp_cron_clean
        
        log_info "Removed $daily_count daily collection jobs"
        log_info "Removed $weekly_count weekly digest jobs"
        log_info "Removed $comment_count comment lines"
    fi
}

uninstall_system_files() {
    echo ""
    log_info "Removing system files..."
    
    # Remove lock files
    if [[ -d "locks" ]]; then
        rm -rf locks/
        log_info "Removed lock files"
    fi
    
    # Remove migration files
    if [[ -d "migrations" ]]; then
        rm -rf migrations/
        log_info "Removed migration files"
    fi
    
    # Remove generated scripts (keep original source scripts)
    if [[ -f "scripts/run_daily_collection.sh" ]]; then
        rm -f scripts/run_daily_collection.sh
        log_info "Removed generated daily collection script"
    fi
    
    if [[ -f "scripts/run_weekly_intelligent_digest.sh" ]]; then
        rm -f scripts/run_weekly_intelligent_digest.sh
        log_info "Removed generated weekly digest script"
    fi
    
    # Remove cron backup files
    rm -f cron_backup_*.txt
    log_info "Removed cron backup files"
}

uninstall_user_data() {
    echo ""
    log_warning "This will permanently delete all learning data and configurations!"
    read -r -p "Are you absolutely sure? Type 'DELETE' to confirm: " confirm
    
    if [[ "$confirm" != "DELETE" ]]; then
        log_info "User data removal cancelled"
        return
    fi
    
    log_info "Removing user data and configurations..."
    
    # Remove database and data directory
    if [[ -d "data" ]]; then
        rm -rf data/
        log_info "Removed database and data files"
    fi
    
    # Remove backups
    if [[ -d "backups" ]]; then
        rm -rf backups/
        log_info "Removed backup files"
    fi
    
    # Remove logs
    if [[ -d "logs" ]]; then
        rm -rf logs/
        log_info "Removed log files"
    fi
    
    # Remove user configurations (keep examples and defaults)
    if [[ -f "config/config.yaml" ]]; then
        rm -f config/config.yaml
        log_info "Removed user configuration file"
    fi
    
    if [[ -f "config/.env" ]]; then
        rm -f config/.env
        log_info "Removed environment configuration"
    fi
    
    if [[ -f "config/subscribers.txt" ]]; then
        rm -f config/subscribers.txt
        log_info "Removed subscriber list"
    fi
    
    # Remove A/B test reports
    rm -f ab_test_report_*.json
    log_info "Removed A/B test reports"
}

# Run main function
main "$@"
