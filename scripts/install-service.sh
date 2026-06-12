#!/usr/bin/env bash
# ALCHEMY - Service Installation Script
#
# Installs the processing daemon as either a cron job or systemd service.
#
# Usage:
#   # Install as cron job (recommended for CPU-constrained machines)
#   sudo bash scripts/install-service.sh --cron
#
#   # Install as systemd service (long-running daemon)
#   sudo bash scripts/install-service.sh --systemd
#
#   # Remove installed service
#   bash scripts/install-service.sh --remove

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DAEMON_SCRIPT="$SCRIPT_DIR/process-daemon.py"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python3"
SERVICE_NAME="alchemy-pipeline"
CRON_SCHEDULE="*/30 * * * *"  # Every 30 minutes

log()  { echo "[$(date '+%H:%M:%S')] $*"; }
err()  { log "ERROR: $*" >&2; }

install_cron() {
    log "Installing cron job..."

    CRON_JOB="$CRON_SCHEDULE cd $PROJECT_DIR && $VENV_PYTHON $DAEMON_SCRIPT --oneshot >> $PROJECT_DIR/logs/cron.log 2>&1"

    # Check if already installed
    if crontab -l 2>/dev/null | grep -q "$DAEMON_SCRIPT"; then
        log "Cron job already exists. Updating..."
    fi

    # Add to crontab (replace any existing alchemy entry)
    (crontab -l 2>/dev/null | grep -v "$DAEMON_SCRIPT"; echo "$CRON_JOB") | crontab -

    log "Cron job installed: $CRON_SCHEDULE"
    log "Logs: $PROJECT_DIR/logs/cron.log"
}

install_systemd() {
    log "Installing systemd service..."

    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=ALCHEMY Pipeline Processing Daemon
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_PYTHON $DAEMON_SCRIPT --watch
Restart=on-failure
RestartSec=10
StandardOutput=append:$PROJECT_DIR/logs/daemon.log
StandardError=append:$PROJECT_DIR/logs/daemon.error.log

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl start "$SERVICE_NAME"

    log "systemd service installed and started: $SERVICE_NAME"
    log "Status: sudo systemctl status $SERVICE_NAME"
}

remove_service() {
    log "Removing installed service..."

    # Remove systemd service if exists
    if systemctl list-units --full -all 2>/dev/null | grep -q "$SERVICE_NAME"; then
        sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
        sudo systemctl disable "$SERVICE_NAME" 2>/dev/null || true
        sudo rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
        sudo systemctl daemon-reload
        log "Systemd service removed."
    fi

    # Remove cron job
    if crontab -l 2>/dev/null | grep -q "$DAEMON_SCRIPT"; then
        (crontab -l 2>/dev/null | grep -v "$DAEMON_SCRIPT") | crontab -
        log "Cron job removed."
    fi

    log "Service removal complete."
}

# --- Main ---

if [ ! -f "$DAEMON_SCRIPT" ]; then
    err "Daemon script not found at $DAEMON_SCRIPT"
    exit 1
fi

case "${1:-}" in
    --cron)
        install_cron
        ;;
    --systemd)
        install_systemd
        ;;
    --remove)
        remove_service
        ;;
    *)
        echo "Usage: $0 [--cron | --systemd | --remove]"
        echo ""
        echo "Options:"
        echo "  --cron      Install as cron job (recommended for CPU-constrained)"
        echo "  --systemd   Install as systemd service (long-running daemon)"
        echo "  --remove    Remove installed service"
        exit 1
        ;;
esac
