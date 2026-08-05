from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


def request(url: str, api_key: str, method: str = "GET", value=None):
    data = None
    headers = {"X-API-Key": api_key}
    if value is not None:
        data = json.dumps(value).encode("utf-8")
        headers["Content-Type"] = "application/json"
    with urllib.request.urlopen(
        urllib.request.Request(url, data=data, headers=headers, method=method),
        timeout=20,
    ) as response:
        body = response.read()
    return json.loads(body) if body else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--folder-id", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--type", choices=("sendonly", "receiveonly"), required=True)
    parser.add_argument("--device", required=True)
    args = parser.parse_args()
    root = ET.parse(args.config).getroot()
    api_key = root.findtext("./gui/apikey")
    address = root.findtext("./gui/address", "127.0.0.1:8384")
    if address.startswith("0.0.0.0"):
        address = "127.0.0.1" + address[len("0.0.0.0") :]
    base = f"http://{address}/rest/config"
    try:
        folder = request(f"{base}/folders/{args.folder_id}", api_key)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        folder = request(f"{base}/defaults/folder", api_key)
    folder.update(
        {
            "id": args.folder_id,
            "label": args.label,
            "path": args.path,
            "type": args.type,
            "devices": [{"deviceID": args.device, "introducedBy": ""}],
        }
    )
    request(f"{base}/folders/{args.folder_id}", api_key, "PUT", folder)
    verified = request(f"{base}/folders/{args.folder_id}", api_key)
    print(
        json.dumps(
            {
                "id": verified["id"],
                "label": verified["label"],
                "path": verified["path"],
                "type": verified["type"],
                "devices": [item["deviceID"] for item in verified["devices"]],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
