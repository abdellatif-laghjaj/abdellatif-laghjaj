#!/usr/bin/env python3
"""Fetch the same profile contribution calendar used by the 3D README.

Only aggregate daily counts are requested and saved. GitHub includes private
contribution counts according to the user's profile settings; no repository
names, commit details, or credentials are written to the generated data.
Uses the standard library with GITHUB_TOKEN/GH_TOKEN, or an authenticated gh CLI.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
QUERY = """
query($user: String!) {
  user(login: $user) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
  }
}
"""


def graphql(variables):
    payload = json.dumps({"query": QUERY, "variables": variables}).encode()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        request = urllib.request.Request(
            "https://api.github.com/graphql", data=payload,
            headers={"Authorization": f"Bearer {token}",
                     "Content-Type": "application/json", "User-Agent": "commit-landscape"},
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.load(response)
        except urllib.error.HTTPError as error:
            raise RuntimeError(f"GitHub returned HTTP {error.code}; check token access.") from None
    else:
        response = subprocess.run(["gh", "api", "graphql", "--input", "-"],
                                  input=payload, capture_output=True, check=False, timeout=60)
        if response.returncode:
            raise RuntimeError("GitHub request failed. Authenticate gh or provide GITHUB_TOKEN.")
        result = json.loads(response.stdout)
    if result.get("errors"):
        messages = "; ".join(error.get("message", "Unknown GraphQL error") for error in result["errors"])
        raise RuntimeError(f"GitHub query failed: {messages}")
    if not result.get("data", {}).get("user"):
        raise RuntimeError("GitHub user was not found.")
    return result["data"]["user"]["contributionsCollection"]


def fetch(user):
    # No explicit date bounds: this matches the default query in the 3D action.
    calendar = graphql({"user": user})["contributionCalendar"]
    counts = {}
    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            date, count = day["date"], day["contributionCount"]
            parsed = dt.date.fromisoformat(date)
            if parsed.isoformat() != date or type(count) is not int or count < 0:
                raise RuntimeError("GitHub returned an unexpected contribution date or count.")
            if date in counts:
                raise RuntimeError("Duplicate calendar date; refusing an invalid snapshot.")
            counts[date] = count
    if not counts:
        raise RuntimeError("GitHub returned an empty contribution calendar.")
    dates = sorted(counts)
    start, end = dt.date.fromisoformat(dates[0]), dt.date.fromisoformat(dates[-1])
    if len(dates) != (end - start).days + 1:
        raise RuntimeError("Incomplete contribution calendar; refusing a partial snapshot.")
    total = calendar["totalContributions"]
    if type(total) is not int or total != sum(counts.values()):
        raise RuntimeError("Daily counts do not match GitHub's calendar total.")
    return {
        "sample": False,
        "user": user,
        "metric": "contributions",
        "description": "Daily GitHub profile contribution counts, including private contribution totals enabled on the profile. No private repository details are collected.",
        "source": {"url": f"https://github.com/{user}", "scope": "profile contribution calendar",
                   "api": "GitHub GraphQL contributionCalendar", "calendar_total": total},
        "start": str(start), "end": str(end),
        "days": [{"date": date, "contributions": counts[date]} for date in dates],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "bulletchicken"))
    args = parser.parse_args()
    data = fetch(args.user)
    destination = ROOT / "data/activity.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    temporary.replace(destination)
    total = sum(day["contributions"] for day in data["days"])
    active = sum(day["contributions"] > 0 for day in data["days"])
    print(f"{args.user}: {total} contributions across {active} active days ({data['start']} through {data['end']}).")


if __name__ == "__main__":
    main()
