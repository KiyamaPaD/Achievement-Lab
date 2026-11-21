#!/usr/bin/env python3
"""Read public repository and merged PR metrics through the GitHub REST API.

The API does not expose reliable personal achievement award status. This is a
read-only GitHub integration, not an achievement-awarding service.
"""

import argparse
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


API_BASE = "https://api.github.com"
USERNAME_PATTERN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?")


class GitHubMetricsError(ValueError):
    """Raised when public GitHub metrics cannot be fetched or parsed."""


def get_json(path: str):
    """GET an API path using only standard-library HTTP and JSON modules."""
    request = Request(
        API_BASE + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Achievement-Lab-public-metrics",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    try:
        with urlopen(request, timeout=15) as response:
            return json.load(response)
    except HTTPError as error:
        raise GitHubMetricsError(f"GitHub API returned HTTP {error.code}") from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise GitHubMetricsError(f"Could not read GitHub API response: {error}") from error


def collect_metrics(username: str, fetch=get_json) -> dict:
    """Summarize public repos and public merged PRs, handling pagination."""
    if not USERNAME_PATTERN.fullmatch(username):
        raise GitHubMetricsError("Invalid GitHub username.")

    encoded = quote(username, safe="")
    repositories = []

    for page in range(1, 51):
        path = f"/users/{encoded}/repos?type=owner&per_page=100&page={page}"
        batch = fetch(path)

        if not isinstance(batch, list):
            raise GitHubMetricsError("Expected a list of repositories.")

        repositories.extend(batch)

        if len(batch) < 100:
            break
    else:
        raise GitHubMetricsError("Too many repository pages (limit: 50).")

    query = urlencode({"q": f"is:pr is:merged author:{username}", "per_page": 1})
    result = fetch(f"/search/issues?{query}")

    if not isinstance(result, dict) or type(result.get("total_count")) is not int:
        raise GitHubMetricsError("GitHub PR search returned an invalid response.")

    featured = []

    for repo in repositories:
        if not isinstance(repo, dict) or not isinstance(repo.get("name"), str):
            raise GitHubMetricsError("Invalid repository data.")

        stars = repo.get("stargazers_count")
        if type(stars) is not int or stars < 0:
            raise GitHubMetricsError("Invalid repository star count.")

        featured.append({"name": repo["name"], "stars": stars})

    featured.sort(key=lambda item: (-item["stars"], item["name"].lower()))

    return {
        "username": username,
        "public_repositories": len(repositories),
        "public_merged_prs": result["total_count"],
        "top_repositories": featured[:5],
        "note": "Public GitHub API data only. Achievement award status is not available.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Show public activity from GitHub's REST API.")
    parser.add_argument("--user", default="KiyamaPaD", help="GitHub username")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    try:
        metrics = collect_metrics(args.user)
    except GitHubMetricsError as error:
        print(f"GitHub metrics error: {error}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(metrics, indent=2, ensure_ascii=False))
    else:
        print(f"Public GitHub activity — {metrics['username']}")
        print(f"Merged public PRs: {metrics['public_merged_prs']}")
        print(f"Public repositories: {metrics['public_repositories']}")
        print("Most-starred public repositories:")

        for repo in metrics["top_repositories"]:
            print(f"  {repo['name']}: {repo['stars']} star(s)")

        print(metrics["note"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
