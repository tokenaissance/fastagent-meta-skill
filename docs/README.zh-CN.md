# fastagent-meta-skill 中文介绍

> 研究、创建、改进、迁移、评估、打包、安装检查、治理并安全发布 fastagent agent skill，输入可以是工作流、提示词、对话记录、文档、SOP、runbook、脚本或笔记。

[![English](https://img.shields.io/badge/Docs-English-black)](../README.md)
[![中文](https://img.shields.io/badge/Docs-%E4%B8%AD%E6%96%87-red)](README.zh-CN.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](../LICENSE)

`fastagent-meta-skill` 构建可复用的 FastAgent skill 包，而不是长提示词。它把「把这个流程做成 Skill」变成真正能被发现、能稳定触发、能通过验证、还能安全发布的 Skill。

把提示词、SOP、对话记录、旧 Skill、脚本或一个模糊想法交给 Agent：

```text
用 fastagent 元 Skill，把这套工作流做成一个可复用的 Skill；
先研究同类热门 Skill，完成触发评测和安全检查，然后发布到 GitHub。
```

它会自己完成：**需求收敛 → 同类检索 → 提炼 keep/adapt/reject/invent → Skill 设计 → 触发评测 → 包校验 → README → Secret 扫描 → PR → Release → npx 安装验证**。

**v2.8.1 本地候选已验证：** 33/33 单元测试、23/23 触发评测、0 个包校验问题。公开发布证据以 [Releases](https://github.com/tokenaissance/fastagent-meta-skill/releases) 为准。

## 为什么做这个

Skill 正在变成 Agent 时代真正可复用的软件单元，但「写一份 `SKILL.md`」离一个好用的 Skill 还很远：

- 描述写得太宽，会到处误触发；写得太窄，又永远叫不出来。
- 把一段长 Prompt 换个文件名，不会自动变成可靠工作流。
- 不研究已有方案，很容易重复造一个更差的轮子。
- 本地能跑，不代表别人能安装，更不代表可以安全发布。
- README、许可证、版本、密钥泄露、PR、Release 和安装证明，经常在最后一步一起失控。

Anthropic 与 OpenAI 的官方 `skill-creator` 奠定了很好的基础。本元 Skill 在此之上补齐了实际做几十个 Skill 时最需要的一段：**先搜索再创造、用证据控制质量，并把成品安全发布给别人使用。**

初始方法来自搭档姚老师的 [`yaojingang/yao-meta-skill`](https://github.com/yaojingang/yao-meta-skill)。我们继续研究并整合公开的 Agent Skill 最佳实践，随后加入双目录检索、GitHub 验源、证据感知的发布门禁与自包含发布能力。

## 它比普通 Skill 创建器多做什么

| 能力 | 普通「生成 SKILL.md」 | fastagent-meta-skill |
|---|---:|---:|
| 从 Prompt / SOP / 对话 / 旧 Skill 提炼工作流 | ✓ | ✓ |
| 先搜索 skills.sh 与 SkillsMP 的相关 Skill | | ✓ |
| 回到 GitHub 核对来源、维护、安全与许可证 | | ✓ |
| 记录 `keep / adapt / reject / invent`，避免拼贴抄袭 | | ✓ |
| 测试该触发与不该触发的真实说法 | 视实现而定 | ✓ |
| 区分设计优势、已验证优势和待验证假设 | | ✓ |
| 校验目录、版本、上下文预算与递归发现 | | ✓ |
| 准备 README 与 MIT License | | ✓ |
| Secret / API 泄露扫描 | | ✓ |
| 功能分支、PR、检查、Release | | ✓ |
| `npx skills add` 公开发现与隔离安装验证 | | ✓ |

它不是让 Skill 变得更重，而是让复杂度与风险匹配：个人试验走轻量 `Scaffold` 门禁，公开发布才启用完整 `Governed` 门禁。

## 你可以直接这样说

- 「把这个提示词升级成一个可以给团队复用的 Skill。」
- 「采访我，把这套隐性工作方法整理成 Skill；每次只问一个关键问题。」
- 「先搜索同类热门 Skill，分析优缺点，再做一个不抄袭的版本。」
- 「优化这个已有 Skill 的触发率、准确性和指令遵循。」
- 「审计这个 Skill，只给问题和建议，先不要修改文件。」
- 「把这个 Skill 发布到 GitHub，生成 npx 安装命令并验证别人能装。」

## 它到底会产出什么

根据场景复杂度，元 Skill 会创建必要而非礼仪性的文件：

```text
your-skill/
├── SKILL.md                    # Agent 路由与最小执行骨架
├── README.md                   # 给人看的产品页
├── LICENSE                     # 默认 MIT
├── manifest.json               # 版本、作者、平台与门禁
├── agents/interface.yaml       # 跨 Agent 接口
├── references/                 # 长方法、判断与安全边界
├── scripts/                    # 可重复验证与确定性工具
├── evals/trigger_cases.json    # 应触发、不应触发、近邻场景
└── reports/                    # Skill IR、研究、评测与发布证据
```

个人试验不会被迫拥有整套目录；公开、高风险或团队复用的 Skill 才会逐级增加门禁。

## 一套完整工作流

1. **Intent**：确认重复任务、目标用户、输入、输出、边界与成功标准。
2. **Search**：用 2–4 组意图关键词查询 skills.sh 与 SkillsMP，再回到 GitHub 验源。
3. **Synthesis**：记录每个候选的 `keep / adapt / reject / invent`，明确原创贡献。
4. **Package**：写精简 `SKILL.md`，把长判断放进 references，把确定性动作放进 scripts。
5. **Eval**：先测触发边界；风险需要时再补输出、运行时或人工评测。
6. **Release**：检查版本、README、许可证、秘密信息与安装入口，经功能分支和 PR 发布。
7. **Verify**：创建 Release，确认远端默认分支，并在隔离环境完成公开安装。

## 在 FastAgent 中运行

当本 Skill 运行在 FastAgent Agent 中时，新 Skill 必须用 `write_file` 的 `skills/<name>/` 路径前缀持久化。运行时会把该前缀路由到每个用户的技能目录（`~/.fastagent/users/<userId>/skills/<name>/`），下一轮的技能扫描会发现它，并镜像到工作区存储供云端 Pod 使用。任何其他路径都会落到没有任何发现机制的工作区文件夹。

```text
✅ write_file(path="skills/domain-check/SKILL.md", content=...)
❌ write_file(path="domain-check/SKILL.md", ...)   # 会落到 /workspace
```

新 Skill 要到**下一轮对话**才对 LLM 可见，而不是本轮中途。

## 安装与验证

```bash
npx skills add tokenaissance/fastagent-meta-skill
```

只安装这个 Skill：

```bash
npx skills add tokenaissance/fastagent-meta-skill --skill fastagent-meta-skill
```

验证：

```bash
test -f ~/.agents/skills/fastagent-meta-skill/SKILL.md
python3 ~/.agents/skills/fastagent-meta-skill/scripts/validate_skill.py \
  ~/.agents/skills/fastagent-meta-skill
```

## 前置条件

- [ ] Node.js 18+：`node --version`
- [ ] npx 可用：`npx --version`
- [ ] Python 3.11+（含 PyYAML）：`python3 --version && python3 -c "import yaml"`
- [ ] 发布到 GitHub 时安装并登录 GitHub CLI：`gh auth status`
- [ ] 搜索或发布时允许访问 skills.sh、SkillsMP 与 GitHub

## 内置搜索

```bash
python3 scripts/research_prior_art.py \
  "<query 1>" "<query 2>" \
  --strict --summary \
  --output reports/prior-art-candidates.json
```

底层数据源：

```bash
npx --yes skills find "<query>"
python3 scripts/search_skillsmp.py "<query>" --limit 20 --sort stars
```

详细方法见 [`references/prior-art-research.md`](../references/prior-art-research.md)。

## 自包含发布

只检查，不改文件、不写 GitHub：

```bash
python3 scripts/publish_skill.py /path/to/skill --dry-run
```

正式发布：

```bash
python3 scripts/publish_skill.py /path/to/skill
```

发布器会依次执行包验证、版本一致性、secret scan、功能分支、PR 检查、合并、GitHub Release、`npx skills add --list`、隔离安装和本地安全同步。

- 不直接推送 `main/master`
- 不覆盖已经发布的同版本 Release
- 不吞掉 push 或检查失败
- 不破坏性删除旧的本地 Skill
- PR 冲突、未完成/失败检查或 requested changes 会阻断自动合并

完整参数见 [`references/publishing.md`](../references/publishing.md)。

## 本地质量检查

```bash
python3 scripts/validate_skill.py .
python3 scripts/export_skill_ir.py . --output reports/skill-ir.json
python3 scripts/trigger_eval.py . --cases evals/trigger_cases.json --output reports/trigger-eval.json
python3 scripts/release_check.py . --phase local --run-tests
python3 -m unittest discover -s tests -p 'test_*.py'
```

## 推荐环境

脚本需要 **Python 3.11+**（`scripts/search_skillsmp.py` 使用 `datetime.UTC`）和 **PyYAML**（`scripts/validate_skill.py`），所以必须用同时满足两者的解释器，否则本地门禁会被拆到多个解释器里。macOS 默认 `python3` 可能是 3.9（没有 `datetime.UTC`），独立的 `python3.13` 又可能缺 PyYAML；用带 Python 3.11+ 和 PyYAML 的 conda 环境可以避免这个问题。本机 `google` conda 环境同时具备：

```bash
conda run -n google python --version                                   # Python 3.13.11
conda run -n google python -c "import yaml; print(yaml.__version__)"   # 6.0.3
```

用同一个解释器跑本地检查，例如：

```bash
conda run -n google python scripts/validate_skill.py .
conda run -n google python scripts/release_check.py . --phase local --run-tests
```

## 常见问题 / Troubleshooting

| 问题 | 常见原因 | 处理方式 |
|---|---|---|
| `No valid skills found` | `SKILL.md` frontmatter 不完整或嵌套入口错误 | 运行 `scripts/validate_skill.py`，修正 `name`、`description` 与根入口 |
| Skill 到处误触发 | description 太泛 | 补 should-not-trigger 与 near-neighbor 用例，收窄描述 |
| Skill 永远不触发 | 用户自然说法没有进入 description | 从真实对话补触发词，再跑 trigger eval |
| README 像内部说明书 | 把 `SKILL.md` 直接复制成 README | 重写成价值、安装、说法、输出、风险与排错 |
| 发布后别人装不上 | 只验证本地目录，没有公开发现和隔离安装 | 完整运行发布器，不把 push 成功当作发布完成 |
| 发布器拒绝版本 | `vX.Y.Z` 已存在 | 提升版本；已发布版本不可覆盖 |
| SkillsMP 网络中断 | 上游分块响应或限流 | 让统一研究器重试并保留 `missing evidence`，不要编造结果 |

## 设计哲学：Fork 它，而不是膜拜它

Skill 不应该是一套不可修改的「标准答案」。它更像把个人经验编译成 Agent 可以执行的源代码。

建议先安装、跑一个真实任务，然后 fork：删除不属于你的规则，加入你自己的判断、工具、风格、评测与发布边界。一个越来越像你的 Skill，才真正符合 Skill 的理念。

## 致谢与来源

- [`joeseesun/qiaomu-meta-skill`](https://github.com/joeseesun/qiaomu-meta-skill)：本仓库的 fork 上游；门禁阶梯、先例研究法与自包含发布器。
- [`yaojingang/yao-meta-skill`](https://github.com/yaojingang/yao-meta-skill)：Skill IR、评测证据、Review、信任边界与 SkillOps 方法。
- [`anthropics/skills`](https://github.com/anthropics/skills)：Skill 创建、迭代与真实评测实践。
- [`openai/skills`](https://github.com/openai/skills)：渐进披露、自由度与可验证的 Skill 打包方法。
- [`joeseesun/qiaomu-skill-publisher`](https://github.com/joeseesun/qiaomu-skill-publisher)：README、License 与安装验证；其能力现已安全内建。
- skills.sh、SkillsMP 与所有在 prior-art 报告中被研究的开源作者。

上游思想以语义方式吸收并保留归因，不整库镜像，不复制私有内容或长段表述，也不把搜索热度冒充质量。

Upstream inspiration: https://github.com/joeseesun/qiaomu-meta-skill; https://github.com/yaojingang/yao-meta-skill; https://github.com/joeseesun/qiaomu-skill-publisher

## 安全与证据边界

- 公开候选只读取元数据与源码，不会为了学习而执行未经审查的第三方脚本。
- API key、Cookie、Token、私有附件、绝对路径和原始对话不得进入公开仓库。
- 目录安装量、仓库 stars、安全审计和许可证分别记录，不合并为「最佳 Skill 分数」。
- 没有 provider 实跑、人工盲评或用户结果时，必须明确标记 `missing evidence`。
- 发布是外部写操作，只有明确要求时才执行，并通过功能分支、PR、Release 与公开安装验证。

## 许可证

MIT（版权持有者见 LICENSE）。
