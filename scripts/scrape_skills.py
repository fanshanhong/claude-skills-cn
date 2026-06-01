#!/usr/bin/env python3
"""
scrape_skills.py — Discover SKILL.md files from seed sources and produce a
sources/<batch>.yaml draft for human review.

Per pipeline-rules.md (experiments/pipeline-demo/), the scraper does NOT
generate articles. It produces a metadata draft for yichen to review and
approve (status: pending_review → approved), after which a separate
generation script feeds approved entries to the AI pipeline.

Usage:
  python3 scrape_skills.py --seeds sources/seeds.yaml --output sources/2026-06-01-batch.yaml

Environment:
  GITHUB_TOKEN — optional, raises rate limit from 60/hr to 5000/hr
"""

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

import yaml

GITHUB_API = "https://api.github.com"
USER_AGENT = "claude-skills-cn-scraper/0.1"


def http_get(url, token=None, accept="application/vnd.github+json", retries=3, max_bytes=None, timeout=60):
    headers = {"User-Agent": USER_AGENT, "Accept": accept}
    if token and url.startswith(GITHUB_API):
        headers["Authorization"] = f"Bearer {token}"
    if max_bytes:
        headers["Range"] = f"bytes=0-{max_bytes - 1}"
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 403 and "rate limit" in e.read().decode("utf-8", "ignore").lower():
                wait = 60 * (attempt + 1)
                print(f"  rate limited, sleeping {wait}s...", file=sys.stderr)
                time.sleep(wait)
                last_err = e
                continue
            if e.code == 416 and max_bytes:
                return http_get(url, token=token, accept=accept, retries=1, max_bytes=None, timeout=timeout)
            raise
        except urllib.error.URLError as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise last_err


def github_api(path, token=None):
    url = path if path.startswith("http") else f"{GITHUB_API}{path}"
    return json.loads(http_get(url, token=token))


def fetch_frontmatter_only(url):
    """Fetch only enough bytes to parse YAML frontmatter (typically <4KB)."""
    raw = http_get(url, accept="text/plain", max_bytes=8192, timeout=30)
    return raw.decode("utf-8", errors="replace")


def fetch_via_contents_api(owner, repo, path, ref, token=None):
    """Fetch file content via GitHub Contents API (more stable than raw CDN)."""
    encoded_path = urllib.parse.quote(path)
    api_path = f"/repos/{owner}/{repo}/contents/{encoded_path}?ref={ref}"
    data = github_api(api_path, token=token)
    if isinstance(data, list):
        raise ValueError(f"path is a directory, not a file: {path}")
    if data.get("encoding") != "base64":
        raise ValueError(f"unexpected encoding: {data.get('encoding')}")
    raw = base64.b64decode(data["content"])
    return raw.decode("utf-8", errors="replace")


def parse_frontmatter(content):
    if not content.startswith("---"):
        return {}
    try:
        end = content.index("\n---", 3)
        return yaml.safe_load(content[3:end].strip()) or {}
    except (ValueError, yaml.YAMLError):
        return {}


def license_id(repo_info):
    lic = repo_info.get("license") or {}
    return lic.get("spdx_id") or lic.get("name") or "???"


def list_skill_md_in_repo(owner, repo, token=None):
    repo_info = github_api(f"/repos/{owner}/{repo}", token=token)
    branch = repo_info.get("default_branch", "main")
    tree = github_api(f"/repos/{owner}/{repo}/git/trees/{branch}?recursive=1", token=token)
    if tree.get("truncated"):
        print(f"  ⚠ tree truncated for {owner}/{repo} — some SKILL.md may be missed", file=sys.stderr)
    paths = []
    for entry in tree.get("tree", []):
        if entry["type"] != "blob":
            continue
        path = entry["path"]
        if not path.endswith("SKILL.md"):
            continue
        if any(seg in path.split("/") for seg in ("node_modules", ".git", "vendor")):
            continue
        paths.append(path)
    return paths, branch, repo_info


def derive_skill_id(skill_path, fm_name):
    if fm_name:
        return re.sub(r"[^a-z0-9-]+", "-", fm_name.lower()).strip("-")
    parts = skill_path.split("/")
    if len(parts) >= 2 and parts[-1] == "SKILL.md":
        return parts[-2]
    return skill_path.replace("/", "-").removesuffix(".md")


def build_entry(owner, repo, branch, path, repo_info, source_type, plugin_name, seed, token=None):
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    try:
        content = fetch_via_contents_api(owner, repo, path, branch, token=token)
    except Exception as e:
        print(f"  ⚠ contents API failed {path}: {e}; falling back to raw CDN", file=sys.stderr)
        try:
            content = fetch_frontmatter_only(raw_url)
        except Exception as e2:
            print(f"  ⚠ raw CDN also failed {path}: {e2}", file=sys.stderr)
            return None
    fm = parse_frontmatter(content)
    skill_id = derive_skill_id(path, fm.get("name"))
    description = (fm.get("description") or "").strip().replace("\n", " ")
    if len(description) > 240:
        description = description[:237] + "..."
    return {
        "id": f"{repo}-{skill_id}" if plugin_name else skill_id,
        "source_url": f"https://github.com/{owner}/{repo}/blob/{branch}/{path}",
        "raw_url": raw_url,
        "repo_url": f"https://github.com/{owner}/{repo}",
        "skill_path": path,
        "skill_name": fm.get("name") or skill_id,
        "skill_name_cn": None,
        "description_en": description,
        "author": seed.get("author_override") or owner,
        "license": seed.get("license_override") or license_id(repo_info),
        "source_type": source_type,
        "plugin": plugin_name,
        "sibling_skills": [],
        "status": "pending_review",
    }


