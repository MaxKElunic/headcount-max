#!/usr/bin/env python3
"""Validate the source catalog: structure, license vocabulary, and that every skill named exists.

The catalog points agents at outside authorities. Two things make a pointer worse than none — a
reference to a skill that no longer exists, so nothing surfaces it, and a license class that is
wrong, so an agent reproduces text it was only allowed to read. Both are checkable here.

Reachability is not checked by default. A publisher being briefly down is not a reason to fail
somebody's pull request, so `--online` runs that separately and a scheduled workflow calls it.
"""
import argparse
import datetime
import glob
import os
import re
import sys
import tomllib

# Closed vocabulary. The three at the end are the ones most often assumed open and are not, which
# is the single most useful thing this catalog records — see sources/README.md.
LICENSES = {
    "public-domain-usgov", "public-domain", "cc0", "cc-by", "cc-by-sa",
    "attribution-required", "open-data",
    "free-to-read", "registration-required", "paywalled",
}
REQUIRED = ("id", "title", "publisher", "url", "license", "jurisdiction",
            "authoritative_for", "skills", "checked")
ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SKILL_REF = re.compile(r"^([a-z][a-z0-9-]*):([a-z][a-z0-9-]*)$")


def load():
    """Every source in the catalog, with the file it came from."""
    entries = []
    for path in sorted(glob.glob("sources/*.toml")):
        with open(path, "rb") as handle:
            data = tomllib.load(handle)
        for entry in data.get("source", []):
            entries.append((path, entry))
    return entries


def validate(entries):
    problems, seen = [], {}
    for path, entry in entries:
        where = f"{path}: {entry.get('id', '<no id>')}"
        for field in REQUIRED:
            if not entry.get(field):
                problems.append(f"{where}: missing {field}")
        if not entry.get("id"):
            continue
        if not ID.fullmatch(entry["id"]):
            problems.append(f"{where}: id is not lowercase-hyphenated")
        if entry["id"] in seen:
            problems.append(f"{where}: duplicate id, also in {seen[entry['id']]}")
        seen[entry["id"]] = path

        if entry.get("license") and entry["license"] not in LICENSES:
            problems.append(f"{where}: license {entry['license']!r} is not in the vocabulary — "
                            f"one of {', '.join(sorted(LICENSES))}")
        for field in ("url", "data"):
            value = entry.get(field)
            if value and not value.startswith("https://"):
                problems.append(f"{where}: {field} is not https")
        if entry.get("checked"):
            try:
                datetime.date.fromisoformat(str(entry["checked"]))
            except ValueError:
                problems.append(f"{where}: checked is not an ISO date")
        for ref in entry.get("skills", []):
            match = SKILL_REF.fullmatch(ref)
            if not match:
                problems.append(f"{where}: {ref!r} is not a department:skill reference")
                continue
            if not os.path.exists(f"plugins/{match[1]}/skills/{match[2]}/SKILL.md"):
                problems.append(f"{where}: `{ref}` does not exist")
    return problems


def reachable(entries):
    """Fetch every URL. Separate from validation because the network is not a property of the diff."""
    import urllib.error
    import urllib.request
    problems = []
    for path, entry in entries:
        for field in ("url", "data"):
            url = entry.get(field)
            if not url:
                continue
            request = urllib.request.Request(url, method="GET", headers={
                "User-Agent": "headcount-source-catalog/1.0 (+https://github.com/cbrock84/headcount)"
            })
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    if response.status >= 400:
                        problems.append(f"{entry['id']}: {field} returned {response.status}")
            except urllib.error.HTTPError as error:
                # 403 is routinely a bot filter rather than a dead link; report it as a warning.
                label = "warning" if error.code in (403, 429) else "problem"
                line = f"{entry['id']}: {field} returned {error.code} ({url})"
                print(f"  {label}: {line}")
                if label == "problem":
                    problems.append(line)
            except Exception as error:  # noqa: BLE001 — any transport failure is the same finding
                problems.append(f"{entry['id']}: {field} unreachable — {type(error).__name__} ({url})")
    return problems


def pointers(entries):
    """A skill with sources must say so, and a skill that says so must have them.

    The generated `references/sources.md` is only useful if the skill body sends the agent to it.
    Without this check the pairing rots in both directions at once: a skill gains sources and never
    mentions them, or loses its last source and keeps pointing at a file that is no longer emitted.
    """
    problems = []
    with_sources = {ref for _, e in entries for ref in e.get("skills", [])}
    for path in sorted(glob.glob("plugins/*/skills/*/SKILL.md")):
        parts = path.split(os.sep)
        ref = f"{parts[1]}:{parts[3]}"
        mentions = "\n## Sources\n" in open(path, encoding="utf-8").read()
        if ref in with_sources and not mentions:
            problems.append(f"{path}: has catalog sources but no `## Sources` section — "
                            f"the agent is never told the file exists")
        if mentions and ref not in with_sources:
            problems.append(f"{path}: has a `## Sources` section but nothing in the catalog "
                            f"lists `{ref}`")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online", action="store_true",
                        help="also fetch every URL; not run in the per-push build")
    args = parser.parse_args()

    entries = load()
    problems = validate(entries)
    if not problems:
        problems += pointers(entries)
    if args.online and not problems:
        problems += reachable(entries)

    for problem in problems:
        print(f"  {problem}")
    skills = {ref for _, e in entries for ref in e.get("skills", [])}
    print(f"sources: {len(entries)} checked across {len(skills)} skill(s), {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
