import tempfile
import unittest
from pathlib import Path

from linkedin_message_drafter.cli import _iter_prospects


class BatchTests(unittest.TestCase):
    def test_bad_item_does_not_abort_batch(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "a.json").write_text('{"name":"A","context":"x","goal":"y"}')
            Path(d, "b.json").write_text('{"name":"B"}')  # missing required fields
            Path(d, "c.csv").write_text("name,context,goal\nC,x,y\nBad,,\n")
            results = list(_iter_prospects([d]))

        ok = [p for _, p, err in results if err is None]
        bad = [(label, err) for label, p, err in results if err]
        self.assertEqual({p.name for p in ok}, {"A", "C"})  # good ones survive
        self.assertEqual(len(bad), 2)                        # b.json + the bad CSV row
        self.assertTrue(any("row 3" in label for label, _ in bad))  # row number reported


if __name__ == "__main__":
    unittest.main()
