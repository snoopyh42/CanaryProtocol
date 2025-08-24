#!/bin/bash
# Learning Progress Dashboard

echo "🧠 CANARY PROTOCOL LEARNING DASHBOARD"
echo "====================================="
echo ""

# Get current directory (should be CanaryProtocol root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Daily collection summary
echo "📊 RECENT DATA COLLECTION:"
./canary collect --summary
echo ""

# Learning intelligence
echo "🎯 ADAPTIVE INTELLIGENCE:"
./canary dashboard
echo ""

# User feedback summary
echo "📝 USER FEEDBACK:"
./canary feedback-summary
echo ""

# Recent emergency triggers
echo "🚨 EMERGENCY TRIGGERS:"
./canary collect --check-emergency
echo ""

# Recent logs
echo "📋 RECENT ACTIVITY:"
echo "Daily Collection (last 5 entries):"
tail -n 5 logs/daily_collection.log 2>/dev/null || echo "No daily collection log found"
echo ""
echo "Weekly Digest (last 5 entries):"
tail -n 5 logs/canary_cron.log 2>/dev/null || echo "No weekly digest log found"
