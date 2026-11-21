#!/usr/bin/env python3
"""Display the manually recorded GitHub Achievement Lab progress.

This script does not query or grant GitHub achievements. The roadmap is the
single source of truth until its owner confirms new badges on GitHub.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ACHIEVEMENTS = (
    "Pull Shark",
    "Quickdraw",
    "YOLO",
    "Pair Extraordinaire",
    "Galaxy Brain",
    "Starstruck",
    "Public Sponsor",
)
DEFAULT_ROADMAP = Path(__file__).resolve().parents[1] / "docs" / "ROADMAP.md"


class TrackerError(ValueError):
    """Raised when the achievement tracker is incomplete or invalid."""


def parse_tracker(document: str) -> dict[str, str]:
    """Return the status of each active achievement in the collection table."""
    in_collection = False
    result: dict[str, str] = {}

    for line in document.splitlines():
        if line.startswith("## "):
            if in_collection:
                break
            in_collection = "Colecția" in line
            continue

        if not in_collection or not line.startswith("|"):
            continue

        columns = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(columns) < 2:
            continue

        name = next(
            (item for item in ACHIEVEMENTS if re.search(r"\b" + re.escape(item) + r"\b", columns[0], re.I)),
            None,
        )
        if name is None:
            continue
        if name in result:
            raise TrackerError(f"Duplicate achievement in collection: {name}")

        status_column = columns[1]
        unlocked = "✅" in status_column
        locked = "⬜" in status_column
        pending = bool(re.search(r"\bPENDING\b", status_column, re.IGNORECASE))
        if (unlocked and (locked or pending)) or (not unlocked and not locked):
            raise TrackerError(f"Unrecognized status for {name}: {status_column}")

        if unlocked:
            result[name] = "unlocked"
        elif pending:
            result[name] = "pending"
        else:
            result[name] = "remaining"

    missing = [name for name in ACHIEVEMENTS if name not in result]
    if missing:
        raise TrackerError("Missing achievements from collection: " + ", ".join(missing))

    return {name: result[name] for name in ACHIEVEMENTS}


def get_report(document: str) -> dict:
    """Produce counts and per-achievement states for display or JSON export."""
    statuses = parse_tracker(document)
    unlocked = sum(status == "unlocked" for status in statuses.values())
    pending = sum(status == "pending" for status in statuses.values())
    return {
        "total": len(ACHIEVEMENTS),
        "unlocked": unlocked,
        "pending": pending,
        "remaining": len(ACHIEVEMENTS) - unlocked - pending,
        "achievements": [{"name": name, "status": status} for name, status in statuses.items()],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Show progress from docs/ROADMAP.md.")
    parser.add_argument("--file", type=Path, default=DEFAULT_ROADMAP, help="Roadmap Markdown path")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    try:
        report = get_report(args.file.read_text(encoding="utf-8"))
    except (OSError, TrackerError) as error:
        print(f"Progress checker error: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"GitHub Achievements: {report['unlocked']}/{report['total']} unlocked")
        print(f"Pending: {report['pending']}")
        print(f"Not yet earned or attempted: {report['remaining']}")
        for achievement in report["achievements"]:
            symbol = {"unlocked": "✓", "pending": "⌛", "remaining": "·"}[achievement["status"]]
            print(f"  {symbol} {achievement['name']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
