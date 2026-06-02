#!/usr/bin/env python3
"""Build sources/2026-06-02-batch.yaml from cached SKILL.md files."""
import re, os, json, yaml
from pathlib import Path
from datetime import datetime

CACHE = Path('/Users/yichen/cainiao/AI/PersonalSite/claude-site/sources/cache/2026-06-02-batch')
DECODED = CACHE / '_decoded'
OUT = Path('/Users/yichen/cainiao/AI/PersonalSite/claude-site/sources/2026-06-02-batch.yaml')


def parse_fm(content: str) -> dict:
    if not content.startswith('---'):
        return {}
    try:
        end = content.index('\n---', 3)
        return yaml.safe_load(content[3:end].strip()) or {}
    except Exception:
        return {}


def trim_desc(s: str) -> str:
    s = (s or '').strip().replace('\n', ' ')
    s = re.sub(r'\s+', ' ', s)
    if len(s) > 240:
        s = s[:237] + '...'
    return s


def read(name: str) -> str:
    p = DECODED / f'{name}.md'
    return p.read_text(encoding='utf-8') if p.exists() else ''


# ─────────── Plugin metadata ───────────
# repo, branch, license, author, plugin_name, plugin_overview_id, plugin_overview_name_cn
PLUGINS = {
    'pua': dict(owner='tanweai', repo='pua', branch='main', license='Unlicense',
                author='tanweai', plugin='pua',
                overview_id='pua-workflow', overview_cn='PUA 多人格 Coding 助手集',
                overview_desc='中文 Claude Code 人格切换插件集，用各种"老板/产品/打工人"人设逼 AI 把活干漂亮。'),
    'ecc': dict(owner='affaan-m', repo='ecc', branch='main', license='MIT',
                author='affaan-m', plugin='ecc',
                overview_id='ecc-workflow', overview_cn='ECC 持续学习 Skills 大全',
                overview_desc='Everything Claude Code (ECC) — 一套 249 个 SKILL.md 的"持续学习"工具箱，覆盖 TDD、安全审计、检索、评测、自治 loop 等场景。'),
    'oh-my-claudecode': dict(owner='Yeachan-Heo', repo='oh-my-claudecode', branch='main', license='MIT',
                author='Yeachan-Heo', plugin='oh-my-claudecode',
                overview_id='oh-my-claudecode-workflow', overview_cn='Oh-My-ClaudeCode 个人工作流',
                overview_desc='韩国独立开发者 Yeachan-Heo 的 Claude Code 个人 plugin，包含 autopilot/ralph/ultrawork/deep-interview/team 等 8 个核心 SKILL，主打"长跑式"研发自治。'),
    'gstack': dict(owner='garrytan', repo='gstack', branch='main', license='MIT',
                author='Garry Tan', plugin='gstack',
                overview_id='gstack-workflow', overview_cn='gstack 创业全流程 Skills',
                overview_desc='Y Combinator 总裁 Garry Tan 的个人 Claude Code 工具集：从 office-hours 头脑风暴 → CEO/Eng 双重计划评审 → 设计 → QA → ship 部署，覆盖创业团队完整研发链路。'),
    'claude-mem': dict(owner='thedotmack', repo='claude-mem', branch='main', license='Apache-2.0',
                author='Alex Newman', plugin='claude-mem',
                overview_id='claude-mem-workflow', overview_cn='claude-mem 持久记忆系统',
                overview_desc='为 Claude Code 提供跨 session 持久记忆压缩系统：自动观察工具调用、生成语义摘要、注入新 session。配套 SQLite + Chroma 向量库 + 10 个 MCP 搜索接口。'),
    'ralph': dict(owner='snarktank', repo='ralph', branch='main', license='MIT',
                author='snarktank', plugin='ralph',
                overview_id='ralph-workflow', overview_cn='Ralph 自治 Agent 系统',
                overview_desc='Ralph 是一个自治 Agent 系统，吃 PRD 自己干活直到完成。仓库附带 prd 起草 + ralph PRD-JSON 转换两个 SKILL，是 Ralph 工作流的入口。'),
    'ui-ux-pro-max-skill': dict(owner='nextlevelbuilder', repo='ui-ux-pro-max-skill', branch='main', license='MIT',
                author='nextlevelbuilder', plugin='ui-ux-pro-max-skill',
                overview_id='ui-ux-pro-max-workflow', overview_cn='UI/UX Pro Max 设计套件',
                overview_desc='一站式品牌/设计系统/UI 样式/Banner/Slides/Logo/CIP 全套 UI 设计 Skills，搭配 Gemini 3.1 Pro 与 Chart.js 生成视觉素材，55 种 Logo 风格 + 50 件 CIP 物料。'),
}


