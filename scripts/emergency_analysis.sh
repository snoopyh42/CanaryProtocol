#!/bin/bash
# Emergency Analysis Trigger

# Source common functions
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/common.sh"

# Set up error handling
set -e
trap 'cleanup "emergency_analysis"' EXIT

# Main execution
main() {
    echo -e "${RED}🚨 EMERGENCY ANALYSIS MODE${NC}"
    echo "========================="
    
    log_info "Starting emergency analysis"
    
    # Check if already running
    if ! create_lock "emergency_analysis"; then
        log_error "Emergency analysis already running, exiting"
        exit 1
    fi
    
    # Setup environment
    if ! setup_python_env; then
        log_error "Failed to setup Python environment"
        exit 1
    fi
    
    # Check required modules
    if ! check_python_modules "openai" "feedparser" "requests" "sqlite3"; then
        log_error "Missing required Python modules"
        exit 1
    fi
    
    # Show recent emergency triggers
    echo ""
    log_info "Checking recent emergency triggers"
    if run_python_script "$CANARY_CORE/daily_silent_collector.py" --check-emergency; then
        log_debug "Emergency trigger check completed"
    else
        log_warn "Emergency trigger check failed, continuing with analysis"
    fi
    
    echo ""
    log_info "Running immediate emergency analysis"
    
    # Run immediate analysis with emergency flag
    if run_python_script "$CANARY_CORE/canary_protocol.py" --emergency --verbose; then
        log_info "Emergency analysis completed successfully"
    else
        log_error "Emergency analysis failed"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ Emergency analysis completed${NC}"
}

# Run main function
main "$@"
