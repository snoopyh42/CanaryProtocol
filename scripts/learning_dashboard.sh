#!/bin/bash
# Learning Progress Dashboard

# Source common functions
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/common.sh"

# Main execution
main() {
    echo -e "${BLUE}🧠 CANARY PROTOCOL LEARNING DASHBOARD${NC}"
    echo "====================================="
    echo ""
    
    # Setup environment
    if ! setup_python_env; then
        log_error "Failed to setup Python environment"
        exit 1
    fi
    
    # Daily collection summary
    echo -e "${GREEN}📊 RECENT DATA COLLECTION:${NC}"
    if run_python_script "$CANARY_CORE/daily_silent_collector.py" --summary; then
        log_debug "Data collection summary displayed"
    else
        log_warn "Failed to get data collection summary"
    fi
    echo ""
    
    # Learning intelligence
    echo -e "${GREEN}🎯 ADAPTIVE INTELLIGENCE:${NC}"
    if run_python_script "$CANARY_CORE/adaptive_intelligence.py"; then
        log_debug "Adaptive intelligence status displayed"
    else
        log_warn "Failed to get adaptive intelligence status"
    fi
    echo ""
    
    # User feedback summary
    echo -e "${GREEN}📝 USER FEEDBACK:${NC}"
    if run_python_script "$CANARY_CORE/smart_feedback.py" --summary; then
        log_debug "User feedback summary displayed"
    else
        log_warn "Failed to get user feedback summary"
    fi
    echo ""
    
    # Recent emergency triggers
    echo -e "${GREEN}🚨 EMERGENCY TRIGGERS:${NC}"
    if run_python_script "$CANARY_CORE/daily_silent_collector.py" --check-emergency; then
        log_debug "Emergency triggers checked"
    else
        log_warn "Failed to check emergency triggers"
    fi
    echo ""
    
    # Recent logs
    echo -e "${GREEN}📋 RECENT ACTIVITY:${NC}"
    echo "Daily Collection (last 5 entries):"
    if [[ -f "$CANARY_LOGS/daily_collection.log" ]]; then
        tail -n 5 "$CANARY_LOGS/daily_collection.log"
    else
        echo "No daily collection log found"
    fi
    echo ""
    echo "Weekly Digest (last 5 entries):"
    if [[ -f "$CANARY_LOGS/canary_cron.log" ]]; then
        tail -n 5 "$CANARY_LOGS/canary_cron.log"
    else
        echo "No weekly digest log found"
    fi
    
    echo ""
    echo -e "${GREEN}✅ Dashboard display completed${NC}"
}

# Run main function
main "$@"
