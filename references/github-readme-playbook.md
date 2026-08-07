# GitHub README Playbook

Use this when creating, refactoring, or publishing a skill. The README is the
public product page for humans; `SKILL.md` is the runtime instruction file for
agents. Do not dump internal agent rules into the README.

## Canonical Template

**`fastagent-meta-skill/README.md` is the reference template for all derived
skill READMEs.** When building a new skill, open this repo's own README and
follow its structure, tone, and section ordering. The sections below describe
that format in detail.

## README Goal

The README should make a stranger quickly answer:

1. What problem does this solve for me?
2. What will I get after installing it?
3. How do I install and verify it?
4. What can I say to trigger it?
5. What can go wrong, and how do I fix it?

## Required Section Order

Follow `fastagent-meta-skill/README.md` as the canonical example. The section
order is:

```markdown
# skill-name

> 一句话痛点/价值主张。

[badges: Release, Stars, Last commit, License, language switcher(s)]

## 为什么值得用 / Why I built this
## 能力对比 / What makes it more than X
## 你可以这样说 / Natural-language examples
## 它会做什么 / What it produces
## 完整工作流 / One complete workflow
## 安装 / Installation
## 前置条件 / Prerequisites
## [feature-specific sections — CLI demos, config, etc.]
## 推荐环境 / Recommended environment
## Troubleshooting
## 设计哲学 / Design philosophy
## 致谢 / Credits and sources
## 安全与证据边界 / Security and evidence boundary
## License
```

Keep the first screen focused: hook, badges, install, natural-language examples,
and one concrete output preview. Long architecture notes belong later.

## Must-Have Checklist

- [ ] First sentence describes the user's pain or desired outcome, not the
      implementation.
- [ ] Badge row: Release, Stars, Last commit, License, and language switchers
      when multi-language READMEs exist. Follow `fastagent-meta-skill/README.md`
      badge format.
- [ ] One-line install command appears near the top:
      `npx skills add owner/repo`.
- [ ] Capability comparison table (feature vs “plain X” vs “this skill”) when
      the skill replaces or improves an existing approach.
- [ ] 3-5 natural-language trigger examples show what a user would actually say.
- [ ] Directory tree shows what the skill produces after installation.
- [ ] Numbered workflow steps (ideally 7 or fewer) describe the end-to-end flow.
- [ ] Prerequisites use checkbox format and include verification commands.
- [ ] Output section shows concrete files, API calls, screenshots, or snippets.
- [ ] Configuration section lists environment variables without secrets.
- [ ] Troubleshooting has at least 3 rows: symptom, cause, fix.
- [ ] Risks and side effects are explicit for credentials, writes, costs, network
      calls, publishing, destructive actions, or account automation.
- [ ] Design philosophy section explains the “why” behind key decisions.
- [ ] Third-party tools and upstream projects are credited with links.
- [ ] Security/evidence boundary section covers what is and is not committed,
      how third-party sources are handled, and what counts as evidence.
- [ ] README does not expose private domains, tokens, cookies, VPS paths, or
      user-specific absolute paths unless the skill is explicitly private.

## Language Decision

For public GitHub skills backed by a Tokenaissance repo, default to
English-primary with a Chinese translation at `docs/README.zh-CN.md`. Use
language-switch badges matching `fastagent-meta-skill/README.md`. For purely
internal or Chinese-audience-only skills, Chinese-primary is acceptable.

## Web Or Visual Project Extras

If a skill ships a website, visual tool, or generated media experience, README
must include:

- product screenshot near the first screen, preferably `docs/assets/product-screenshot.png`
- live demo or deploy button when available
- screenshot capture command such as `npm run capture:screenshots`
- example gallery or before/after output

Do not publish a visual project README without screenshots unless the user
explicitly asks for a minimal private package.

## Writing Rules

- Prefer short paragraphs and concrete examples.
- Start with user value, not architecture.
- Put prerequisites after the install/use examples unless missing credentials
  would be dangerous or expensive.
- Use natural-language examples instead of only CLI commands.
- Keep internal agent constraints out of README unless they affect users.
- If the skill is open source, replace private values with placeholders:
  `https://your-site.example`, `YOUR_TOKEN`, `OWNER/REPO`.
- Reference `fastagent-meta-skill/README.md` when unsure about a section's
  tone, depth, or placement.

## Bad Smells

- README is just `SKILL.md` pasted into Markdown.
- First paragraph says “This skill uses...” instead of “You can...”.
- No install command.
- No examples of what to say to the agent.
- Missing capability comparison table when the skill replaces an existing tool
  or workflow.
- No badges or broken badge URLs.
- Private hostnames, passwords, cookies, or local paths appear in public docs.
- Troubleshooting is missing.
- No credits/attribution for upstream projects.
- No security/evidence boundary section.
- Web/UI project has no screenshot.
