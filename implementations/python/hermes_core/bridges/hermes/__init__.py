"""
Hermes v1.0 — Hermes Agent Bridge
Ch3 §3.2 bridges/ — Platform adapter for Hermes Agent
"""

# This bridge adapts the Hermes Reference Implementation
# to work within the Hermes Agent environment.
# 
# Responsibilities:
#   - Map Hermes Memory tool to file-based state
#   - Translate Cron tool to scheduler/jobs.json
#   - Provide SSH executor for remote commands
