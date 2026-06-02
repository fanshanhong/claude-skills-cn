#!/usr/bin/env python3
"""
generate_articles.py — 读 sources/<batch>.yaml 中 status: approved 的条目，
按 prompt-template-v3 喂给 Opus 4.7 生成中文文章。

抓 SKILL.md 必须走 GitHub Contents API（raw CDN 在本机网络下不稳）。

Usage:
  python3 scripts/generate_articles.py \
    --batch sources/2026-06-01-batch.yaml \
    --prompt experiments/pipeline-demo/prompt-template-v3.md \
    --output-dir articles/2026-06-01-batch \
    --log logs/2026-06-01-batch.jsonl \
    [--only <id>]              # 仅生成某一篇（试跑用）
    [--max-workers 4]          # 并发数
    [--dry-run]                # 不调 API，只打印 prompt size

Environment:
  ANTHROPIC_API_KEY — 必需
  GITHUB_TOKEN — 推荐（无则 60 req/hr）
"""

import argparse
import base64
import concurrent.futures
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

# Anthropic SDK
import anthropic

MODEL = "claude-opus-4-7"
# https://www.anthropic.com/pricing#api — Opus pricing as of session start
PRICE_INPUT_PER_MTOK = 15.0   # USD per 1M input tokens
PRICE_OUTPUT_PER_MTOK = 75.0  # USD per 1M output tokens
MAX_OUTPUT_TOKENS = 8192

GITHUB_API = "https://api.github.com"
USER_AGENT = "claude-skills-cn-generator/0.1"


# ────────────────────────── GitHub fetch (Contents API) ──────────────────────────


def github_get(path, token=None, retries=3, timeout=60):
    url = path if path.startswith("http") else f"{GITHUB_API}{path}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 403 and "rate limit" in e.read().decode("utf-8", "ignore").lower():
                wait = 60 * (attempt + 1)
                print(f"  rate limited, sleeping {wait}s...", file=sys.stderr)
                time.sleep(wait)
                last_err = e
                continue
            raise
        except urllib.error.URLError as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise last_err


def fetch_file_via_contents_api(owner, repo, path, ref, token=None):
    """Fetch full file content via Contents API. Returns decoded UTF-8 string."""
    encoded_path = urllib.parse.quote(path)
    api_path = f"/repos/{owner}/{repo}/contents/{encoded_path}?ref={ref}"
    data = github_get(api_path, token=token)
    if isinstance(data, list):
        raise ValueError(f"path is a directory: {path}")
    if data.get("encoding") != "base64":
        raise ValueError(f"unexpected encoding: {data.get('encoding')}")
    raw = base64.b64decode(data["content"])
    return raw.decode("utf-8", errors="replace")


def parse_github_blob_url(url):
    """Parse https://github.com/{owner}/{repo}/blob/{branch}/{path} → (owner, repo, branch, path)."""
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)", url)
    if not m:
        raise ValueError(f"unparseable blob URL: {url}")
    return m.groups()


def parse_github_repo_url(url):
    """Parse https://github.com/{owner}/{repo} → (owner, repo)."""
    m = re.match(r"https://github\.com/([^/]+)/([^/]+?)(?:/|$)", url.rstrip("/"))
    if not m:
        raise ValueError(f"unparseable repo URL: {url}")
    return m.groups()


# ────────────────────────── Prompt assembly ──────────────────────────


def load_system_prompt(prompt_template_path):
    """Load prompt-template-v3.md as the system prompt verbatim."""
    return Path(prompt_template_path).read_text(encoding="utf-8")


