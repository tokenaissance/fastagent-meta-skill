#!/usr/bin/env python3
"""Safely prepare and publish a fastagent agent skill through GitHub review gates.

This script absorbs the useful behavior of qiaomu-skill-publisher while keeping
fastagent-meta-skill's stricter release contract: no direct default-branch push,
immutable released versions, PR inspection, a versioned GitHub Release, and a
clean npx installation check before reporting success.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = PACKAGE_ROOT / "scripts"
DEFAULT_BRANCHES = {"main", "master"}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module("fastagent_publish_validate", SCRIPT_DIR / "validate_skill.py")
RELEASE = load_module("fastagent_publish_release", SCRIPT_DIR / "release_check.py")


class PublishError(RuntimeError):
    pass


@dataclass
class CommandResult:
    args: list[str]
    returncode: int | None
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


Runner = Callable[..., CommandResult]


def run(
    args: list[str],
    cwd: Path,
    *,
    timeout: float = 300.0,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> CommandResult:
    try:
        completed = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            env=env,
        )
        result = CommandResult(args, completed.returncode, completed.stdout.strip(), completed.stderr.strip())
    except (OSError, subprocess.TimeoutExpired) as exc:
        result = CommandResult(args, None, "", str(exc))
    if check and not result.ok:
        command = " ".join(args)
        detail = result.stderr or result.stdout or "unknown error"
        raise PublishError(f"command failed: {command}\n{detail}")
    return result


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PublishError(f"{path} must contain a JSON object")
    return payload


def identity(root: Path) -> dict[str, str]:
    skill_path = root / "SKILL.md"
    manifest_path = root / "manifest.json"
    if not skill_path.is_file():
        raise PublishError("missing SKILL.md")
    if not manifest_path.is_file():
        raise PublishError("missing manifest.json; public fastagent skills require versioned metadata")
    frontmatter = VALIDATOR.parse_frontmatter(skill_path.read_text(encoding="utf-8"))
    manifest = load_json(manifest_path)
    name = str(frontmatter.get("name", "")).strip()
    description = " ".join(str(frontmatter.get("description", "")).split())
    version = str(manifest.get("version", "")).strip()
    owner = str(manifest.get("owner", "tokenaissance")).strip() or "tokenaissance"
    if not name or not description:
        raise PublishError("SKILL.md frontmatter requires name and description")
    if manifest.get("name") != name:
        raise PublishError("manifest.json name does not match SKILL.md")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise PublishError("manifest.json version must be semantic X.Y.Z")
    return {"name": name, "description": description, "version": version, "owner": owner}


def parse_origin(url: str) -> tuple[str | None, str | None]:
    match = re.search(r"github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?$", url.strip())
    return (match.group(1), match.group(2)) if match else (None, None)


def origin_identity(root: Path, runner: Runner = run) -> tuple[str | None, str | None]:
    result = runner(["git", "remote", "get-url", "origin"], root, check=False)
    return parse_origin(result.stdout) if result.ok else (None, None)


def check_cli_prerequisites(root: Path, runner: Runner = run) -> None:
    for command in (["git", "--version"], ["gh", "--version"], ["npx", "--version"]):
        runner(command, root)
    runner(["gh", "auth", "status"], root)


def github_user(root: Path, explicit: str | None, origin_owner: str | None, runner: Runner = run) -> str:
    if explicit:
        return explicit
    if origin_owner:
        return origin_owner
    result = runner(["gh", "api", "user", "--jq", ".login"], root)
    if not result.stdout:
        raise PublishError("unable to resolve GitHub user")
    return result.stdout.strip()


def ensure_license(root: Path, owner: str, *, write: bool) -> list[str]:
    path = root / "LICENSE"
    if path.exists():
        return []
    if write:
        year = dt.datetime.now().year
        path.write_text(
            f"""MIT License

Copyright (c) {year} {owner}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",
            encoding="utf-8",
        )
    return ["LICENSE"]


