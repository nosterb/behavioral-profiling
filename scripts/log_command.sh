#!/bin/bash
#
# Command Logger for Claude Code Sessions
#
# This script logs all commands executed during Claude Code sessions
# to maintain a persistent record across sessions.
#
# Usage: Automatically triggered by Claude Code hooks
#        Or manually: ./scripts/log_command.sh "command description" "full command"

LOG_DIR="${AWARENESS_PROJECT_ROOT:-$(dirname "$0")/..}/logs/command_history"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DATE=$(date '+%Y-%m-%d')
SESSION_ID="${CLAUDE_SESSION_ID:-unknown}"

# Create daily log file
DAILY_LOG="$LOG_DIR/commands_${DATE}.log"
FULL_LOG="$LOG_DIR/commands_all.log"

# Get command info
DESCRIPTION="${1:-No description}"
COMMAND="${2:-$BASH_COMMAND}"
PWD_PATH=$(pwd)

# Log entry format
LOG_ENTRY="[$TIMESTAMP] [SESSION:$SESSION_ID] [PWD:$PWD_PATH]
  DESC: $DESCRIPTION
  CMD:  $COMMAND
"

# Append to both daily and full logs
echo "$LOG_ENTRY" >> "$DAILY_LOG"
echo "$LOG_ENTRY" >> "$FULL_LOG"

# Also create a JSON log for structured parsing
JSON_LOG="$LOG_DIR/commands_${DATE}.json"
if [ ! -f "$JSON_LOG" ]; then
    echo "[" > "$JSON_LOG"
else
    # Remove trailing ] to append
    sed -i '' -e '$ d' "$JSON_LOG"
    echo "," >> "$JSON_LOG"
fi

cat >> "$JSON_LOG" <<EOF
  {
    "timestamp": "$TIMESTAMP",
    "session_id": "$SESSION_ID",
    "pwd": "$PWD_PATH",
    "description": "$DESCRIPTION",
    "command": "$COMMAND"
  }
]
EOF

# Keep only last 90 days of logs
find "$LOG_DIR" -name "commands_*.log" -mtime +90 -delete
find "$LOG_DIR" -name "commands_*.json" -mtime +90 -delete