def build_user_message_single_or_plugin_skill(entry, skill_md_content):
    """For single-skill / plugin-skill."""
    sibling = entry.get("sibling_skills") or []
    sibling_str = ", ".join(sibling) if sibling else "（无，本 Skill 不属于 plugin）"

    parts = [
        "请按上述规则生成一篇中文文章。本次任务字段（由外层管线提供，禁止 AI 推断 URL）：",
        "",
        f"- SKILL_SOURCE_URL: {entry['source_url']}",
        f"- REPO_URL: {entry['repo_url']}",
        f"- AUTHOR: {entry['author']}",
        f"- LICENSE: {entry['license']}",
        f"- SOURCE_TYPE: {entry['source_type']}",
        f"- SIBLING_SKILLS: [{sibling_str}]",
        f"- SKILL_NAME: {entry['skill_name']}",
        f"- SKILL_NAME_CN: {entry.get('skill_name_cn') or ''}",
        f"- PLUGIN: {entry.get('plugin') or ''}",
        "",
    ]

    # license 提示：source-available 需特殊声明
    if "Source-Available" in str(entry.get("license", "")):
        parts.append(
            "⚠ 本 Skill 是 source-available（非开源）。请在文章顶部紧邻 frontmatter "
            "处加一段授权说明：「本 Skill 由 Anthropic 提供 source-available 授权，"
            "**仅供学习参考**，不允许再分发或商用。原始仓库请遵守授权条款。」"
        )
        parts.append("")

    parts.extend([
        "SKILL_MD_CONTENT（源 SKILL.md 全文，每行带行号便于 self-check 引用）：",
        "",
        "```markdown",
        _with_line_numbers(skill_md_content),
        "```",
        "",
        "请输出完整的 Markdown 文件：YAML frontmatter + 中文正文 + 末尾 self-check HTML 注释块。",
        "不要在 Markdown 外加任何说明文字（不要 ``` 包裹整篇）。",
    ])
    return "\n".join(parts)


SIBLING_TRUNCATE_CHARS = 6000  # ~2K tokens per sibling in plugin-overview


def _truncate_skill_for_overview(content, max_chars=SIBLING_TRUNCATE_CHARS):
    """Trim a SKILL.md to its frontmatter + opening section so the
    plugin-overview prompt fits within Opus's 200K context window even
    when a plugin has 10 enterprise-class SKILLs (e.g. gstack)."""
    if len(content) <= max_chars:
        return content
    return content[:max_chars] + f"\n\n...[已截断,完整 SKILL.md {len(content)} 字符,见单 Skill 文章]"


def build_user_message_plugin_overview(entry, readme_content, sibling_skill_contents):
    """For plugin-overview. sibling_skill_contents: dict[skill_name] = SKILL.md 全文."""
    parts = [
        "请按上述规则生成一篇 plugin-overview 中文工作流总览文章。本次任务字段：",
        "",
        f"- SKILL_SOURCE_URL: {entry['source_url']}（plugin 仓库主页）",
        f"- REPO_URL: {entry['repo_url']}",
        f"- AUTHOR: {entry['author']}",
        f"- LICENSE: {entry['license']}",
        f"- SOURCE_TYPE: {entry['source_type']}",
        f"- PLUGIN: {entry['plugin']}",
        f"- SIBLING_SKILLS（本 plugin 包含的全部 Skill）: {entry['sibling_skills']}",
        "",
        "PLUGIN_README（仓库 README.md 全文，带行号）：",
        "",
        "```markdown",
        _with_line_numbers(readme_content),
        "```",
        "",
        f"以下是本 plugin 全部 {len(sibling_skill_contents)} 个 SKILL.md 的内容(按 skill_name 字典序,过长的会截断保留前 {SIBLING_TRUNCATE_CHARS} 字符)。",
        "请基于这些内容总结：包含哪些 Skills、典型工作流串讲、Skill 间协作关系。",
        "",
    ]
    for skill_name in sorted(sibling_skill_contents.keys()):
        content = _truncate_skill_for_overview(sibling_skill_contents[skill_name])
        parts.extend([
            f"### SKILL: {skill_name}",
            "",
            "```markdown",
            content,
            "```",
            "",
        ])
    parts.extend([
        "请输出完整 Markdown：YAML frontmatter + 2000-3500 字正文 + 末尾 self-check 块。",
        "重点章节：『典型工作流串讲』至少 2 个串讲示例，每个示例 3-5 步 Skill 协作。",
    ])
    return "\n".join(parts)


def _with_line_numbers(text):
    lines = text.split("\n")
    width = len(str(len(lines)))
    return "\n".join(f"{i+1:>{width}}: {line}" for i, line in enumerate(lines))


# ────────────────────────── Entry processing ──────────────────────────


def load_cached(cache_dir, cached_name):
    """If sources/cache/<batch>/_decoded/<cached_name>.md exists, return its content."""
    if not cache_dir or not cached_name:
        return None
    p = Path(cache_dir) / "_decoded" / f"{cached_name}.md"
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None


