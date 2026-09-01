# FastAgent Runtime Skill Guide — target-platform conformance standard

Source of truth: `fastagent/skills/fastagent-skill-guide/SKILL.md` in the
`tokenaissance/fastagent` runtime repo. This is the standard the FastAgent
SkillsLoader actually parses, so any package whose `target_platforms` includes
`fastagent` must satisfy it before release. Keep this file in sync with the
runtime guide when either changes.

## Skill Structure

```
skill-name/
├── SKILL.md          # Required — skill instructions
├── scripts/          # Optional — executable scripts for deterministic tasks
├── references/       # Optional — docs loaded into context as needed
└── assets/           # Optional — templates, icons, fonts
```

## SKILL.md Format

Use YAML frontmatter followed by markdown instructions:

```markdown
---
name: My Skill Name
description: One-line description of what this skill does and when to use it
homepage: https://example.com
metadata:
  fastagent:
    emoji: "🔧"
    always: false
    os: ["darwin", "linux"]
    requires:
      bins: ["git"]
      anyBins: ["python3", "python"]
      env: ["API_KEY"]
    primaryEnv: "API_KEY"
---

# Skill Title

Step-by-step instructions in markdown...
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Human-readable skill name |
| `description` | Yes | Brief description — this is the primary trigger mechanism |
| `homepage` | No | URL for more info |
| `metadata.fastagent.emoji` | No | Display icon |
| `metadata.fastagent.always` | No | If true, full content is always in system prompt |
| `metadata.fastagent.os` | No | OS requirements (darwin, linux, windows) |
| `metadata.fastagent.requires.bins` | No | All listed binaries must exist on PATH |
| `metadata.fastagent.requires.anyBins` | No | At least one must exist |
| `metadata.fastagent.requires.env` | No | Required environment variables |
| `metadata.fastagent.primaryEnv` | No | Maps config apiKey to this env var |

Note: `metadata.openclaw` is also supported for backward compatibility with
OpenClaw skills. The loader also accepts `metadata.fastclaw` and falls back
`fastagent` → `fastclaw` → `openclaw`.

### Writing the Description

The description determines whether the agent loads this skill. Make it
specific and slightly "pushy" — include both what the skill does AND contexts
where it should trigger.

Bad: `"Format data"`
Good: `"Format CSV and Excel data into clean tables. Use whenever the user mentions spreadsheets, data formatting, column alignment, CSV cleanup, or tabular output."`

## Where Skills Are Stored

Skills are discovered from multiple directories in precedence order (higher
overrides lower):

1. **Agent workspace** — `{agentDir}/skills/` — skills specific to this agent
2. **Team** — `{teamDir}/skills/` — shared within a team
3. **User installed** — `~/.fastagent/skills/` — user-level skills
4. **OpenClaw compatible** — `~/.openclaw/skills/` — installed via OpenClaw
5. **System bundled** — npm global locations
6. **Extra dirs** — configured in `fastagent.json`

The loader key is the **directory name**; the frontmatter `name` is
informational. `~/.agents/skills/` is **not** scanned by FastAgent — the
`npx skills add` default target is invisible to it. For FastAgent, install to
the user layer (`~/.fastagent/skills/<name>/`) or the per-user bucket
(`~/.fastagent/users/<uid>/skills/<name>/`).

## Three-Level Loading

Skills use progressive disclosure:

1. **Metadata** (name + description) — Always in system prompt context (~100 words)
2. **SKILL.md body** — Loaded when agent calls `load_skill` (<500 lines ideal)
3. **Bundled resources** — Loaded on demand via file tools (unlimited size)

Keep SKILL.md under 500 lines. If approaching the limit, move detailed content
to `references/` with clear pointers.

The loader substitutes `{baseDir}` with the absolute skill directory when a
skill loads, so reference files within the skill can be addressed with the
`{baseDir}` token.

## Gating

`metadata.fastagent.os`, `requires.bins`, `requires.anyBins`, and
`requires.env` are evaluated against the host at discovery. A gated skill
stays visible in the catalog with the missing-requirement reason (so the agent
can explain it) but is not available for invocation. `always: true` bypasses
gating.

## Writing Guidelines

- Use imperative form in instructions ("Run the command", not "You should run the command")
- Explain **why** things are important, not just what to do
- Include examples for output formats
- Use `{baseDir}` token to reference files within the skill directory — it gets replaced with the absolute path at load time
- Avoid heavy MUST/NEVER language — explain reasoning so the agent can handle edge cases

## Applying during packaging

When this package is used to create or wrap a skill whose
`target_platforms` includes `fastagent`:

1. Ensure the root `SKILL.md` frontmatter has at least `name` + `description`,
   and add `metadata.fastagent` (`emoji`, `requires.anyBins` for the runtime's
   interpreter/tooling) so discovery, gating, and the admin UI behave.
2. Keep the root `SKILL.md` under 500 lines; push depth into `references/`.
3. Prefer `{baseDir}`-relative references so the skill works both inside the
   FastAgent loader and on generic hosts.
4. Document the FastAgent install path (`~/.fastagent/skills/<name>/`), not
   the `~/.agents/skills` default, in the README install section.
