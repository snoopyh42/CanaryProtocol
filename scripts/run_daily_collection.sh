#!/bin/bash
# Daily Silent Data Collection for Canary Protocol

# Source common functions
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/common.sh"

# Set up error handling
set -e
trap 'cleanup "daily_collection"' EXIT

# Main execution
main() {
    log_info "Starting daily data collection"
    
    # Check if already running
    if ! create_lock "daily_collection"; then
        log_error "Daily collection already running, exiting"
        exit 1
    fi
    
    # Setup environment
    if ! setup_python_env; then
        log_error "Failed to setup Python environment"
        exit 1
    fi
    
    # Check required modules
    if ! check_python_modules "feedparser" "requests" "sqlite3"; then
        log_error "Missing required Python modules"
        exit 1
    fi
    
    # Run the collector
    log_info "Running daily silent collector"
    if run_python_script "$CANARY_CORE/daily_silent_collector.py" >> "$CANARY_LOGS/daily_collection.log" 2>&1; then
        log_info "Daily collection completed successfully"
    else
        log_error "Daily collection failed"
        exit 1
    fi
    
    # Check for emergency triggers
    log_debug "Checking for emergency triggers"
    if python3 "$CANARY_CORE/daily_silent_collector.py" --check-emergency | grep -q "EMERGENCY"; then
        log_warn "Emergency trigger detected"
        # Optional: Send emergency notification
        # run_python_script "$CANARY_CORE/canary_protocol.py" --emergency >> "$CANARY_LOGS/daily_collection.log" 2>&1
    fi
    
    log_info "Daily collection process completed"
}

# Run main function
main "$@"
