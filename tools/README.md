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
GitHub Achievements: 3/7 unlocked
Remaining: 4
  ✓ Pull Shark
  ✓ Quickdraw
  ✓ YOLO
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

## Public GitHub API metrics

The read-only `tools/github_public_metrics.py` script is a **real GitHub REST API integration** in development. It calls GitHub's public REST endpoints to retrieve a user's public repositories and the number of their publicly visible merged pull requests. It never writes to GitHub, uses no third-party dependencies, and does not access private account data.

From the repository root:

```bash
python tools/github_public_metrics.py --user KiyamaPaD
python tools/github_public_metrics.py --user KiyamaPaD --json
```

Its output includes the current public merged PR count and the top five public repositories by star count. API results can change at any time; **they do not confirm GitHub achievement awards**. GitHub may rate-limit unauthenticated API requests. This integration provides information; it cannot grant badges or enroll anyone in GitHub programs.

To run both test suites, use:

```bash
python -m unittest discover -s tests -v
```

### GitHub Developer Program

GitHub permits individual developers to register if they have an integration under development or in production that uses the GitHub API, plus a working support contact email. This repository's public-metrics script demonstrates the GitHub API integration. The owner must still register through [GitHub Developer Program](https://github.com/developer/register), supply their own support email, and verify the badge on their GitHub profile.

The **Developer Program Member** badge is a GitHub profile highlight, not one of the seven achievements counted in `docs/ROADMAP.md`.
