"""Tests for the local, dependency-free achievement progress checker."""

import unittest

from tools.achievement_status import ACHIEVEMENTS, TrackerError, get_report, parse_tracker


def make_roadmap(statuses=None):
    if statuses is None:
        statuses = {name: "⬜ În așteptare" for name in ACHIEVEMENTS}
    rows = "\n".join(f"| **{name}** | {state} | — |" for name, state in statuses.items())
    return (
        "# Roadmap\n\n"
        "## 🏆 Colecția: 2 / 7 deblocate\n\n"
        "| Achievement | Status | Notes |\n"
        "| --- | --- | --- |\n"
        f"{rows}\n\n"
        "## 🥇 Tier-uri superioare\n\n"
        "| Pull Shark | 2 | 16 | 128 | 1024 |\n"
    )


class ProgressCheckerTests(unittest.TestCase):
    def test_reports_all_seven_with_two_unlocked(self):
        values = {name: "⬜ În așteptare" for name in ACHIEVEMENTS}
        values["Pull Shark"] = "✅ Obținut"
        values["Quickdraw"] = "✅ Obținut"
        report = get_report(make_roadmap(values))

        self.assertEqual(report["total"], 7)
        self.assertEqual(report["unlocked"], 2)
        self.assertEqual(report["remaining"], 5)
        self.assertEqual(report["achievements"][0]["status"], "unlocked")
        self.assertEqual(report["achievements"][-1]["status"], "remaining")

    def test_ignores_tier_table(self):
        statuses = parse_tracker(make_roadmap())
        self.assertEqual(len(statuses), 7)

    def test_rejects_missing_achievement(self):
        values = {name: "⬜" for name in ACHIEVEMENTS if name != "YOLO"}
        with self.assertRaisesRegex(TrackerError, "Missing achievements.*YOLO"):
            parse_tracker(make_roadmap(values))

    def test_rejects_duplicate_achievement(self):
        content = make_roadmap().replace(
            "## 🥇 Tier-uri superioare",
            "| **Pull Shark** | ⬜ | duplicate |\n\n## 🥇 Tier-uri superioare",
        )
        with self.assertRaisesRegex(TrackerError, "Duplicate achievement"):
            parse_tracker(content)

    def test_rejects_ambiguous_status(self):
        values = {name: "⬜" for name in ACHIEVEMENTS}
        values["YOLO"] = "✅ ⬜"
        with self.assertRaisesRegex(TrackerError, "Unrecognized status for YOLO"):
            parse_tracker(make_roadmap(values))

    
    def test_pending_is_not_unlocked(self):
        values = {name: "⬜ În așteptare" for name in ACHIEVEMENTS}

        values["Pull Shark"] = "✅ Obținut"
        values["YOLO"] = "⬜ PENDING"

        report = get_report(make_roadmap(values))

        self.assertEqual(report["unlocked"], 1)
        self.assertEqual(report["pending"], 1)
        self.assertEqual(report["remaining"], 5)

        statuses = {
            item["name"]: item["status"]
            for item in report["achievements"]
        }

        self.assertEqual(statuses["YOLO"], "pending")

    
    def test_pending_case_insensitive(self):
        values = {name: "⬜ În așteptare" for name in ACHIEVEMENTS}

        values["Galaxy Brain"] = "⬜ pending"

        report = get_report(make_roadmap(values))

        self.assertEqual(report["pending"], 1)
        self.assertEqual(report["unlocked"], 0)
        self.assertEqual(report["remaining"], 6)


if __name__ == "__main__":
    unittest.main()
 