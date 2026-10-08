#!/usr/bin/env python3
"""Refresh the Google Scholar citation data used by the publication badges.

The site renders citation badges from ``_data/citations.yml`` at build time.
Google Scholar offers no public API and sends no CORS headers, so a browser
cannot read it directly; the counts are collected here and committed with the
site instead (the scheduled GitHub Action runs this script for you).

Usage
-----
    python3 scripts/fetch_google_scholar_citations.py           # refresh in place
    python3 scripts/fetch_google_scholar_citations.py --check   # fail if stale
    python3 scripts/fetch_google_scholar_citations.py --soft    # never fail when blocked

The Scholar profile id comes from ``_data/profile.yml`` (``gscholar``); override
it with ``--scholar-id`` or ``$GOOGLE_SCHOLAR_ID``.

Publications are matched to Scholar by *normalized* title, so neither front
matter nor a Semantic Scholar id is required. Add ``google_scholar_title:`` to a
publication when the Scholar entry is worded differently, or
``google_scholar_citations:`` to pin a count by hand.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "_data" / "profile.yml"
PUBLICATIONS_DIR = ROOT / "_publications"
OUTPUT_PATH = ROOT / "_data" / "citations.yml"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
PAGE_SIZE = 100
MAX_PAGES = 10
MATCH_THRESHOLD = 0.90


class Blocked(Exception):
    """Google Scholar refused the request (captcha / rate limit)."""


# --------------------------------------------------------------------------- #
# Fetching
# --------------------------------------------------------------------------- #
def fetch(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", "replace")


def read_profile_id() -> str:
    text = PROFILE_PATH.read_text(encoding="utf-8") if PROFILE_PATH.exists() else ""
    match = re.search(r"^\s*gscholar:\s*(.+?)\s*(?:#.*)?$", text, re.MULTILINE)
    raw = match.group(1).strip().strip("\"'") if match else ""
    return raw


def extract_scholar_id(raw: str) -> str:
    """Accept a bare id, `id&hl=en`, or a full profile URL."""
    if not raw:
        return ""
    if "user=" in raw:
        raw = raw.split("user=", 1)[1]
    return re.split(r"[&\s]", raw, maxsplit=1)[0].strip()


def clean_text(value: str | None) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip() if value else ""


def find_anchor(row: str, class_name: str) -> tuple[str, str]:
    """Return (href, inner text) of the first <a> with the given class."""
    match = re.search(rf'<a([^>]*class="[^"]*\b{re.escape(class_name)}\b[^"]*"[^>]*)>(.*?)</a>', row, re.S)
    if not match:
        return "", ""
    href_match = re.search(r'href="([^"]*)"', match.group(1))
    return html.unescape(href_match.group(1)) if href_match else "", clean_text(match.group(2))


def parse_profile(page: str) -> dict:
    if "unusual traffic" in page.lower() or "not a robot" in page.lower():
        raise Blocked("Google Scholar served a captcha")
    if 'class="gsc_a_tr"' not in page and 'id="gsc_rsb_st"' not in page:
        raise Blocked("Google Scholar returned no profile data")

    # gsc_rsb_std cells come in pairs (all time, last five years) per row:
    # citations, h-index, i10-index.
    metrics = [int(value) for value in re.findall(r'class="gsc_rsb_std">(\d+)</td>', page)]
    name_match = re.search(r'id="gsc_prf_in"[^>]*>(.*?)</div>', page, re.S)

    entries = []
    for row in re.findall(r'<tr class="gsc_a_tr">(.*?)</tr>', page, re.S):
        title_href, title = find_anchor(row, "gsc_a_at")
        if not title:
            continue
        cites_href, cites_text = find_anchor(row, "gsc_a_ac")
        year_match = re.search(r'class="[^"]*\bgsc_a_hc\b[^"]*"[^>]*>(.*?)</span>', row, re.S)
        gray = [clean_text(value) for value in re.findall(r'<div class="gs_gray">(.*?)</div>', row, re.S)]
        citations = cites_text if cites_text.isdigit() else "0"

        entries.append(
            {
                "title": title,
                "authors": gray[0] if gray else "",
                "venue": gray[1] if len(gray) > 1 else "",
                "citations": int(citations),
                "year": clean_text(year_match.group(1)) if year_match else "",
                "citation_url": absolute(title_href),
                "cites_url": absolute(cites_href),
            }
        )

    return {
        "name": clean_text(name_match.group(1)) if name_match else "",
        "cited_by": metrics[0] if len(metrics) > 0 else 0,
        "h_index": metrics[2] if len(metrics) > 2 else 0,
        "i10_index": metrics[4] if len(metrics) > 4 else 0,
        "entries": entries,
    }


def absolute(href: str) -> str:
    if not href:
        return ""
    if href.startswith("http"):
        return href
    return "https://scholar.google.com" + (href if href.startswith("/") else "/" + href)


def fetch_all_entries(scholar_id: str) -> list[dict]:
    entries: list[dict] = []
    for page_index in range(MAX_PAGES):
        url = (
            "https://scholar.google.com/citations"
            f"?user={scholar_id}&hl=en&view_op=list_works&sortby=pubdate"
            f"&cstart={page_index * PAGE_SIZE}&pagesize={PAGE_SIZE}"
        )
        page = fetch(url)
        parsed = parse_profile(page)
        if page_index == 0:
            profile.update({key: value for key, value in parsed.items() if key != "entries"})
        found = parsed["entries"]
        if not found:
            break
        entries.extend(found)
        if len(found) < PAGE_SIZE:
            break
    return entries


# --------------------------------------------------------------------------- #
# Matching against local publications
# --------------------------------------------------------------------------- #
def normalize(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", title.lower())


def read_front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    block = (text[3:end] if end != -1 else text[3:]).strip("\n")
    fields: dict[str, str] = {}
    for key in ("title", "google_scholar_title", "google_scholar_citations", "google_scholar_url"):
        match = re.search(rf"^\s*{key}:\s*(.+?)\s*$", block, re.MULTILINE)
        if not match:
            continue
        value = match.group(1).strip()
        if value[:1] in ("'", '"') and value[-1:] == value[:1] and len(value) > 1:
            value = value[1:-1]
        fields[key] = value.strip().strip('"')
    return fields


def best_match(title: str, entries: list[dict]) -> dict | None:
    wanted = normalize(title)
    best, score = None, 0.0
    for entry in entries:
        if normalize(entry["title"]) == wanted:
            return entry
        ratio = SequenceMatcher(None, wanted, normalize(entry["title"])).ratio()
        if ratio > score:
            best, score = entry, ratio
    return best if best is not None and score >= MATCH_THRESHOLD else None


# --------------------------------------------------------------------------- #
# YAML output (stdlib only: JSON strings are valid YAML scalars)
# --------------------------------------------------------------------------- #
def yaml_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_yaml(data: dict) -> str:
    lines = [
        "# Generated by scripts/fetch_google_scholar_citations.py -- do not edit by hand.",
        "# Refresh with:  python3 scripts/fetch_google_scholar_citations.py",
        "source: google_scholar",
        f"scholar_id: {yaml_str(data['scholar_id'])}",
        f"generated_at: {yaml_str(data['generated_at'])}",
        "profile:",
        f"  name: {yaml_str(data['profile']['name'])}",
        f"  cited_by: {data['profile']['cited_by']}",
        f"  h_index: {data['profile']['h_index']}",
        f"  i10_index: {data['profile']['i10_index']}",
        f"  url: {yaml_str(data['profile']['url'])}",
        "papers:",
    ]
    if not data["papers"]:
        lines[-1] = "papers: {}"
    for title, paper in data["papers"].items():
        lines.append(f"  {yaml_str(title)}:")
        lines.append(f"    scholar_title: {yaml_str(paper['scholar_title'])}")
        lines.append(f"    citations: {paper['citations']}")
        lines.append(f"    year: {yaml_str(paper['year'])}")
        lines.append(f"    authors: {yaml_str(paper['authors'])}")
        lines.append(f"    venue: {yaml_str(paper['venue'])}")
        lines.append(f"    citation_url: {yaml_str(paper['citation_url'])}")
        lines.append(f"    cites_url: {yaml_str(paper['cites_url'])}")
    return "\n".join(lines) + "\n"


def without_timestamp(text: str) -> str:
    return re.sub(r"^generated_at:.*$", "", text, flags=re.MULTILINE)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
profile: dict = {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scholar-id", default=os.environ.get("GOOGLE_SCHOLAR_ID") or read_profile_id())
    parser.add_argument("--check", action="store_true", help="exit non-zero if the data file is stale")
    parser.add_argument("--soft", action="store_true", help="exit 0 instead of failing when Scholar blocks us")
    parser.add_argument("--out", default=str(OUTPUT_PATH))
    args = parser.parse_args()

    scholar_id = extract_scholar_id(args.scholar_id)
    if not scholar_id:
        print("error: no Google Scholar id (set gscholar in _data/profile.yml or use --scholar-id)", file=sys.stderr)
        return 2

    try:
        entries = fetch_all_entries(scholar_id)
    except (Blocked, urllib.error.URLError, TimeoutError) as exc:
        message = f"warning: could not read Google Scholar ({exc}); keeping the existing data file"
        print(message, file=sys.stderr)
        return 0 if args.soft else 1

    profile.setdefault("name", "")
    profile.setdefault("cited_by", 0)
    profile.setdefault("h_index", 0)
    profile.setdefault("i10_index", 0)
    profile["url"] = f"https://scholar.google.com/citations?user={scholar_id}&hl=en"

    papers: dict[str, dict] = {}
    matched_entries: set[int] = set()
    unmatched: list[str] = []
    for path in sorted(PUBLICATIONS_DIR.glob("*/*.md")):
        fields = read_front_matter(path)
        title = fields.get("title", "")
        if not title:
            continue
        if fields.get("google_scholar_citations"):
            continue  # pinned by hand in front matter
        entry = best_match(fields.get("google_scholar_title") or title, entries)
        if entry is None:
            unmatched.append(f"{title} ({path.relative_to(ROOT)})")
            continue
        matched_entries.add(id(entry))
        papers[title] = {
            "scholar_title": entry["title"],
            "citations": entry["citations"],
            "year": entry["year"],
            "authors": entry["authors"],
            "venue": entry["venue"],
            "citation_url": entry["citation_url"],
            "cites_url": entry["cites_url"],
        }

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {
        "scholar_id": scholar_id,
        "generated_at": generated_at,
        "profile": profile,
        "papers": papers,
    }

    out_path = Path(args.out)
    previous = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
    unchanged = without_timestamp(previous) == without_timestamp(render_yaml({**data, "generated_at": ""}))

    if unchanged and previous:
        print(f"up to date: {len(papers)} matched publication(s), {profile['cited_by']} profile citations")
    elif args.check:
        print(f"stale: {out_path.relative_to(ROOT)} needs a refresh", file=sys.stderr)
        return 1
    else:
        if unchanged and previous:  # keep the original timestamp when nothing else moved
            stored = re.search(r"^generated_at:.*$", previous, re.MULTILINE)
            data["generated_at"] = stored.group(0).split(":", 1)[1].strip().strip('"') if stored else generated_at
        out_path.write_text(render_yaml(data), encoding="utf-8")
        print(f"wrote {out_path.relative_to(ROOT)}: {len(papers)} matched publication(s), {profile['cited_by']} profile citations")

    for note in unmatched:
        print(f"  note: no Google Scholar entry for {note}")
    for index, entry in enumerate(entries):
        if id(entry) not in matched_entries:
            print(f"  note: Scholar entry not used by any publication: {entry['title']!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