# ─────────── Single-skill / Tool / Framework / Subagent ───────────
SINGLES = [
    # (cached_name, id, name, name_cn, owner, repo, branch, path, kind, license, author, source_type, desc_override)
    ('agent-browser_skill', 'agent-browser', 'agent-browser', 'AI 代理浏览器自动化',
     'vercel-labs', 'agent-browser', 'main', 'skills/agent-browser/SKILL.md',
     'tool', 'Apache-2.0', 'Vercel Labs', 'single-skill', None),
    ('web-access_skill', 'web-access', 'web-access', '浏览器联网操作中枢',
     'eze-is', 'web-access', 'main', 'SKILL.md',
     'skill', 'Unlicense', 'eze-is', 'single-skill', None),
    ('planning-with-files_skill', 'planning-with-files', 'planning-with-files', '基于文件的实施计划',
     'OthmanAdi', 'planning-with-files', 'master', 'skills/planning-with-files/SKILL.md',
     'skill', 'MIT', 'OthmanAdi', 'single-skill', None),
    ('vercel-labs_find-skills.skill.json', 'find-skills', 'find-skills', 'Skills 发现与一键安装',
     'vercel-labs', 'skills', 'main', 'skills/find-skills/SKILL.md',
     'skill', 'Apache-2.0', 'Vercel Labs', 'single-skill', None),
    ('anthropics_code-simplifier.agent.json', 'code-simplifier', 'code-simplifier', '代码简化 Subagent',
     'anthropics', 'claude-plugins-official', 'main', 'plugins/code-simplifier/agents/code-simplifier.md',
     'subagent', 'Apache-2.0', 'Anthropic', 'single-skill', None),
    # OpenSpec — Framework, no SKILL.md, point to README as plugin-overview style
    ('Fission-AI_OpenSpec.readme.json', 'openspec', 'openspec', 'OpenSpec 规格驱动开发框架',
     'Fission-AI', 'OpenSpec', 'main', 'README.md',
     'framework', 'MIT', 'Fission AI', 'single-skill',
     'OpenSpec is a spec-driven development framework for AI coding agents. Distributed via npm install -g @fission-ai/openspec, with /opsx:propose, /opsx:apply, /opsx:archive slash commands to align AI coders with intended behavior before code is written.'),
]