def generated_readme(meta: dict[str, str], github_owner: str, repo: str, upstream: str) -> str:
    description = meta["description"]
    hook = re.split(r"[。.]", description, maxsplit=1)[0].strip()
    upstream_line = f"Upstream inspiration: {upstream}" if upstream else "Upstream inspiration: none declared"
    return f"""# {repo}

> {hook}.

[![GitHub Release](https://img.shields.io/github/v/release/{github_owner}/{repo}?display_name=tag&sort=semver)](https://github.com/{github_owner}/{repo}/releases)
[![Stars](https://img.shields.io/github/stars/{github_owner}/{repo}?style=flat-square)](https://github.com/{github_owner}/{repo}/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/{github_owner}/{repo}?style=flat-square)](https://github.com/{github_owner}/{repo}/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](LICENSE)
[![English](https://img.shields.io/badge/Docs-English-black)](README.md)
[![中文](https://img.shields.io/badge/Docs-%E4%B8%AD%E6%96%87-red)](docs/README.zh-CN.md)

`{repo}` turns "{description}" into a package that is discoverable, reliably triggered, validated, and safe to publish.

```bash
npx skills add {github_owner}/{repo}
```

## Why this skill

{description}

## What makes it more than a plain prompt

| Capability | Plain approach | {repo} |
|---|---:|---:|
| Turn a workflow into a reusable skill | copy a prompt into a file | ✓ |
| Record keep / adapt / reject / invent against prior art | skip research | ✓ |
| Test phrasings that should and should not trigger | guess | ✓ |
| Validate layout, version, and context budget | trust it | ✓ |
| Prepare README, LICENSE, and install verification | skip | ✓ |
| Publish through feature branch, PR, Release, and clean install | push to main | ✓ |

## Natural-language examples

- "Use ${meta['name']} to turn this workflow into a reusable skill."
- "Audit the inputs and boundaries first, then run ${meta['name']} end to end and verify."
- "Follow the full ${meta['name']} workflow and do not skip any gate."

## What it produces

```text
{repo}/
├── SKILL.md                    # agent routing and minimal execution skeleton
├── README.md                   # human-facing product page
├── docs/README.zh-CN.md        # Chinese translation
├── LICENSE                     # default MIT
├── manifest.json               # version, author, platforms, and gates
├── agents/interface.yaml       # cross-agent interface
├── references/                 # long methods, judgment, and safety boundaries
├── scripts/                    # repeatable verification and deterministic tools
├── evals/trigger_cases.json    # should-trigger, should-not-trigger, near-neighbor cases
└── reports/                    # Skill IR, research, eval, and release evidence
```

## One complete workflow

1. **Intent**: confirm the repeated job, target users, inputs, outputs, and success criteria.
2. **Research**: search prior art, verify sources, and record keep / adapt / reject / invent.
3. **Package**: write a lean `SKILL.md`, long judgment in references, deterministic actions in scripts.
4. **Eval**: test trigger boundaries first; add output or human eval when risk justifies it.
5. **Release**: check version, README, license, secrets, and install entry; publish through a feature branch and PR.
6. **Verify**: create a Release and complete a clean public install.

## Installation and verification

```bash
npx skills add {github_owner}/{repo}
test -f ~/.agents/skills/{meta['name']}/SKILL.md
python3 ~/.agents/skills/{meta['name']}/scripts/validate_skill.py ~/.agents/skills/{meta['name']}
```

## Prerequisites

- [ ] Node.js and npx installed: `node --version && npx --version`
- [ ] Python 3 installed: `python3 --version`
- [ ] Reviewed the skill's permissions and risk boundary

## Output and risks

Installing yields the complete skill package, including `SKILL.md`, `references/`, `scripts/`, `evals/`, and declared assets; the exact output follows the skill's Output Contract.

- The skill operates within local files and explicit authorization; it should not silently expand its own permissions.
- Review public files before publishing for secrets, cookies, private paths, or unverified claims.
- Agent skills can execute code; review the source and permissions before installing.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `No valid skills found` | invalid YAML frontmatter | use a block scalar `description: |` and revalidate |
| Skill not found | wrong install source or name | run `npx skills add {github_owner}/{repo} --list` |
| Validation script fails | missing prerequisites or evidence | add what the error path names, then rerun |

## Design philosophy

A skill is closer to compiling personal experience into source code an agent can execute than to a fixed "correct answer". Install it, run one real task, then fork: delete rules that are not yours and add your own judgment, tools, style, and eval.

## Credits and sources

{upstream_line}

## Security and evidence boundary

- Public claims must match trigger, output, runtime, install, or human evidence actually present; without it, label `missing evidence`.
- Publishing is an external write; it runs only when explicitly requested, through a feature branch, PR, Release, and clean public install.

## License

MIT (see LICENSE for copyright holders).
"""


