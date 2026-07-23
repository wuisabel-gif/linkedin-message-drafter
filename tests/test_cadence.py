import os
import unittest

from linkedin_message_drafter.cadence import deslop


class CadenceTests(unittest.TestCase):
    def test_deslop_returns_none_when_unavailable(self):
        # A bogus deslop path forces the node branch to fail — deslop() must
        # degrade to None (skip the check), never raise or fabricate a score.
        os.environ["CADENCE_DESLOP"] = "/nonexistent/deslop.mjs"
        try:
            self.assertIsNone(deslop("some draft text"))
        finally:
            del os.environ["CADENCE_DESLOP"]


if __name__ == "__main__":
    unittest.main()
