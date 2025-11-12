#!/bin/bash
# system_check.sh - Collect and save basic system information
# --- CONFIG  ---
LOG_DIR="$HOME/system_logs"
LOG_FILE="$LOG_DIR/system_check_$(date +%Y%m%d_%H%M%S).log"
# --- SETUP ---
mkdir -p "$LOG_DIR"
# --- GATHER INFO ---
{
  echo "==== System Check ===="
  echo "Date: $(date)"
  echo "Hostname: $(hostname)"
  echo "Uptime: $(uptime -p)"
  echo "-----------------------------"
  echo "Logged-in users:"
  who
  echo "-----------------------------"
  echo "Disk usage:"
  df -h | grep '^/dev/'
  echo "-----------------------------"
  echo "Memory usage:"
  free -h
  echo "-----------------------------"
  echo "IP addresses:"
  ip -4 addr show | grep inet
  echo "============================="
} > "$LOG_FILE"
echo "System info saved to: $LOG_FILE"