def generated_readme_zh(meta: dict[str, str], github_owner: str, repo: str, upstream: str) -> str:
    hook = re.split(r"[。.]", meta["description"], maxsplit=1)[0].strip()
    upstream_line = f"上游灵感：{upstream}" if upstream else "上游灵感：未声明"
    return f"""# {repo}

> {hook}。

[![English](https://img.shields.io/badge/Docs-English-black)](../README.md)
[![中文](https://img.shields.io/badge/Docs-%E4%B8%AD%E6%96%87-red)](README.zh-CN.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](../LICENSE)

`{repo}` 把「{meta['description']}」变成真正能被发现、能稳定触发、能通过验证、还能安全发布的 Skill。

```bash
npx skills add {github_owner}/{repo}
```

## 为什么值得用

{meta['description']}

## 能力对比

| 能力 | 普通做法 | {repo} |
|---|---:|---:|
| 把工作流做成可复用的 Skill | 把提示词复制进文件 | ✓ |
| 记录 keep / adapt / reject / invent | 跳过调研 | ✓ |
| 测试该触发与不该触发的说法 | 靠猜 | ✓ |
| 校验目录、版本与上下文预算 | 相信它 | ✓ |
| 准备 README、LICENSE 与安装验证 | 跳过 | ✓ |
| 经功能分支、PR、Release 与干净安装发布 | 直接推 main | ✓ |

## 你可以直接这样说

- “使用 ${meta['name']} 把这个工作流做成可复用的 Skill。”
- “先审计输入和边界，再按 ${meta['name']} 完整执行并验证。”
- “按 ${meta['name']} 的完整工作流执行，不要跳过门禁。”

## 它会产出什么

```text
{repo}/
├── SKILL.md                    # Agent 路由与最小执行骨架
├── README.md                   # 给人看的产品页
├── docs/README.zh-CN.md        # 中文翻译
├── LICENSE                     # 默认 MIT
├── manifest.json               # 版本、作者、平台与门禁
├── agents/interface.yaml       # 跨 Agent 接口
├── references/                 # 长方法、判断与安全边界
├── scripts/                    # 可重复验证与确定性工具
├── evals/trigger_cases.json    # 应触发、不应触发、近邻场景
└── reports/                    # Skill IR、研究、评测与发布证据
```

## 一套完整工作流

1. **Intent**：确认重复任务、目标用户、输入、输出与成功标准。
2. **Research**：先搜同类，验源，记录 keep / adapt / reject / invent。
3. **Package**：写精简 `SKILL.md`，长判断放 references，确定性动作放 scripts。
4. **Eval**：先测触发边界；风险需要时再补输出或人工评测。
5. **Release**：检查版本、README、许可证、秘密与安装入口，经功能分支和 PR 发布。
6. **Verify**：创建 Release，并在隔离环境完成干净安装。

## 安装与验证

```bash
npx skills add {github_owner}/{repo}
test -f ~/.agents/skills/{meta['name']}/SKILL.md
python3 ~/.agents/skills/{meta['name']}/scripts/validate_skill.py ~/.agents/skills/{meta['name']}
```

## 前置条件

- [ ] 已安装 Node.js 与 npx：`node --version && npx --version`
- [ ] 已安装 Python 3：`python3 --version`
- [ ] 已阅读该 Skill 的权限与风险边界

## 输出与风险

安装后得到完整 Skill 包，包括 `SKILL.md`、`references/`、`scripts/`、`evals/` 与已声明的资产；具体输出以 Skill 的 Output Contract 为准。

- Skill 以本地文件和明确授权为边界，不应静默扩大权限。
- 发布前检查公开文件中没有密钥、Cookie、私有路径或未经验证的结果声明。
- Agent Skill 具有执行能力；安装前请审查源码与权限。

## Troubleshooting

| 问题 | 原因 | 解决 |
|---|---|---|
| `No valid skills found` | YAML frontmatter 无效 | 使用块标量 `description: |` 并重新验证 |
| 找不到 Skill | 安装源或名称错误 | 运行 `npx skills add {github_owner}/{repo} --list` |
| 验证脚本失败 | 前置依赖或证据文件缺失 | 按错误路径补齐后重新运行 |

## 设计哲学

Skill 更接近把个人经验编译成 Agent 可以执行的源代码，而不是一套不可修改的「标准答案」。先安装、跑一个真实任务，再 fork：删除不属于你的规则，加入你自己的判断、工具、风格与评测。

## 致谢

{upstream_line}

## 安全与证据边界

- 公开声明必须匹配实际存在的触发、输出、运行时、安装或人工证据；没有就标记 `missing evidence`。
- 发布是外部写操作，只有明确要求时才执行，并通过功能分支、PR、Release 与公开安装验证。

## License

MIT（版权持有者见 LICENSE）。
"""