# ─────────── Plugin skills ───────────
# (cached_name, id, plugin_key, skill_name_override, name_cn, path)
PLUGIN_SKILLS = [
    # pua 8
    ('pua_pua', 'pua-pua', 'pua', None, 'PUA 老板模式', 'skills/pua/SKILL.md'),
    ('pua_p7', 'pua-p7', 'pua', None, 'P7 资深工程师', 'skills/p7/SKILL.md'),
    ('pua_p9', 'pua-p9', 'pua', None, 'P9 技术专家', 'skills/p9/SKILL.md'),
    ('pua_p10', 'pua-p10', 'pua', None, 'P10 资深技术专家', 'skills/p10/SKILL.md'),
    ('pua_pro', 'pua-pro', 'pua', None, '产品经理 PRO 模式', 'skills/pro/SKILL.md'),
    ('pua_mama', 'pua-mama', 'pua', None, '老妈关怀模式', 'skills/mama/SKILL.md'),
    ('pua_yes', 'pua-yes', 'pua', None, 'Yes 极简肯定', 'skills/yes/SKILL.md'),
    ('pua_pua-loop', 'pua-pua-loop', 'pua', None, 'PUA 自动 Loop', 'skills/pua-loop/SKILL.md'),
    # ecc 10
    ('ecc_continuous-learning-v2', 'ecc-continuous-learning-v2', 'ecc', None, '持续学习 v2', 'skills/continuous-learning-v2/SKILL.md'),
    ('ecc_tdd-workflow', 'ecc-tdd-workflow', 'ecc', None, 'TDD 测试驱动开发', 'skills/tdd-workflow/SKILL.md'),
    ('ecc_security-review', 'ecc-security-review', 'ecc', None, '安全审计', 'skills/security-review/SKILL.md'),
    ('ecc_iterative-retrieval', 'ecc-iterative-retrieval', 'ecc', None, '迭代检索', 'skills/iterative-retrieval/SKILL.md'),
    ('ecc_strategic-compact', 'ecc-strategic-compact', 'ecc', None, '战略性压缩 Context', 'skills/strategic-compact/SKILL.md'),
    ('ecc_eval-harness', 'ecc-eval-harness', 'ecc', None, '评测框架', 'skills/eval-harness/SKILL.md'),
    ('ecc_verification-loop', 'ecc-verification-loop', 'ecc', None, '验证 Loop', 'skills/verification-loop/SKILL.md'),
    ('ecc_search-first', 'ecc-search-first', 'ecc', None, 'Search-First 优先搜索', 'skills/search-first/SKILL.md'),
    ('ecc_skill-stocktake', 'ecc-skill-stocktake', 'ecc', None, 'Skill 盘点', 'skills/skill-stocktake/SKILL.md'),
    ('ecc_autonomous-loops', 'ecc-autonomous-loops', 'ecc', None, '自治 Loop 模式', 'skills/autonomous-loops/SKILL.md'),
    # oh-my-claudecode 8
    ('omc_autopilot', 'omc-autopilot', 'oh-my-claudecode', None, 'Autopilot 自动驾驶', 'skills/autopilot/SKILL.md'),
    ('omc_ralph', 'omc-ralph', 'oh-my-claudecode', None, 'Ralph 长跑模式', 'skills/ralph/SKILL.md'),
    ('omc_ultrawork', 'omc-ultrawork', 'oh-my-claudecode', None, 'Ultrawork 深度工作', 'skills/ultrawork/SKILL.md'),
    ('omc_deep-interview', 'omc-deep-interview', 'oh-my-claudecode', None, '深度访谈模式', 'skills/deep-interview/SKILL.md'),
    ('omc_team', 'omc-team', 'oh-my-claudecode', None, '多 Agent 团队协作', 'skills/team/SKILL.md'),
    ('omc_ccg', 'omc-ccg', 'oh-my-claudecode', None, 'CCG Commit 信息生成', 'skills/ccg/SKILL.md'),
    ('omc_ask', 'omc-ask', 'oh-my-claudecode', None, '快问快答 Ask', 'skills/ask/SKILL.md'),
    ('omc_autoresearch', 'omc-autoresearch', 'oh-my-claudecode', None, '自动研究 Autoresearch', 'skills/autoresearch/SKILL.md'),
    # gstack 10
    ('gstack_office-hours', 'gstack-office-hours', 'gstack', None, '创业 Office Hours 头脑风暴', 'office-hours/SKILL.md'),
    ('gstack_plan-ceo-review', 'gstack-plan-ceo-review', 'gstack', None, 'CEO 视角策略评审', 'plan-ceo-review/SKILL.md'),
    ('gstack_plan-eng-review', 'gstack-plan-eng-review', 'gstack', None, 'Eng 视角架构评审', 'plan-eng-review/SKILL.md'),
    ('gstack_review', 'gstack-review', 'gstack', None, '代码 Diff 审查', 'review/SKILL.md'),
    ('gstack_qa', 'gstack-qa', 'gstack', None, 'QA 行为测试', 'qa/SKILL.md'),
    ('gstack_ship', 'gstack-ship', 'gstack', None, 'Ship 一键发布', 'ship/SKILL.md'),
    ('gstack_investigate', 'gstack-investigate', 'gstack', None, '问题根因调查', 'investigate/SKILL.md'),
    ('gstack_design-shotgun', 'gstack-design-shotgun', 'gstack', None, '设计霰弹评审', 'design-shotgun/SKILL.md'),
    ('gstack_autoplan', 'gstack-autoplan', 'gstack', None, 'Autoplan 全自动评审管线', 'autoplan/SKILL.md'),
    ('gstack_spec', 'gstack-spec', 'gstack', None, '可交付 Spec 起草', 'spec/SKILL.md'),
    # claude-mem 10
    ('cm_mem-search', 'claude-mem-mem-search', 'claude-mem', None, '记忆搜索（自然语言查询）', 'plugin/skills/mem-search/SKILL.md'),
    ('cm_knowledge-agent', 'claude-mem-knowledge-agent', 'claude-mem', None, '知识 Agent', 'plugin/skills/knowledge-agent/SKILL.md'),
    ('cm_learn-codebase', 'claude-mem-learn-codebase', 'claude-mem', None, '学习代码库', 'plugin/skills/learn-codebase/SKILL.md'),
    ('cm_smart-explore', 'claude-mem-smart-explore', 'claude-mem', None, '智能探索（项目/代码）', 'plugin/skills/smart-explore/SKILL.md'),
    ('cm_timeline-report', 'claude-mem-timeline-report', 'claude-mem', None, '时间线报告', 'plugin/skills/timeline-report/SKILL.md'),
    ('cm_make-plan', 'claude-mem-make-plan', 'claude-mem', None, '制定计划', 'plugin/skills/make-plan/SKILL.md'),
    ('cm_pathfinder', 'claude-mem-pathfinder', 'claude-mem', None, 'Pathfinder 路线规划', 'plugin/skills/pathfinder/SKILL.md'),
    ('cm_weekly-digests', 'claude-mem-weekly-digests', 'claude-mem', None, '每周摘要', 'plugin/skills/weekly-digests/SKILL.md'),
    ('cm_babysit', 'claude-mem-babysit', 'claude-mem', None, 'Babysit 任务监督', 'plugin/skills/babysit/SKILL.md'),
    ('cm_design-is', 'claude-mem-design-is', 'claude-mem', None, '设计哲学 Design Is', 'plugin/skills/design-is/SKILL.md'),
    # ralph 2
    ('ralph_prd', 'ralph-prd', 'ralph', None, 'PRD 起草助手', 'skills/prd/SKILL.md'),
    ('ralph_ralph', 'ralph-ralph', 'ralph', None, 'PRD 转 Ralph JSON', 'skills/ralph/SKILL.md'),
    # ui-ux-pro-max-skill 7
    ('uxpm_banner-design', 'uxpm-banner-design', 'ui-ux-pro-max-skill', None, '横幅视觉设计', '.claude/skills/banner-design/SKILL.md'),
    ('uxpm_brand', 'uxpm-brand', 'ui-ux-pro-max-skill', None, '品牌一致性', '.claude/skills/brand/SKILL.md'),
    ('uxpm_design-system', 'uxpm-design-system', 'ui-ux-pro-max-skill', None, '设计系统与 Token', '.claude/skills/design-system/SKILL.md'),
    ('uxpm_design', 'uxpm-design', 'ui-ux-pro-max-skill', None, '综合设计套件（Logo/CIP/Banner/Icon）', '.claude/skills/design/SKILL.md'),
    ('uxpm_slides', 'uxpm-slides', 'ui-ux-pro-max-skill', None, '策略 HTML 演示', '.claude/skills/slides/SKILL.md'),
    ('uxpm_ui-styling', 'uxpm-ui-styling', 'ui-ux-pro-max-skill', None, 'UI 样式生成', '.claude/skills/ui-styling/SKILL.md'),
    ('uxpm_ui-ux-pro-max', 'uxpm-ui-ux-pro-max', 'ui-ux-pro-max-skill', None, 'UI/UX Pro Max 总入口', '.claude/skills/ui-ux-pro-max/SKILL.md'),
]


