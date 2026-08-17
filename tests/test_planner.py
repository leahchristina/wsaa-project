import sys
import unittest
from pathlib import Path


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER))

import planner


class TestPlanner(unittest.TestCase):

    def test_december_excludes_shutdown_dates(self):
        available_dates = planner.get_available_dates(
            2026,
            12
        )

        date_values = [
            planning_date.isoformat()
            for planning_date in available_dates
        ]

        self.assertNotIn("2026-12-25", date_values)
        self.assertNotIn("2026-12-26", date_values)


if __name__ == "__main__":
    unittest.main()