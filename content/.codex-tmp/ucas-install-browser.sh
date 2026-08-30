#!/bin/bash
set -euo pipefail

output=/home/conrad/workspace/ucas-browser-install.log
hotspot='netplan-wlan0-XYH 0563'

exec >"$output" 2>&1

restore_hotspot() {
    nmcli connection up "$hotspot" || true
}
trap restore_hotspot EXIT

echo "=== started ==="
date --iso-8601=seconds
nmcli connection up UCAS
sleep 8

echo "=== IPv6 checks ==="
curl -6 --fail --silent --show-error --location --max-time 20 \
    --output /dev/null https://deb.debian.org/
curl -6 --fail --silent --show-error --location --max-time 20 \
    --output /dev/null https://archive.raspberrypi.com/

echo "=== apt update ==="
apt-get -o Acquire::ForceIPv6=true update

echo "=== install browser ==="
DEBIAN_FRONTEND=noninteractive apt-get \
    -o Acquire::ForceIPv6=true \
    --no-install-recommends \
    --yes install \
    chromium chromium-sandbox chromium-l10n fonts-liberation matchbox-keyboard

echo "=== versions ==="
chromium --version
matchbox-keyboard --help >/dev/null 2>&1 || true
echo "=== finished ==="
date --iso-8601=seconds
