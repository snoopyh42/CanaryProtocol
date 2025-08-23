#!/bin/bash
# Weekly Intelligent Digest with Learning

# Source common functions
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/common.sh"

# Set up error handling
set -e
trap 'cleanup "weekly_digest"' EXIT

# Main execution
main() {
    log_info "Starting weekly intelligent digest"
    
    # Check if already running
    if ! create_lock "weekly_digest"; then
        log_error "Weekly digest already running, exiting"
        exit 1
    fi
    
    # Setup environment
    if ! setup_python_env; then
        log_error "Failed to setup Python environment"
        exit 1
    fi
    
    # Check required modules
    if ! check_python_modules "openai" "feedparser" "requests" "sqlite3" "markdown2"; then
        log_error "Missing required Python modules"
        exit 1
    fi
    
    # Show weekly data summary
    log_info "Generating weekly data summary"
    if run_python_script "$CANARY_CORE/daily_silent_collector.py" --summary >> "$CANARY_LOGS/canary_cron.log" 2>&1; then
        log_debug "Weekly summary generated successfully"
    else
        log_warn "Weekly summary generation failed, continuing with digest"
    fi
    
    # Run the full intelligent analysis
    log_info "Running intelligent analysis and digest"
    if run_python_script "$CANARY_CORE/canary_protocol.py" >> "$CANARY_LOGS/canary_cron.log" 2>&1; then
        log_info "Weekly digest completed successfully"
    else
        log_error "Weekly digest failed"
        exit 1
    fi
    
    log_info "Weekly intelligent digest process completed"
}

# Run main function
main "$@"