def process_github_repo(seed, token):
    owner, repo = seed["repo"].split("/")
    pack_mode = seed.get("pack_mode", "collection")
    print(f"Scanning {owner}/{repo} (pack_mode={pack_mode})...", file=sys.stderr)

    paths, branch, repo_info = list_skill_md_in_repo(owner, repo, token=token)
    if not paths:
        print(f"  ⚠ no SKILL.md found", file=sys.stderr)
        return []
    print(f"  found {len(paths)} SKILL.md", file=sys.stderr)

    entries = []

    if pack_mode == "plugin":
        plugin_name = repo
        for path in paths:
            entry = build_entry(owner, repo, branch, path, repo_info,
                                source_type="plugin-skill", plugin_name=plugin_name, seed=seed, token=token)
            if entry:
                entries.append(entry)

        if entries:
            readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
            entries.append({
                "id": f"{repo}-workflow",
                "source_url": f"https://github.com/{owner}/{repo}",
                "raw_url": readme_url,
                "repo_url": f"https://github.com/{owner}/{repo}",
                "skill_path": None,
                "skill_name": f"{repo}-workflow",
                "skill_name_cn": None,
                "description_en": f"Plugin overview / workflow for {repo}",
                "author": seed.get("author_override") or owner,
                "license": seed.get("license_override") or license_id(repo_info),
                "source_type": "plugin-overview",
                "plugin": plugin_name,
                "sibling_skills": [],
                "status": "pending_review",
            })

        sibling_names = [e["skill_name"] for e in entries if e["source_type"] == "plugin-skill"]
        for e in entries:
            if e["source_type"] in ("plugin-skill", "plugin-overview"):
                e["sibling_skills"] = [n for n in sibling_names if n != e["skill_name"]]

    elif pack_mode == "collection":
        for path in paths:
            entry = build_entry(owner, repo, branch, path, repo_info,
                                source_type="single-skill", plugin_name=None, seed=seed, token=token)
            if entry:
                entries.append(entry)
    else:
        print(f"  ⚠ unknown pack_mode: {pack_mode}", file=sys.stderr)

    return entries


def process_direct_url(seed, token):
    url = seed["url"]
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)", url)
    if not m:
        print(f"⚠ unparseable url: {url}", file=sys.stderr)
        return []
    owner, repo, branch, path = m.groups()
    try:
        repo_info = github_api(f"/repos/{owner}/{repo}", token=token)
        branch = repo_info.get("default_branch", branch)
    except Exception as e:
        print(f"  ⚠ repo info fetch failed: {e}", file=sys.stderr)
        repo_info = {}
    entry = build_entry(owner, repo, branch, path, repo_info,
                        source_type=seed.get("source_type", "single-skill"),
                        plugin_name=seed.get("plugin"),
                        seed=seed, token=token)
    if entry and "id" in seed:
        entry["id"] = seed["id"]
    return [entry] if entry else []


SEED_HANDLERS = {
    "github_repo": process_github_repo,
    "direct_url": process_direct_url,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seeds", required=True, help="Path to seeds.yaml")
    parser.add_argument("--output", required=True, help="Path to write sources/<batch>.yaml")
    parser.add_argument("--batch-id", default=None, help="Batch ID (default: today's date)")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("⚠ no GITHUB_TOKEN — rate limit 60/hr", file=sys.stderr)

    with Path(args.seeds).open() as f:
        seeds_doc = yaml.safe_load(f) or {}
    seeds = seeds_doc.get("seeds", [])
    print(f"Loaded {len(seeds)} seeds", file=sys.stderr)

    all_entries = []
    for seed in seeds:
        handler = SEED_HANDLERS.get(seed.get("type"))
        if not handler:
            print(f"⚠ unknown seed type: {seed.get('type')}", file=sys.stderr)
            continue
        try:
            all_entries.extend(handler(seed, token))
        except Exception as e:
            print(f"⚠ seed {seed.get('repo') or seed.get('url')} failed: {e}", file=sys.stderr)

    seen = set()
    deduped = []
    for e in all_entries:
        if e["raw_url"] in seen:
            continue
        seen.add(e["raw_url"])
        deduped.append(e)

    batch_id = args.batch_id or datetime.now().strftime("%Y-%m-%d")
    counts = {t: sum(1 for e in deduped if e["source_type"] == t)
              for t in ("single-skill", "plugin-skill", "plugin-overview")}

    output = {
        "batch_id": batch_id,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "total_entries": len(deduped),
        "approved_count": 0,
        "counts_by_type": counts,
        "entries": deduped,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        yaml.safe_dump(output, f, allow_unicode=True, sort_keys=False, width=120)

    print(f"\n✅ Wrote {len(deduped)} entries to {output_path}", file=sys.stderr)
    print(f"   Breakdown: {counts}", file=sys.stderr)
    print(f"   Next: review {output_path}, change status: pending_review → approved", file=sys.stderr)


if __name__ == "__main__":
    main()
