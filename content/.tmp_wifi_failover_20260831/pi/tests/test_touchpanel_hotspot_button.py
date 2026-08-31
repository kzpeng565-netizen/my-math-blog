from __future__ import annotations

import unittest
from pathlib import Path


class TouchPanelHotspotButtonTests(unittest.TestCase):
    def test_button_uses_shared_safe_failover_command(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = (root / "panel.py").read_text(encoding="utf-8")
        self.assertIn("一键恢复热点连接", source)
        self.assertIn("--force-fallback", source)
        self.assertIn("threading.Thread", source)
        self.assertIn("热点连接失败，已尝试恢复 UCAS", source)
        self.assertIn("hotspot_button.configure", source)
        self.assertNotIn(
            '"connection",\n            "up",\n            "netplan-wlan0-XYH 0563"',
            source,
        )


if __name__ == "__main__":
    unittest.main()
