# Local achievement progress checker

The dashboard is maintained manually because GitHub doesn't provide a supported, reliable endpoint for granting or reading all personal achievement awards.

This tiny tool reads the **existing** `docs/ROADMAP.md` table and calculates accurate totals, with no dependencies outside Python.

## Usage

From the repository root:

```bash
python tools/achievement_status.py
```

Expected output with the current tracker:

```text
GitHub Achievements: 2/7 unlocked
Remaining: 5
  ✓ Pull Shark
  ✓ Quickdraw
  · YOLO
  · Pair Extraordinaire
  · Galaxy Brain
  · Starstruck
  · Public Sponsor
```

Machine-readable output:

```bash
python tools/achievement_status.py --json
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

After you **actually** receive a new GitHub award, update the status in `docs/ROADMAP.md` and run this checker again. It validates the seven active awards, ignores the higher-tier table, and returns a nonzero exit status for malformed or missing entries.

**Note:** This does not earn, award, or unlock achievements. It only tracks GitHub-awarded achievements that the owner has confirmed on their profile.
