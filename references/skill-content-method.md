# Skill Content Method

How to write skills that are well-scoped, calibrated, and grounded in real
expertise. Use when authoring or reviewing `SKILL.md` body content, references,
and supporting assets.

## Start from real expertise

Do not ask an LLM to generate a skill from general training knowledge — the
result is vague, generic procedures ("handle errors appropriately," "follow
best practices") instead of the specific API patterns, edge cases, and
project conventions that make a skill valuable.

### Extract from a hands-on task

Complete a real task in conversation, then extract the reusable pattern. Pay
attention to:

- **Steps that worked** — the sequence of actions that led to success.
- **Corrections the user made** — places where they steered the approach
  ("use library X instead of Y," "check for edge case Z").
- **Input/output formats** — what the data looked like going in and coming out.
- **Context the user provided** — project-specific facts, conventions, or
  constraints the agent didn't already know.

### Synthesize from project artifacts

Good source material for synthesizing a skill:

- Internal documentation, runbooks, and style guides
- API specifications, schemas, and configuration files
- Code review comments and issue trackers
- Version control history, especially patches and fixes
- Real-world failure cases and their resolutions

Project-specific artifacts produce skills that capture *your* schemas, failure
modes, and recovery procedures — not generic advice.

## Refine with real execution

Run the skill against real tasks, then feed the results — all of them, not
just failures — back into the creation process. Ask:

- What triggered false positives?
- What was missed?
- What could be cut?

Read agent execution traces, not just final outputs. If the agent wastes
time on unproductive steps, common causes:

- Instructions too vague (agent tries several approaches before finding one)
- Instructions that don't apply to the current task (agent follows them anyway)
- Too many options presented without a clear default

For a structured approach to iteration with test cases and grading, see
[Eval Playbook](eval-playbook.md) and [Output Eval Method](output-eval-method.md).

## Spending context wisely

Every token in a skill competes for the agent's attention with conversation
history, system context, and other active skills.

### Add what the agent lacks, omit what it knows

Focus on what the agent *wouldn't* know without the skill: project-specific
conventions, domain-specific procedures, non-obvious edge cases, and the
particular tools or APIs to use. Don't explain general concepts the agent
already understands.

Ask about each piece of content: **"Would the agent get this wrong without
this instruction?"** If no, cut it.

### Design coherent units

A skill should encapsulate a coherent unit of work. Too narrow — multiple
skills must load for one task, risking overhead and conflicts. Too broad —
hard to activate precisely.

### Aim for moderate detail

Overly comprehensive skills can hurt more than they help. The agent struggles
to extract what's relevant and may pursue unproductive paths. Concise,
stepwise guidance with a working example tends to outperform exhaustive
documentation.

### Structure large skills with progressive disclosure

Keep `SKILL.md` lean — core instructions the agent needs on every run. Move
detailed reference material to `references/` and tell the agent *when* to
load each file:

```markdown
Read `references/api-errors.md` if the API returns a non-200 status code.
```

This is more useful than a generic "see references/ for details."

## Calibrating control

Match the specificity of instructions to the fragility of the task.

### Match specificity to fragility

**Give the agent freedom** when multiple approaches are valid and the task
tolerates variation. Explain *why* — an agent that understands the purpose
behind an instruction makes better context-dependent decisions.

**Be prescriptive** when operations are fragile, consistency matters, or a
specific sequence must be followed. Use exact commands and forbid variation:

```
## Database migration

Run exactly this sequence:

python scripts/migrate.py --verify --backup

Do not modify the command or add additional flags.
```

### Provide defaults, not menus

When multiple tools or approaches could work, pick a default and mention
alternatives briefly rather than presenting them as equal options:

```markdown
Use pdfplumber for text extraction. For scanned PDFs requiring OCR,
fall back to pdf2image with pytesseract instead.
```

### Favor procedures over declarations

Teach the agent *how to approach* a class of problems, not *what to produce*
for a specific instance. A reusable method might describe reading a schema,
joining on conventions, applying user filters, and formatting output — rather
than a single hardcoded SQL query. The *approach* should generalize even when
individual details are specific.

## Reusable patterns

These are tested techniques for structuring skill content. Not every skill
needs all of them — use the ones that fit.

### Gotchas sections

The highest-value content in many skills is a list of gotchas —
environment-specific facts that defy reasonable assumptions:

```markdown
## Gotchas

- The `users` table uses soft deletes. Always include
  `WHERE deleted_at IS NULL`.
- `user_id` in DB = `uid` in auth = `accountId` in billing.
- `/health` returns 200 even if the DB is down. Use `/ready` instead.
```

Keep gotchas in `SKILL.md` where the agent reads them before encountering
the situation. When you correct an agent's mistake, add the correction to
gotchas — this is one of the most direct ways to improve a skill iteratively.

### Templates for output format

When output must follow a specific format, provide a template. Agents
pattern-match well against concrete structures. Short templates live inline
in `SKILL.md`; longer ones go in `assets/` with a reference from `SKILL.md`.

### Checklists for multi-step workflows

An explicit checklist helps the agent track progress and avoid skipping
steps, especially when steps have dependencies:

```markdown
## Workflow

Progress:
- [ ] Step 1: Analyze (run `scripts/analyze.py`)
- [ ] Step 2: Map fields (edit `fields.json`)
- [ ] Step 3: Validate (run `scripts/validate.py`)
- [ ] Step 4: Execute (run `scripts/execute.py`)
```

### Validation loops

Instruct the agent to validate its own work before moving on: do the work,
run a validator (script, checklist, or self-check), fix issues, and repeat
until validation passes.

```markdown
1. Make your edits
2. Run `python scripts/validate.py output/`
3. If validation fails, review errors, fix, and re-run
4. Only proceed when validation passes
```

### Plan-validate-execute

For batch or destructive operations, create an intermediate plan in a
structured format, validate it against a source of truth, and only then
execute. The key ingredient is a validation step that catches errors
before they cause damage — and gives the agent enough information to
self-correct.

### Bundling reusable scripts

When the agent independently reinvents the same logic each run (building
charts, parsing a format, validating output), write a tested script once
and bundle it in `scripts/`. This improves determinism and saves context.