def fetch_with_cache(entry, cache_dir, owner, repo, path, branch, gh_token):
    """Prefer local cache (via entry['_cached_name']); fall back to Contents API."""
    cached_name = entry.get("_cached_name") if isinstance(entry, dict) else None
    cached = load_cached(cache_dir, cached_name)
    if cached is not None:
        return cached
    return fetch_file_via_contents_api(owner, repo, path, branch, token=gh_token)


def fetch_sources_for_entry(entry, batch_entries, gh_token, cache_dir=None):
    """Fetch SKILL.md (and for plugin-overview, README + all sibling SKILL.md).

    Prefers cache_dir/_decoded/<entry._cached_name>.md when available.
    """
    source_type = entry["source_type"]

    if source_type in ("single-skill", "plugin-skill", "plugin-doc"):
        owner, repo, branch, path = parse_github_blob_url(entry["source_url"])
        content = fetch_with_cache(entry, cache_dir, owner, repo, path, branch, gh_token)
        return {"skill_md": content}

    elif source_type == "plugin-overview":
        # entry.repo_url 是 plugin 仓库；source_url 也是仓库主页
        owner, repo = parse_github_repo_url(entry["repo_url"])
        # 优先用 cache;cache 缺失再走 GH(main → master)
        readme = load_cached(cache_dir, entry.get("_cached_name"))
        if readme is None:
            try:
                readme = fetch_file_via_contents_api(owner, repo, "README.md", "main", token=gh_token)
            except Exception:
                readme = fetch_file_via_contents_api(owner, repo, "README.md", "master", token=gh_token)

        # 找出本 plugin 下所有 sibling 的 SKILL.md（从 batch_entries 中匹配同 plugin 的 plugin-skill）
        plugin_name = entry["plugin"]
        sibling_contents = {}
        for sib in batch_entries:
            if sib["source_type"] == "plugin-skill" and sib.get("plugin") == plugin_name:
                so, sr, sb, sp = parse_github_blob_url(sib["source_url"])
                try:
                    c = fetch_with_cache(sib, cache_dir, so, sr, sp, sb, gh_token)
                    sibling_contents[sib["skill_name"]] = c
                except Exception as e:
                    print(f"  ⚠ sibling fetch failed {sib['skill_name']}: {e}", file=sys.stderr)
        return {"readme": readme, "sibling_skills": sibling_contents}

    raise ValueError(f"unknown source_type: {source_type}")


def generate_one(entry, batch_entries, system_prompt, client, gh_token, output_dir, dry_run=False, cache_dir=None):
    eid = entry["id"]
    print(f"[{eid}] fetching sources...", file=sys.stderr)
    t0 = time.time()
    try:
        sources = fetch_sources_for_entry(entry, batch_entries, gh_token, cache_dir=cache_dir)
    except Exception as e:
        return {"id": eid, "ok": False, "error": f"fetch: {e}"}
    fetch_secs = time.time() - t0

    # 组装 user message
    if entry["source_type"] in ("single-skill", "plugin-skill", "plugin-doc"):
        user_msg = build_user_message_single_or_plugin_skill(entry, sources["skill_md"])
    else:
        user_msg = build_user_message_plugin_overview(entry, sources["readme"], sources["sibling_skills"])

    if dry_run:
        return {
            "id": eid,
            "ok": True,
            "dry_run": True,
            "user_msg_chars": len(user_msg),
            "user_msg_kchars": len(user_msg) // 1000,
            "fetch_secs": round(fetch_secs, 2),
        }

    # 调用 API
    print(f"[{eid}] calling API ({MODEL}), user_msg={len(user_msg)//1000}K chars...", file=sys.stderr)
    t1 = time.time()
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_OUTPUT_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:
        return {"id": eid, "ok": False, "error": f"api: {e}"}
    gen_secs = time.time() - t1

    # 提取生成内容
    text = "".join(block.text for block in resp.content if block.type == "text")

    # 用量
    usage = resp.usage
    in_tok = usage.input_tokens
    out_tok = usage.output_tokens
    cost = in_tok / 1e6 * PRICE_INPUT_PER_MTOK + out_tok / 1e6 * PRICE_OUTPUT_PER_MTOK

    # 写文件
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{eid}.md"
    out_path.write_text(text, encoding="utf-8")

    print(
        f"[{eid}] ✅ done in {gen_secs:.1f}s, in={in_tok} out={out_tok} "
        f"cost=${cost:.3f} → {out_path.name}",
        file=sys.stderr,
    )

    return {
        "id": eid,
        "ok": True,
        "output_path": str(out_path),
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "cost_usd": round(cost, 4),
        "fetch_secs": round(fetch_secs, 2),
        "gen_secs": round(gen_secs, 2),
        "source_type": entry["source_type"],
        "model": MODEL,
        "ts": datetime.now().isoformat(timespec="seconds"),
    }


