#!/bin/bash
# Common functions and variables for Canary Protocol scripts

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the absolute path of the Canary Protocol directory
get_canary_root() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    dirname "$script_dir"
}

# Initialize environment variables
init_environment() {
    CANARY_ROOT="$(get_canary_root)"
    export CANARY_ROOT
    export CANARY_CORE="$CANARY_ROOT/core"
    export CANARY_LOGS="$CANARY_ROOT/logs"
    export CANARY_DATA="$CANARY_ROOT/data"
    export CANARY_CONFIG="$CANARY_ROOT/config"
    
    # Create necessary directories
    mkdir -p "$CANARY_LOGS" "$CANARY_DATA"
}

# Initialize environment on script load
init_environment

# Logging functions with color output
log_info() {
    local log_file="${CANARY_ROOT}/logs/script.log"
    mkdir -p "$(dirname "$log_file")"
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S'): $1" | tee -a "$log_file"
}

log_error() {
    local log_file="${CANARY_ROOT}/logs/script.log"
    mkdir -p "$(dirname "$log_file")"
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S'): $1" | tee -a "$log_file" >&2
}

log_warning() {
    local log_file="${CANARY_ROOT}/logs/script.log"
    mkdir -p "$(dirname "$log_file")"
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S'): $1" | tee -a "$log_file"
}

log_warn() {
    log_warning "$@"
}

log_debug() {
    if [[ "${DEBUG:-}" == "true" ]]; then
        local log_file="${CANARY_ROOT}/logs/script.log"
        mkdir -p "$(dirname "$log_file")"
        echo -e "${BLUE}[DEBUG]${NC} $(date '+%Y-%m-%d %H:%M:%S'): $1" | tee -a "$log_file"
    fi
}

# Check if Python 3 is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3.8 or higher."
        return 1
    fi
    
    local python_version
    python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_info "Using Python $python_version"
    return 0
}

# Setup Python environment
setup_python_env() {
    init_environment
    cd "$CANARY_ROOT" || {
        log_error "Cannot navigate to Canary Protocol directory: $CANARY_ROOT"
        return 1
    }
    
    # Check if virtual environment exists and activate it
    if [[ -d ".venv" ]]; then
        log_debug "Activating virtual environment (.venv)"
        # shellcheck source=/dev/null
        source .venv/bin/activate || {
            log_warn "Failed to activate .venv virtual environment, proceeding without it"
        }
    elif [[ -d "venv" ]]; then
        log_debug "Activating virtual environment (venv)"
        # shellcheck source=/dev/null
        source venv/bin/activate || {
            log_warn "Failed to activate venv virtual environment, proceeding without it"
        }
    else
        log_debug "No virtual environment found, using system Python"
    fi
    
    # Add core directory to Python path
    export PYTHONPATH="$CANARY_CORE:${PYTHONPATH:-}"
    
    return 0
}

# Check if required Python modules are available
check_python_modules() {
    local modules=("$@")
    local missing_modules=()
    
    for module in "${modules[@]}"; do
        if ! python3 -c "import $module" &> /dev/null; then
            missing_modules+=("$module")
        fi
    done
    
    if [[ ${#missing_modules[@]} -gt 0 ]]; then
        log_error "Missing required Python modules: ${missing_modules[*]}"
        log_info "Install with: pip3 install ${missing_modules[*]}"
        return 1
    fi
    
    return 0
}

# Run Python script with error handling
run_python_script() {
    local script_path="$1"
    shift
    local args=("$@")
    
    if [[ ! -f "$script_path" ]]; then
        log_error "Python script not found: $script_path"
        return 1
    fi
    
    log_debug "Running: python3 $script_path ${args[*]}"
    python3 "$script_path" "${args[@]}"
    local exit_code=$?
    
    if [[ $exit_code -ne 0 ]]; then
        log_error "Python script failed with exit code $exit_code: $script_path"
        return $exit_code
    fi
    
    return 0
}

# Check if process is already running
check_process_running() {
    local process_name="$1"
    if pgrep -f "$process_name" > /dev/null; then
        log_warn "Process already running: $process_name"
        return 0
    fi
    return 1
}

# Lock file management to prevent concurrent runs
create_lock() {
    local lock_name="$1"
    local lock_file="${CANARY_ROOT}/locks/${lock_name}.lock"
    
    if [[ -f "$lock_file" ]]; then
        local lock_pid
        lock_pid=$(cat "$lock_file")
        if kill -0 "$lock_pid" 2>/dev/null; then
            log_error "Another instance is already running (PID: $lock_pid)"
            return 1
        else
            log_warning "Removing stale lock file"
            rm -f "$lock_file"
        fi
    fi
    
    mkdir -p "$(dirname "$lock_file")"
    echo $$ > "$lock_file"
    return 0
}

remove_lock() {
    local lock_name="$1"
    local lock_file="${CANARY_ROOT}/locks/${lock_name}.lock"
    [[ -f "$lock_file" ]] && rm -f "$lock_file"
}

# Cleanup function to be called on script exit
cleanup() {
    local lock_name="$1"
    if [[ -n "$lock_name" ]]; then
        remove_lock "$lock_name"
    fi
}

# Get configuration value
get_config_value() {
    local key="$1"
    local default_value="$2"
    
    # Try to get value from environment first
    local env_key
    env_key="CANARY_$(echo "$key" | tr '[:lower:]' '[:upper:]' | tr '.' '_')"
    if [[ -n "${!env_key}" ]]; then
        echo "${!env_key}"
        return 0
    fi
    
    # Try to get from Python config if available
    if [[ -f "$CANARY_CORE/config_loader.py" ]]; then
        local value
        value=$(python3 -c "
import sys
sys.path.append('core')
from config_loader import ConfigLoader
config = ConfigLoader()
print(config._config.get('$key', '$default_value'))
")
        echo "$value"
        return 0
    fi
    
    echo "$default_value"
    return 0
}

# Validate email configuration
check_email_config() {
    local gmail_user
    local gmail_password
    gmail_user=$(get_config_value "email.gmail_user" "")
    gmail_password=$(get_config_value "email.gmail_password" "")
    
    if [[ -z "$gmail_user" || -z "$gmail_password" ]]; then
        log_warn "Email configuration incomplete - notifications may not work"
        return 1
    fi
    
    log_debug "Email configuration validated"
    return 0
}
