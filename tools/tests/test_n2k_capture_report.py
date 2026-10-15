# Copyright © 2026 Isto Hunttila
import unittest
from tools.n2k_capture_report import decode_id

class TestCanIdentifier(unittest.TestCase):
    def test_heading_broadcast(self):
        # 0x09F112xx -> PGN 127250 (vessel heading)
        priority, pgn, src, dst = decode_id(0x09F11223)
        self.assertEqual((priority, pgn, src, dst), (2, 127250, 35, 255))

    def test_iso_request_destination(self):
        priority, pgn, src, dst = decode_id(0x18EA2223)
        self.assertEqual((priority, pgn, src, dst), (6, 59904, 35, 34))

if __name__ == "__main__":
    unittest.main()