# ────────────────────────── Main ──────────────────────────


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--batch", required=True, help="Path to sources/<batch>.yaml")
    p.add_argument("--prompt", required=True, help="Path to prompt-template-v3.md")
    p.add_argument("--output-dir", required=True, help="Where to write generated articles")
    p.add_argument("--log", required=True, help="JSONL log file path")
    p.add_argument("--only", help="Only generate this entry id (smoke test)")
    p.add_argument("--max-workers", type=int, default=4)
    p.add_argument("--dry-run", action="store_true", help="Skip API, only fetch + show sizes")
    args = p.parse_args()

    auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    if not auth_token and not api_key:
        print("❌ ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    gh_token = os.environ.get("GITHUB_TOKEN")
    if not gh_token:
        print("⚠ no GITHUB_TOKEN — rate limit 60/hr", file=sys.stderr)

    client_kwargs = {}
    if auth_token:
        client_kwargs["auth_token"] = auth_token
        print(f"using auth_token (Bearer), base_url={base_url or '<default>'}", file=sys.stderr)
    else:
        client_kwargs["api_key"] = api_key
        print(f"using api_key (x-api-key), base_url={base_url or '<default>'}", file=sys.stderr)
    if base_url:
        client_kwargs["base_url"] = base_url
    client = anthropic.Anthropic(**client_kwargs)
    system_prompt = load_system_prompt(args.prompt)

    batch_path = Path(args.batch)
    with batch_path.open() as f:
        batch = yaml.safe_load(f)
    all_entries = batch["entries"]
    approved = [e for e in all_entries if e.get("status") == "approved"]

    # cache_dir: sources/cache/<yaml-stem>/ —— fetch_sources_for_entry 优先读此目录
    # 命名约定:cache 目录与 yaml 文件同 stem(如 2026-06-02-batch.yaml ↔ cache/2026-06-02-batch/)
    cache_dir = batch_path.parent / "cache" / batch_path.stem
    if not cache_dir.exists():
        cache_dir = batch_path.parent / "cache" / (batch.get("batch_id") or "")
    if cache_dir.exists():
        print(f"using cache_dir: {cache_dir}", file=sys.stderr)
    else:
        cache_dir = None
        print("no cache_dir found, all fetches via GH Contents API", file=sys.stderr)

    if args.only:
        approved = [e for e in approved if e["id"] == args.only]
        if not approved:
            print(f"❌ no approved entry with id={args.only}", file=sys.stderr)
            sys.exit(1)

    print(f"Generating {len(approved)} articles (of {len(all_entries)} total, "
          f"{sum(1 for e in all_entries if e['status']=='approved')} approved in batch)",
          file=sys.stderr)

    output_dir = Path(args.output_dir)
    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as ex:
        futures = {
            ex.submit(generate_one, e, all_entries, system_prompt, client, gh_token, output_dir, args.dry_run, cache_dir): e["id"]
            for e in approved
        }
        for fut in concurrent.futures.as_completed(futures):
            r = fut.result()
            results.append(r)
            # 流式写 log
            with log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 汇总
    ok = [r for r in results if r["ok"]]
    bad = [r for r in results if not r["ok"]]
    total_cost = sum(r.get("cost_usd", 0) for r in ok)
    total_in = sum(r.get("input_tokens", 0) for r in ok)
    total_out = sum(r.get("output_tokens", 0) for r in ok)

    print("\n" + "=" * 60, file=sys.stderr)
    print(f"Done: {len(ok)} ok, {len(bad)} failed", file=sys.stderr)
    if not args.dry_run:
        print(f"Total tokens: input={total_in:,}, output={total_out:,}", file=sys.stderr)
        print(f"Total cost: ${total_cost:.2f}", file=sys.stderr)
    for r in bad:
        print(f"  ❌ {r['id']}: {r['error']}", file=sys.stderr)


if __name__ == "__main__":
    main()