PLACEHOLDERS = (
    r"<!--\s*TODO",
    r"your-org/your-repo",
    r"docs/assets/product-screenshot\.png",
    r"特性\s*1[：:]描述",
    r"\[用户的自然语言输入\]",
    r"\[解决方案\]",
    r"（在此补充",
)


def readme_languages(root: Path) -> list[str]:
    """Languages a package must ship READMEs for.

    Defaults to English-primary bilingual (README.md + docs/README.zh-CN.md).
    `manifest.json` may override with `readme_languages` (e.g. ["zh-CN"] for a
    purely internal Chinese skill, per the GitHub README playbook exception).
    """
    manifest_path = root / "manifest.json"
    if manifest_path.is_file():
        try:
            declared = load_json(manifest_path).get("readme_languages")
            if isinstance(declared, list):
                normalized = [str(item).strip() for item in declared if str(item).strip()]
                if normalized:
                    return normalized
        except (ValueError, json.JSONDecodeError):
            pass
    return ["en", "zh-CN"]


def _readme_requirements(text: str, upstream: str) -> dict[str, bool]:
    return {
        "install command": "npx skills add" in text,
        "natural-language examples": "Natural-language examples" in text or "你可以直接这样说" in text,
        "verification command": "validate_skill.py" in text,
        "prerequisite checklist": "- [ ]" in text,
        "troubleshooting": "Troubleshooting" in text,
        "license": "## License" in text or "## 许可证" in text,
        "upstream credit": not upstream or upstream in text,
    }


