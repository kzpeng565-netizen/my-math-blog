#!/bin/bash
set -u

output=/home/conrad/workspace/ucas-portal-capture.txt
html=/home/conrad/workspace/ucas-portal.html
assets=/home/conrad/workspace/ucas-portal-assets
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

echo "=== portal headers ==="
curl --silent --show-error --location --max-time 25 \
    --dump-header - \
    --output "$html" \
    --write-out '\nfinal_url=%{url_effective}\nhttp_code=%{http_code}\nredirects=%{num_redirects}\n' \
    https://portal.ucas.ac.cn/index_11.html || true

echo "=== portal assets ==="
mkdir -p "$assets"
for path in \
    static/themes/pro/lib/all.min.js \
    static/themes/pro/lib/patch/patch.es6.js \
    static/themes/pro/js/creater.js \
    static/themes/pro/js/lang.js \
    static/themes/pro/js/Utils.js \
    static/themes/pro/js/Portal.js \
    static/themes/pro/js/main.js
do
    name="${path##*/}"
    curl --silent --show-error --location --max-time 20 \
        --output "$assets/$name" "https://portal.ucas.ac.cn/$path" || true
    wc -c "$assets/$name" 2>/dev/null || true
done

echo "=== ipv6 internet ==="
curl -6 --silent --show-error --location --max-time 15 \
    --output /dev/null \
    --write-out 'final_url=%{url_effective} http_code=%{http_code}\n' \
    https://deb.debian.org/ || true

echo "=== finished ==="
date --iso-8601=seconds
