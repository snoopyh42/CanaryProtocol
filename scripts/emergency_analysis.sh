#!/bin/bash
# Emergency Analysis Trigger

echo "🚨 EMERGENCY ANALYSIS MODE"
echo "========================="

# Get current directory (should be CanaryProtocol root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Show recent emergency triggers
echo "Recent emergency triggers:"
./canary collect --check-emergency

echo ""
echo "Running immediate analysis..."

# Run immediate analysis with verbose flag (emergency flag not supported)
./canary run --verbose

echo ""
echo "Emergency analysis completed."
