#!/usr/bin/env bash
set -e
: "${APP_PASSWORD:=changeme}"
: "${DOWNLOAD_DIR:=/data/downloads}"
mkdir -p "$DOWNLOAD_DIR"
exec gunicorn -w 2 -b 0.0.0.0:${PORT:-5000} app:app
