"""Tests for the read-only public GitHub REST API metrics integration."""

import unittest
from urllib.parse import parse_qs, urlsplit

from tools.github_public_metrics import GitHubMetricsError, collect_metrics


def fake_fetch(path):
    if path.startswith("/users/"):
        return [
            {"name": "MathHard", "stargazers_count": 4},
            {"name": "FTC-Programming-Atlas", "stargazers_count": 2},
            {"name": "Achievement-Lab", "stargazers_count": 4},
        ]

    if path.startswith("/search/issues?"):
        query = parse_qs(urlsplit(path).query)
        assert query["q"] == ["is:pr is:merged author:KiyamaPaD"]
        assert query["per_page"] == ["1"]
        return {"total_count": 19}

    raise AssertionError(f"Unexpected API path: {path}")


class GitHubMetricsTests(unittest.TestCase):
    def test_counts_public_repositories_and_merged_prs(self):
        report = collect_metrics("KiyamaPaD", fake_fetch)

        self.assertEqual(report["public_repositories"], 3)
        self.assertEqual(report["public_merged_prs"], 19)
        self.assertEqual(report["top_repositories"][0]["name"], "Achievement-Lab")
        self.assertEqual(report["top_repositories"][1]["name"], "MathHard")

    def test_rejects_invalid_username_before_any_requests(self):
        def never_called(path):
            self.fail(f"Unexpected API call: {path}")

        for username in ("", "../private", "bad name", "-bad"):
            with self.subTest(username=username):
                with self.assertRaises(GitHubMetricsError):
                    collect_metrics(username, never_called)

    def test_handles_empty_repository_list(self):
        def fetch(path):
            if path.startswith("/users/"):
                return []
            return {"total_count": 0}

        report = collect_metrics("test-user", fetch)

        self.assertEqual(report["public_repositories"], 0)
        self.assertEqual(report["top_repositories"], [])
        self.assertEqual(report["public_merged_prs"], 0)

    def test_paginates_repository_lists(self):
        visited = []

        def fetch(path):
            visited.append(path)
            if path.startswith("/users/"):
                page = parse_qs(urlsplit(path).query)["page"][0]
                if page == "1":
                    return [{"name": f"Repo-{i}", "stargazers_count": i} for i in range(100)]
                if page == "2":
                    return [{"name": "Last", "stargazers_count": 101}]
            return {"total_count": 101}

        report = collect_metrics("KiyamaPaD", fetch)

        self.assertEqual(report["public_repositories"], 101)
        self.assertEqual(report["top_repositories"][0]["name"], "Last")
        self.assertEqual(len(visited), 3)

    def test_rejects_unexpected_api_payloads(self):
        def bad_repo_list(path):
            return {"message": "API error"}

        with self.assertRaisesRegex(GitHubMetricsError, "list of repositories"):
            collect_metrics("KiyamaPaD", bad_repo_list)

        def bad_search(path):
            if path.startswith("/users/"):
                return []
            return {"message": "Rate limit reached"}

        with self.assertRaisesRegex(GitHubMetricsError, "PR search"):
            collect_metrics("KiyamaPaD", bad_search)


if __name__ == "__main__":
    unittest.main()