# ─────────── Plugin docs (ecc 2) ───────────
PLUGIN_DOCS = [
    ('ecc_doc_skill-development-guide', 'ecc-skill-development-guide', 'ecc', 'skill-development-guide',
     'Skill 开发指南', 'docs/SKILL-DEVELOPMENT-GUIDE.md',
     'How to build, test, and ship a skill in ECC: file structure, frontmatter requirements, naming conventions, when to extract subagents, and ECC\'s "continuous learning" iteration loop. Reference for contributors and skill authors.'),
    ('ecc_doc_skill-placement-policy', 'ecc-skill-placement-policy', 'ecc', 'skill-placement-policy',
     'Skill 放置策略', 'docs/SKILL-PLACEMENT-POLICY.md',
     'Where should a new behavior live? Decision tree for choosing between: a new SKILL.md, an existing skill\'s extension, a subagent, a slash command, or system-prompt overlay. ECC\'s opinionated organization principle.'),
]


def build_skill_entry(cached_name, eid, name, name_cn, owner, repo, branch, path,
                       kind, license_, author, source_type, desc_override,
                       plugin=None):
    content = read(cached_name)
    fm = parse_fm(content)
    sname = name or fm.get('name') or eid
    desc = desc_override if desc_override else trim_desc(fm.get('description', ''))
    if not desc and content:
        # if no frontmatter description, take first non-frontmatter para
        body = content
        if content.startswith('---'):
            try:
                body = content[content.index('\n---', 3) + 4:].strip()
            except Exception:
                pass
        first_para = body.split('\n\n')[0].strip()
        desc = trim_desc(first_para)
    raw_url = f'https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}'
    entry = {
        'id': eid,
        'source_url': f'https://github.com/{owner}/{repo}/blob/{branch}/{path}',
        'raw_url': raw_url,
        'repo_url': f'https://github.com/{owner}/{repo}',
        'skill_path': path,
        'skill_name': sname,
        'skill_name_cn': name_cn,
        'description_en': desc,
        'author': author,
        'license': license_,
        'source_type': source_type,
        'plugin': plugin,
        'sibling_skills': [],
        'status': 'approved',
        '_cached_name': cached_name,
    }
    if kind != 'skill':
        entry['kind'] = kind
    return entry


