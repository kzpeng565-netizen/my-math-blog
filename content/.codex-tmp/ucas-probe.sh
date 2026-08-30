#!/bin/bash
set -u

output=/home/conrad/workspace/ucas-network-probe.txt
body=/tmp/ucas-captive-body.html
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

echo "=== device ==="
nmcli -f DEVICE,TYPE,STATE,CONNECTION device status
echo "=== address ==="
ip -brief address show wlan0
echo "=== route ==="
ip route
echo "=== dns ==="
nmcli device show wlan0 | grep -E 'IP4.GATEWAY|IP4.DNS'

echo "=== captive request ==="
curl --silent --show-error --max-time 20 \
    --dump-header - \
    --output "$body" \
    --write-out '\nfinal_url=%{url_effective}\nhttp_code=%{http_code}\nredirects=%{num_redirects}\n' \
    http://neverssl.com/ || true

echo "=== body ==="
sed -n '1,240p' "$body" 2>/dev/null || true
echo "=== finished ==="
date --iso-8601=seconds