def _check_readme_file(path: Path, label: str, upstream: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    failures = [f"{label} placeholder found: {pattern}" for pattern in PLACEHOLDERS if re.search(pattern, text, re.I)]
    requirements = _readme_requirements(text, upstream)
    failures.extend(f"{label} missing {item}" for item, passed in requirements.items() if not passed)
    return failures


def check_readme(root: Path, upstream: str) -> list[str]:
    languages = readme_languages(root)
    english = "en" in languages
    chinese_only = "zh-CN" in languages and not english
    failures: list[str] = []

    if chinese_only:
        path = root / "README.md"
        if not path.is_file():
            return ["README.md missing"]
        failures.extend(_check_readme_file(path, "README", upstream))
        return failures

    en_path = root / "README.md"
    zh_path = root / "docs" / "README.zh-CN.md"
    if not en_path.is_file():
        failures.append("README.md missing")
    if "zh-CN" in languages and not zh_path.is_file():
        failures.append("docs/README.zh-CN.md missing")
    if en_path.is_file():
        failures.extend(_check_readme_file(en_path, "README", upstream))
        if "zh-CN" in languages and "docs/README.zh-CN.md" not in en_path.read_text(encoding="utf-8"):
            failures.append("README.md language badge does not link to docs/README.zh-CN.md")
    if zh_path.is_file():
        failures.extend(_check_readme_file(zh_path, "README.zh-CN.md", upstream))
        if "../README.md" not in zh_path.read_text(encoding="utf-8"):
            failures.append("docs/README.zh-CN.md language badge does not link back to ../README.md")
    return failures


def prepare_package(
    root: Path,
    meta: dict[str, str],
    github_owner: str,
    repo: str,
    *,
    write: bool,
) -> dict[str, Any]:
    manifest = load_json(root / "manifest.json")
    upstream = str(manifest.get("upstream_inspiration", "")).strip()
    changes = ensure_license(root, meta["owner"], write=write)
    readme = root / "README.md"
    if not readme.exists():
        changes.append("README.md")
        changes.append("docs/README.zh-CN.md")
        if write:
            en_meta = dict(meta)
            description_en = str(manifest.get("description_en", "")).strip()
            if description_en:
                en_meta["description"] = description_en
            readme.write_text(generated_readme(en_meta, github_owner, repo, upstream), encoding="utf-8")
            zh_path = root / "docs" / "README.zh-CN.md"
            zh_path.parent.mkdir(parents=True, exist_ok=True)
            zh_path.write_text(generated_readme_zh(meta, github_owner, repo, upstream), encoding="utf-8")
    failures = [] if not write and not readme.exists() else check_readme(root, upstream)
    return {"changes": sorted(set(changes)), "failures": failures}


def repo_exists(root: Path, slug: str, runner: Runner = run) -> bool:
    return runner(["gh", "repo", "view", slug, "--json", "url"], root, check=False).ok


def release_exists(root: Path, slug: str, version: str, runner: Runner = run) -> bool:
    return runner(["gh", "release", "view", f"v{version}", "--repo", slug], root, check=False).ok


def is_git_repo(root: Path, runner: Runner = run) -> bool:
    return runner(["git", "rev-parse", "--is-inside-work-tree"], root, check=False).stdout == "true"


def default_branch(root: Path, slug: str, runner: Runner = run) -> str:
    result = runner(
        ["gh", "repo", "view", slug, "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"],
        root,
        check=False,
    )
    return result.stdout.strip() if result.ok and result.stdout.strip() else "main"


def branch_slug(name: str, version: str) -> str:
    safe_name = re.sub(r"[^a-z0-9-]+", "-", name.lower()).strip("-")
    return f"codex/publish-{safe_name}-v{version.replace('.', '-')}"


def assert_feature_branch(branch: str, default: str) -> None:
    if not branch or branch in DEFAULT_BRANCHES or branch == default:
        raise PublishError(f"refusing direct default-branch publication: {branch or '<detached>'}")
    if not branch.startswith("codex/"):
        raise PublishError(f"publication branch must use the codex/ prefix: {branch}")


def copy_package(source: Path, destination: Path) -> None:
    ignore = shutil.ignore_patterns(".git", ".DS_Store", "__pycache__", "*.pyc", "*.pyo")
    shutil.copytree(source, destination, dirs_exist_ok=True, ignore=ignore)


def staged_changes(root: Path, runner: Runner = run) -> bool:
    return not runner(["git", "diff", "--cached", "--quiet"], root, check=False).ok


def pr_is_mergeable(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    mergeable = payload.get("mergeable")
    if mergeable != "MERGEABLE":
        blockers.append(f"PR mergeability is not ready: {mergeable or 'unknown'}")
    if payload.get("reviewDecision") == "CHANGES_REQUESTED":
        blockers.append("PR has requested changes")
    if any(review.get("state") == "CHANGES_REQUESTED" for review in payload.get("reviews") or []):
        blockers.append("a PR review requested changes")
    for check in payload.get("statusCheckRollup") or []:
        conclusion = check.get("conclusion")
        status = check.get("status")
        state = check.get("state")
        if conclusion in {"FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"}:
            blockers.append(f"check failed: {check.get('name', 'unknown')}")
        elif state in {"ERROR", "FAILURE", "PENDING", "EXPECTED"}:
            blockers.append(f"status check not successful: {check.get('context', 'unknown')}")
        elif status and (status != "COMPLETED" or conclusion is None):
            blockers.append(f"check still pending: {check.get('name', 'unknown')}")
    return not blockers, blockers


def verify_discovery(root: Path, slug: str, skill_name: str, runner: Runner = run) -> dict[str, Any]:
    listed = runner(["npx", "--yes", "skills", "add", slug, "--list"], root, timeout=300, check=False)
    ok = listed.ok and "Found" in listed.stdout and skill_name in listed.stdout and "No valid skills found" not in listed.stdout
    return {"ok": ok, "returncode": listed.returncode, "skill": skill_name, "found": skill_name in listed.stdout}


def sync_local(source: Path, skill_name: str) -> dict[str, Any]:
    target = Path.home() / ".agents" / "skills" / skill_name
    if target.resolve() == source.resolve():
        return {"status": "skipped", "target": str(target), "reason": "source is already canonical"}
    staging = target.parent / f".{skill_name}.incoming"
    backup_root = Path.home() / ".agents" / "skill-backups"
    timestamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = backup_root / f"{skill_name}-{timestamp}"
    if staging.exists():
        raise PublishError(f"stale local sync staging path exists: {staging}")
    copy_package(source, staging)
    if target.exists() or target.is_symlink():
        backup_root.mkdir(parents=True, exist_ok=True)
        target.rename(backup)
    staging.rename(target)
    return {"status": "updated" if backup.exists() else "created", "target": str(target), "backup": str(backup) if backup.exists() else None}


def release_check(root: Path, phase: str, *, install: bool) -> dict[str, Any]:
    report = RELEASE.evaluate(root, phase, run_tests=True, install_check=install)
    if not report["ok"]:
        blocks = [item["gate"] for item in report["gates"] if item["status"] == "block"]
        raise PublishError(f"{phase} release gates blocked: {', '.join(blocks)}")
    return report


def publish(args: argparse.Namespace, runner: Runner = run) -> dict[str, Any]:
    source = Path(args.skill_dir).expanduser().resolve()
    if not source.is_dir():
        raise PublishError(f"skill directory does not exist: {source}")
    meta = identity(source)
    check_cli_prerequisites(source, runner)
    origin_owner, origin_repo = origin_identity(source, runner)
    owner = github_user(source, args.github_user, origin_owner, runner)
    repo = args.repo_name or origin_repo or meta["name"]
    slug = f"{owner}/{repo}"
    planned = prepare_package(
        source,
        meta,
        owner,
        repo,
        write=not args.dry_run,
    )
    if args.dry_run:
        return {
            "ok": not planned["failures"],
            "mode": "dry-run",
            "skill": meta,
            "repository": slug,
            "repository_exists": repo_exists(source, slug, runner),
            "would_change": planned["changes"],
            "failures": planned["failures"],
            "default_branch_push": "forbidden",
        }
    if planned["failures"]:
        raise PublishError("README preparation failed: " + "; ".join(planned["failures"]))
    package = VALIDATOR.validate(source)
    if not package["ok"] or package["warnings"]:
        raise PublishError(f"package validation failed: {package}")
    if args.prepare_only:
        return {"ok": True, "mode": "prepare-only", "skill": meta, "repository": slug, "changes": planned["changes"]}

    exists = repo_exists(source, slug, runner)
    if exists and release_exists(source, slug, meta["version"], runner):
        if not args.verify_only:
            raise PublishError(
                f"release v{meta['version']} already exists; bump manifest.json before publishing changes, "
                "or use --verify-only"
            )
        discovery = verify_discovery(source, slug, meta["name"], runner)
        published = release_check(source, "published", install=True)
        return {"ok": discovery["ok"] and published["ok"], "mode": "verify-only", "repository": slug, "discovery": discovery, "release": published}

    if args.verify_only:
        raise PublishError("--verify-only requires an existing versioned release")

    if not exists:
        visibility = "--private" if args.private else "--public"
        runner(
            [
                "gh",
                "repo",
                "create",
                slug,
                visibility,
                "--add-readme",
                "--description",
                meta["description"][:300],
            ],
            source,
        )

    source_origin = origin_identity(source, runner)
    source_matches = is_git_repo(source, runner) and source_origin == (owner, repo)
    temporary: tempfile.TemporaryDirectory[str] | None = None
    if source_matches:
        workspace = source
    else:
        temporary = tempfile.TemporaryDirectory(prefix="fastagent-skill-publish-")
        workspace = Path(temporary.name) / repo
        runner(["git", "clone", f"https://github.com/{slug}.git", str(workspace)], source)
        copy_package(source, workspace)

    default = default_branch(workspace, slug, runner)
    current_result = runner(["git", "branch", "--show-current"], workspace, check=False)
    current = current_result.stdout.strip() if current_result.ok else ""
    branch = args.branch or (current if current and current != default else branch_slug(meta["name"], meta["version"]))
    if current != branch:
        runner(["git", "switch", "-c", branch], workspace)
    assert_feature_branch(branch, default)

    local_gates = release_check(workspace, "local", install=False)
    secrets = RELEASE.scan_secrets(workspace)
    if secrets:
        raise PublishError(f"secret scan blocked publication: {secrets}")
    runner(["git", "add", "-A"], workspace)
    runner(["git", "diff", "--cached", "--check"], workspace)
    if staged_changes(workspace, runner):
        runner(["git", "commit", "-m", f"release: prepare {meta['name']} v{meta['version']}"], workspace)
    runner(["git", "push", "-u", "origin", branch], workspace)

    existing_pr = runner(
        ["gh", "pr", "list", "--repo", slug, "--head", branch, "--state", "open", "--json", "url", "--jq", ".[0].url"],
        workspace,
        check=False,
    )
    pr_url = existing_pr.stdout.strip() if existing_pr.ok else ""
    if not pr_url:
        body = (
            f"Publish `{meta['name']}` v{meta['version']} through the fastagent governed release flow.\n\n"
            "- package validation and secret scan run locally\n"
            "- no direct default-branch push\n"
            "- merge is followed by a versioned Release and clean installation check"
        )
        created = runner(
            [
                "gh",
                "pr",
                "create",
                "--repo",
                slug,
                "--base",
                default,
                "--head",
                branch,
                "--title",
                f"release: {meta['name']} v{meta['version']}",
                "--body",
                body,
            ],
            workspace,
        )
        pr_url = created.stdout.strip().splitlines()[-1]
    pr_gates = release_check(workspace, "pr", install=False)
    review = runner(
        [
            "gh",
            "pr",
            "view",
            pr_url,
            "--repo",
            slug,
            "--json",
            "url,state,mergeable,reviewDecision,statusCheckRollup,comments,reviews",
        ],
        workspace,
    )
    review_payload = json.loads(review.stdout)
    mergeable, blockers = pr_is_mergeable(review_payload)
    if not mergeable:
        raise PublishError("PR is not ready to merge: " + "; ".join(blockers))
    if args.no_merge:
        return {
            "ok": True,
            "mode": "pr-ready",
            "repository": slug,
            "branch": branch,
            "pull_request": pr_url,
            "local_gates": local_gates["summary"],
            "pr_gates": pr_gates["summary"],
            "discussion_count": len(review_payload.get("comments") or []),
        }

    runner(
        [
            "gh",
            "pr",
            "merge",
            pr_url,
            "--repo",
            slug,
            "--squash",
            "--delete-branch",
            "--subject",
            f"release: {meta['name']} v{meta['version']}",
        ],
        workspace,
    )
    runner(["git", "fetch", "origin", default], workspace)
    runner(["git", "switch", default], workspace)
    runner(["git", "pull", "--ff-only", "origin", default], workspace)
    runner(
        [
            "gh",
            "release",
            "create",
            f"v{meta['version']}",
            "--repo",
            slug,
            "--target",
            default,
            "--title",
            f"v{meta['version']}",
            "--generate-notes",
        ],
        workspace,
    )
    discovery = verify_discovery(workspace, slug, meta["name"], runner)
    if not discovery["ok"]:
        raise PublishError(f"npx skill discovery failed: {discovery}")
    published = release_check(workspace, "published", install=True)
    sync = {"status": "skipped"} if args.no_sync_local else sync_local(source, meta["name"])
    result = {
        "ok": True,
        "mode": "published",
        "repository": f"https://github.com/{slug}",
        "release": f"https://github.com/{slug}/releases/tag/v{meta['version']}",
        "install": f"npx skills add {slug}",
        "pull_request": pr_url,
        "discovery": discovery,
        "published_gates": published["summary"],
        "sync": sync,
        "direct_default_branch_push": False,
    }
    if temporary is not None:
        temporary.cleanup()
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare and publish a fastagent skill through branch, PR, Release, and install gates.")
    parser.add_argument("skill_dir", help="Skill package directory")
    parser.add_argument("--github-user")
    parser.add_argument("--repo-name")
    parser.add_argument("--branch", help="Feature branch; defaults to codex/publish-<skill>-v<version>")
    parser.add_argument("--private", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Read-only audit; do not edit files or GitHub")
    parser.add_argument("--prepare-only", action="store_true", help="Prepare local LICENSE/README and stop")
    parser.add_argument("--verify-only", action="store_true", help="Verify an existing release and clean install")
    parser.add_argument("--no-merge", action="store_true", help="Stop after the PR passes local and PR gates")
    parser.add_argument("--no-sync-local", action="store_true", help="Do not sync a noncanonical source into ~/.agents/skills")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        result = publish(args)
    except (PublishError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        raise SystemExit(2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result.get("ok"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
