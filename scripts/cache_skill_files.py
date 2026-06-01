#!/usr/bin/env python3
"""
cache_skill_files.py — 把 batch yaml 中所有 approved 条目的 SKILL.md / README
预抓到本地 sources/cache/，给 subagent 用（避免并发打爆 GitHub rate limit）。

走 GitHub Contents API（本机网络下 raw CDN 不稳）。
"""

import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

GITHUB_API = "https://api.github.com"
USER_AGENT = "claude-skills-cn-cache/0.1"
BATCH_FILE = "sources/2026-06-01-batch.yaml"
CACHE_DIR = Path("sources/cache/2026-06-01-batch")


def github_get(path, token=None, retries=3, timeout=60):
    url = path if path.startswith("http") else f"{GITHUB_API}{path}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 403:
                body = e.read().decode("utf-8", "ignore")
                if "rate limit" in body.lower():
                    print(f"  rate limited, sleep 30s...", file=sys.stderr)
                    time.sleep(30)
                    continue
            raise
        except urllib.error.URLError as e:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"failed after {retries} retries: {url}")


def fetch_file(owner, repo, path, ref, token=None):
    encoded = urllib.parse.quote(path)
    api = f"/repos/{owner}/{repo}/contents/{encoded}?ref={ref}"
    data = github_get(api, token=token)
    if data.get("encoding") != "base64":
        raise ValueError(f"unexpected encoding: {data.get('encoding')}")
    return base64.b64decode(data["content"]).decode("utf-8", errors="replace")


def parse_blob_url(url):
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)", url)
    return m.groups() if m else None


def parse_repo_url(url):
    m = re.match(r"https://github\.com/([^/]+)/([^/]+?)(?:/|$)", url.rstrip("/"))
    return m.groups() if m else None


def cache_path_for(entry):
    """本地缓存路径，按 id 命名。"""
    return CACHE_DIR / f"{entry['id']}.md"


def cache_readme_path_for(plugin_name):
    return CACHE_DIR / f"_{plugin_name}_README.md"


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("⚠ no GITHUB_TOKEN — rate limit 60/hr", file=sys.stderr)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    with open(BATCH_FILE) as f:
        batch = yaml.safe_load(f)
    entries = [e for e in batch["entries"] if e.get("status") == "approved"]
    print(f"Caching {len(entries)} approved entries...", file=sys.stderr)

    # 1) single-skill + plugin-skill 抓自己的 SKILL.md
    skill_targets = [e for e in entries if e["source_type"] in ("single-skill", "plugin-skill")]
    # 2) plugin-overview 抓 README（sibling SKILL.md 复用上面抓的）
    overview_targets = [e for e in entries if e["source_type"] == "plugin-overview"]

    n_ok = 0
    n_fail = 0
    n_skip = 0

    for e in skill_targets:
        out = cache_path_for(e)
        if out.exists():
            n_skip += 1
            continue
        parsed = parse_blob_url(e["source_url"])
        if not parsed:
            print(f"  ❌ {e['id']}: unparseable url {e['source_url']}", file=sys.stderr)
            n_fail += 1
            continue
        owner, repo, branch, path = parsed
        try:
            content = fetch_file(owner, repo, path, branch, token=token)
            out.write_text(content, encoding="utf-8")
            print(f"  ✓ {e['id']} ({len(content)//1024}KB)", file=sys.stderr)
            n_ok += 1
        except Exception as ex:
            print(f"  ❌ {e['id']}: {ex}", file=sys.stderr)
            n_fail += 1

    for e in overview_targets:
        plugin = e["plugin"]
        out = cache_readme_path_for(plugin)
        if out.exists():
            n_skip += 1
            continue
        parsed = parse_repo_url(e["repo_url"])
        if not parsed:
            print(f"  ❌ {e['id']}: unparseable repo url", file=sys.stderr)
            n_fail += 1
            continue
        owner, repo = parsed
        try:
            content = fetch_file(owner, repo, "README.md", "main", token=token)
        except Exception:
            try:
                content = fetch_file(owner, repo, "README.md", "master", token=token)
            except Exception as ex:
                print(f"  ❌ {plugin} README: {ex}", file=sys.stderr)
                n_fail += 1
                continue
        out.write_text(content, encoding="utf-8")
        print(f"  ✓ {plugin} README ({len(content)//1024}KB)", file=sys.stderr)
        n_ok += 1

    print(f"\nDone: {n_ok} fetched, {n_skip} cached already, {n_fail} failed", file=sys.stderr)
    print(f"Cache dir: {CACHE_DIR}", file=sys.stderr)


if __name__ == "__main__":
    main()