def main():
    entries = []

    # 1. Singles (single-skill / tool / framework / subagent)
    for s in SINGLES:
        cached, eid, name, name_cn, owner, repo, branch, path, kind, lic, author, st, desc_override = s
        entries.append(build_skill_entry(
            cached, eid, name, name_cn, owner, repo, branch, path,
            kind, lic, author, st, desc_override, plugin=None))

    # 2. Plugin skills
    for ps in PLUGIN_SKILLS:
        cached, eid, plugin_key, name_override, name_cn, path = ps
        meta = PLUGINS[plugin_key]
        # derive skill_name from path basename
        derived_name = path.split('/')[-2] if path.endswith('SKILL.md') else None
        sname = name_override or derived_name
        entries.append(build_skill_entry(
            cached, eid, sname, name_cn,
            meta['owner'], meta['repo'], meta['branch'], path,
            'skill', meta['license'], meta['author'],
            'plugin-skill', None, plugin=meta['plugin']))

    # 3. Plugin docs
    for pd in PLUGIN_DOCS:
        cached, eid, plugin_key, sname, name_cn, path, desc = pd
        meta = PLUGINS[plugin_key]
        entries.append(build_skill_entry(
            cached, eid, sname, name_cn,
            meta['owner'], meta['repo'], meta['branch'], path,
            'skill', meta['license'], meta['author'],
            'plugin-doc', desc, plugin=meta['plugin']))

    # 4. Plugin overviews — one per plugin (7)
    for plugin_key, meta in PLUGINS.items():
        eid = meta['overview_id']
        readme_path = 'README.md'
        cached_readme_name = f'{meta["owner"]}_{meta["repo"]}.readme.json'
        entries.append({
            'id': eid,
            'source_url': f'https://github.com/{meta["owner"]}/{meta["repo"]}',
            'raw_url': f'https://raw.githubusercontent.com/{meta["owner"]}/{meta["repo"]}/{meta["branch"]}/README.md',
            'repo_url': f'https://github.com/{meta["owner"]}/{meta["repo"]}',
            'skill_path': None,
            'skill_name': f'{meta["plugin"]}-workflow',
            'skill_name_cn': meta['overview_cn'],
            'description_en': meta['overview_desc'],
            'author': meta['author'],
            'license': meta['license'],
            'source_type': 'plugin-overview',
            'plugin': meta['plugin'],
            'sibling_skills': [],
            'status': 'approved',
            '_cached_name': cached_readme_name,
        })

    # 5. Wire up sibling_skills for each plugin
    plugin_skill_names = {}
    for e in entries:
        if e['source_type'] == 'plugin-skill':
            plugin_skill_names.setdefault(e['plugin'], []).append(e['skill_name'])
    for e in entries:
        if e['source_type'] in ('plugin-skill', 'plugin-overview', 'plugin-doc'):
            siblings = plugin_skill_names.get(e['plugin'], [])
            e['sibling_skills'] = [n for n in siblings if n != e['skill_name']]

    # Counts
    counts = {}
    for e in entries:
        counts[e['source_type']] = counts.get(e['source_type'], 0) + 1
    kinds = {}
    for e in entries:
        k = e.get('kind', 'skill')
        kinds[k] = kinds.get(k, 0) + 1

    output = {
        'batch_id': '2026-06-02',
        'generated_at': datetime.now().isoformat(timespec='seconds'),
        'total_entries': len(entries),
        'approved_count': sum(1 for e in entries if e['status'] == 'approved'),
        'counts_by_type': counts,
        'counts_by_kind': kinds,
        'entries': entries,
    }

    OUT.write_text(yaml.safe_dump(output, allow_unicode=True, sort_keys=False, width=120), encoding='utf-8')
    print(f'✅ Wrote {len(entries)} entries to {OUT}')
    print(f'   Counts by source_type: {counts}')
    print(f'   Counts by kind: {kinds}')


if __name__ == '__main__':
    main()
