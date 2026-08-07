# fastagent-meta-skill

> Research, create, improve, migrate, evaluate, package, install-check, govern, and safely publish fastagent agent skills from workflows, prompts, transcripts, docs, SOPs, runbooks, scripts, or notes.

[![GitHub Release](https://img.shields.io/github/v/release/tokenaissance/fastagent-meta-skill?display_name=tag&sort=semver)](https://github.com/tokenaissance/fastagent-meta-skill/releases)
[![Stars](https://img.shields.io/github/stars/tokenaissance/fastagent-meta-skill?style=flat)](https://github.com/tokenaissance/fastagent-meta-skill/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/tokenaissance/fastagent-meta-skill)](https://github.com/tokenaissance/fastagent-meta-skill/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](LICENSE)
[![English](https://img.shields.io/badge/Docs-English-black)](README.md)
[![中文](https://img.shields.io/badge/Docs-%E4%B8%AD%E6%96%87-red)](docs/README.zh-CN.md)

`fastagent-meta-skill` builds reusable FastAgent skill packages, not long prompts. It turns "turn this workflow into a Skill" into a package that is discoverable, reliably triggered, validated, and safely published.

Give an agent a prompt, an SOP, a transcript, an old skill, a script, or a vague idea:

```text
Use the fastagent meta skill to turn this workflow into a reusable skill;
research the closest popular skills first, run trigger eval and safety checks, then publish to GitHub.
```

It handles: **intent convergence → prior-art research → synthesize keep/adapt/reject/invent → skill design → trigger eval → package validation → README → secret scan → PR → Release → npx install verification**.

**v2.8.1 local candidate verified:** 33/33 unit tests, 23/23 trigger cases, 0 package validation issues. Published evidence follows the [Releases](https://github.com/tokenaissance/fastagent-meta-skill/releases) page.

## Why I built this

A skill is becoming a genuinely reusable unit of software in the agent era, but "writing a `SKILL.md`" is far from a usable skill:

- A description written too broadly misfires everywhere; written too narrowly, it is never invoked.
- Renaming a long prompt to a filename does not make it a reliable workflow.
- Skipping prior-art research usually re-builds a worse wheel.
- Running locally does not mean others can install it, let alone that it is safe to publish.
- README, license, versioning, secret leaks, PR, Release, and install proof often all collapse at the last step.

Anthropic's and OpenAI's official `skill-creator` provide a solid foundation. This skill builds on top of them the parts that matter most when actually shipping dozens of skills: **research before creating, evidence-controlled quality, and safely publishing the finished package for others to use.**

The initial method comes from partner `yaojingang/yao-meta-skill`. We then studied and integrated public best practices for agent skills, and added dual-catalog search, GitHub source verification, evidence-aware release gates, and a self-contained publisher.

## What makes it more than a SKILL.md generator

| Capability | Plain "generate SKILL.md" | fastagent-meta-skill |
|---|---:|---:|
| Distill a workflow from prompt / SOP / transcript / old skill | ✓ | ✓ |
| Search skills.sh and SkillsMP for related skills first | | ✓ |
| Verify sources, maintenance, security, and license on GitHub | | ✓ |
| Record `keep / adapt / reject / invent` to avoid collage copying | | ✓ |
| Test real phrasings that should and should not trigger | depends | ✓ |
| Distinguish design advantage, validated advantage, and hypothesis | | ✓ |
| Validate layout, version, context budget, and recursive discovery | | ✓ |
| Prepare README and MIT License | | ✓ |
| Secret / API leak scan | | ✓ |
| Feature branch, PR, checks, Release | | ✓ |
| `npx skills add` public discovery and isolated install verification | | ✓ |

It does not make skills heavier; it matches complexity to risk: personal experiments use the lightweight `Scaffold` gate, and public releases enable the full `Governed` gate.

## Natural-language examples

- "Turn this repeated workflow into a skill the team can reuse."
- "Interview me and turn this implicit working method into a skill; ask one key question at a time."
- "Search the closest popular skills, analyze pros and cons, then build an original version."
- "Improve this existing skill's trigger rate, accuracy, and instruction following."
- "Audit this skill. Only give findings and fixes; do not modify files yet."
- "Publish this skill to GitHub, generate the npx install command, and prove a clean machine can install it."

## What it produces

According to scenario complexity, the meta skill creates the necessary, not ceremonial, files:

```text
your-skill/
├── SKILL.md                    # agent routing and minimal execution skeleton
├── README.md                   # human-facing product page
├── LICENSE                     # default MIT
├── manifest.json               # version, author, platforms, and gates
├── agents/interface.yaml       # cross-agent interface
├── references/                 # long methods, judgment, and safety boundaries
├── scripts/                    # repeatable verification and deterministic tools
├── evals/trigger_cases.json    # should-trigger, should-not-trigger, near-neighbor cases
└── reports/                    # Skill IR, research, eval, and release evidence
```

Personal experiments are never forced to have the full layout; public, high-risk, or team-reused skills add gates progressively.

## One complete workflow

1. **Intent**: confirm the repeated job, target users, inputs, outputs, exclusions, and success criteria.
2. **Search**: query skills.sh and SkillsMP with 2–4 intent-shaped keyword sets, then verify sources on GitHub.
3. **Synthesis**: record `keep / adapt / reject / invent` for each candidate and make the original contribution explicit.
4. **Package**: write a lean `SKILL.md`; put long judgment in references and deterministic actions in scripts.
5. **Eval**: test trigger boundaries first; add output, runtime, or human eval when risk justifies it.
6. **Release**: check version, README, license, secrets, and install entry; publish through a feature branch and PR.
7. **Verify**: create a Release, confirm the remote default branch, and complete a clean public install.

## Running inside FastAgent

When this skill runs in a FastAgent agent, new skills are persisted with the `write_file` path prefix `skills/<name>/`. The runtime routes that prefix to the per-user skills bucket (`~/.fastagent/users/<userId>/skills/<name>/`), which the next turn's skill scan discovers and mirrors to the workspace store for cloud pods. Any other path lands in a workspace folder nothing discovers.

```text
✅ write_file(path="skills/domain-check/SKILL.md", content=...)
❌ write_file(path="domain-check/SKILL.md", ...)   # lands in /workspace
```

A new skill becomes visible to the LLM on the **next turn**, not mid-turn.

## Installation

```bash
npx skills add tokenaissance/fastagent-meta-skill
```

Install only this skill:

```bash
npx skills add tokenaissance/fastagent-meta-skill --skill fastagent-meta-skill
```

Verify:

```bash
test -f ~/.agents/skills/fastagent-meta-skill/SKILL.md
python3 ~/.agents/skills/fastagent-meta-skill/scripts/validate_skill.py \
  ~/.agents/skills/fastagent-meta-skill
```

## Prerequisites

- [ ] Node.js 18+: `node --version`
- [ ] npx available: `npx --version`
- [ ] Python 3.11+ (PyYAML): `python3 --version && python3 -c "import yaml"`
- [ ] GitHub CLI installed and authenticated for publishing: `gh auth status`
- [ ] Network access to skills.sh, SkillsMP, and GitHub for search or publishing

## Built-in prior-art discovery

```bash
python3 scripts/research_prior_art.py \
  "<query 1>" "<query 2>" \
  --strict --summary \
  --output reports/prior-art-candidates.json
```

Underlying sources:

```bash
npx --yes skills find "<query>"
python3 scripts/search_skillsmp.py "<query>" --limit 20 --sort stars
```

Method: [Prior-Art Research](references/prior-art-research.md).

## Self-contained publishing

Audit only, no file or GitHub writes:

```bash
python3 scripts/publish_skill.py /path/to/skill --dry-run
```

Publish:

```bash
python3 scripts/publish_skill.py /path/to/skill
```

The publisher runs package validation, version consistency, secret scan, feature branch, PR checks, merge, GitHub Release, `npx skills add --list`, isolated install, and safe local sync.

- Never pushes `main/master` directly
- Never overwrites an already-released version
- Never swallows push or check failures
- Never destructively deletes an older local skill
- PR conflicts, pending/failed checks, or requested changes block auto-merge

CLI details: [Self-Contained Skill Publishing](references/publishing.md).

## Local quality checks

```bash
python3 scripts/validate_skill.py .
python3 scripts/export_skill_ir.py . --output reports/skill-ir.json
python3 scripts/trigger_eval.py . --cases evals/trigger_cases.json --output reports/trigger-eval.json
python3 scripts/release_check.py . --phase local --run-tests
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Recommended environment

The scripts require **Python 3.11+** (`scripts/search_skillsmp.py` uses `datetime.UTC`) and **PyYAML** (`scripts/validate_skill.py`). Ensure a single interpreter provides both, or the local gates will be split across interpreters.

```bash
python3 --version                    # must be 3.11+
python3 -c "import yaml"             # must not error
```

Once confirmed, run the local checks:

```bash
python3 scripts/validate_skill.py .
python3 scripts/release_check.py . --phase local --run-tests
```

## Troubleshooting

| Problem | Common cause | Fix |
|---|---|---|
| `No valid skills found` | Incomplete `SKILL.md` frontmatter or wrong nested entry | Run `scripts/validate_skill.py`; fix `name`, `description`, and the root entry |
| Skill misfires everywhere | Description too broad | Add should-not-trigger and near-neighbor cases; narrow the description |
| Skill never triggers | Natural user phrasing is not in the description | Add trigger words from real conversations, then rerun trigger eval |
| README reads like an internal spec | `SKILL.md` copied verbatim as README | Rewrite for value, install, phrasings, output, risks, and troubleshooting |
| Users cannot install after release | Only local validation, no public discovery or isolated install | Run the full publisher; do not treat a successful push as published |
| Publisher rejects a version | `vX.Y.Z` already exists | Bump the version; released versions are immutable |
| SkillsMP network down | Upstream chunked response or rate limiting | Let the unified runner retry and keep `missing evidence`; do not fabricate |

## Design philosophy: fork it, don't worship it

A skill should not be an unchangeable "correct answer". It is closer to compiling personal experience into source code an agent can execute. Install it, run one real task, then fork: delete the rules that are not yours, and add your own judgment, tools, style, eval, and publishing boundaries. A skill that increasingly resembles you is a skill that honors the idea of a skill.

## Credits and sources

- [`joeseesun/qiaomu-meta-skill`](https://github.com/joeseesun/qiaomu-meta-skill): this repository is a fork; upstream gate ladder, prior-art method, and self-contained publisher.
- [`yaojingang/yao-meta-skill`](https://github.com/yaojingang/yao-meta-skill): Skill IR, eval evidence, review, trust boundaries, and SkillOps method.
- [`anthropics/skills`](https://github.com/anthropics/skills): skill creation, iteration, and real eval practice.
- [`openai/skills`](https://github.com/openai/skills): progressive disclosure, degrees of freedom, and verifiable skill packaging.
- [`joeseesun/qiaomu-skill-publisher`](https://github.com/joeseesun/qiaomu-skill-publisher): README, license, and install verification; the capability is now built in safely.
- skills.sh, SkillsMP, and every open-source author studied in the prior-art reports.

The upstream author's public Codex skill history is preserved as lineage in [`reports/codex-skill-catalog.md`](reports/codex-skill-catalog.md); this fork credits it as upstream evidence rather than presenting it as its own product output.

Upstream ideas are adopted semantically with attribution, not mirrored wholesale; no private content or long verbatim passages are copied, and search popularity is never passed off as quality.

Upstream inspiration: https://github.com/joeseesun/qiaomu-meta-skill; https://github.com/yaojingang/yao-meta-skill; https://github.com/joeseesun/qiaomu-skill-publisher

## Security and evidence boundary

- Public candidates are read for metadata and source only; unvetted third-party scripts are never executed just to study them.
- API keys, cookies, tokens, private attachments, absolute paths, and raw conversations must not enter the public repository.
- Catalog install counts, repo stars, security audits, and licenses are recorded separately, never merged into a fake "best skill score".
- Without provider runs, human blind review, or user results, mark it `missing evidence` explicitly.
- Publishing is an external write; it runs only when explicitly requested, through a feature branch, PR, Release, and clean public install.

## License

MIT (see LICENSE for copyright holders).
