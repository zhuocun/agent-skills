# Agent operations brief

This repo is a collection of portable agent skills, distributed by symlink or by copy.

## What ships from this repo

Skills are the only product. Each skill is a directory at
`.agents/skills/<name>/SKILL.md` — that is the **canonical location**.
`.claude/skills` is a symlink to `.agents/skills` so Claude Code discovers the
skills when working inside this repo.

Local runtimes consume these skills by symlinking the directory into wherever
their runtime loads skills — every skill at once (`ln -s …/.agents/skills
~/.claude/skills`) or one skill at a time (`ln -s …/.agents/skills/<name>
~/.claude/skills/<name>`). See `README.md` for the exact clone-and-link steps;
don't duplicate them here.

The `agent` and `pulse` repos hold copies under their own `.agents/skills/`,
not symlinks. A merge here reaches them only when someone copies it over. Until then, their
weekly `skills-drift` check fails for each skill they hold that the merge changed.

`.claude/output-styles/baseline.md` mirrors `communicate`'s body under its own
frontmatter and H1, and `.claude/settings.json` makes it the active output style
(`Baseline`). Edit both files together; the validator fails when the bodies
differ.

`burst` and `proxy` share the Model selection table, the tier list, the source
order, and `references/cli-dispatch.md`, which each skill ships as an identical
copy. Change them together; the validator fails when the two copies differ.

| Surface | Source | Consumed by |
| --- | --- | --- |
| Skills | `.agents/skills/<name>/SKILL.md` | Claude Code (in-repo via the `.claude/skills` symlink), local runtimes (by symlink), and the `agent` and `pulse` repos (by copy) |

## Skill authoring conventions

Derived from the skills already in this repo (`burst`, `chinese-diction`,
`cr-fe`, `document-editor`, `status-report`):

- **One directory per skill**, and the directory name must equal the skill's
  `name` frontmatter field. The directory holds a `SKILL.md`, plus optional
  `references/` and `agents/` subdirectories when a skill needs them.
- **YAML frontmatter** with two required keys, `name` and a dense
  `description`; other keys are allowed. The
  description carries the routing triggers inline — a "Use when…" clause and,
  where the skill is easily over-applied, a "Do not use for…" clause (see
  `cr-fe`, `document-editor`, `chinese-diction`).
- **Keep the frontmatter YAML-safe.** When the `description` contains
  characters that could break strict parsers, use a folded `>-` block scalar
  rather than a bare string — `chinese-diction` does this and notes it in a
  Maintenance section.
- **Body pattern:** an `# H1` title, a one-paragraph statement of the skill's
  role, an explicit priority order where the work is ranked (e.g. `cr-fe`'s
  "runtime safety → … → layering", `status-report`'s "grounded evidence → … →
  fixed form"), the substance as numbered passes or failure modes
  (`cr-fe`'s review passes, `chinese-diction`'s seven failure modes), and a
  terminal `## Self-check` the agent runs before declaring done.
- **Write for an agent, not a human reader.** Skills are instructions a model
  follows; keep them imperative, concrete, and self-contained. Do not run the
  prose-editing skills (`chinese-diction`, `document-editor`) on SKILL.md files
  — they explicitly exclude agent-instruction files.

## Repo conventions

- **Branch names** for AI-authored work: `claude/<short-topic>`.
- **Commits**: imperative subject; concise body explaining *why*; footer
  `https://claude.ai/code/session_<id>`. Never include AI model identifiers in
  commits, PR titles/bodies, or code comments.

## Claude Code auto-compact (`.claude/settings.json`)

`.claude/settings.json` pins `autoCompactWindow: 400000` and
`env.CLAUDE_AUTOCOMPACT_PCT_OVERRIDE: "80"`, so auto-compaction fires at 80% of a
400K window (~320K tokens) instead of the model's full 1M default. The percentage
override has no settings key — it only takes effect from the `env` block — and is
clamped by `Math.min` to the default, so it can pull compaction *earlier* but
never later. Verified on Claude Code 2.1.173; older builds ignored the override on
1M-context Opus and compacted at a hardcoded ~195K. To re-verify, read an
auto-compact event's `preTokens` in the session `.jsonl`: ~320K means it works,
~195K means it regressed.

## PR & merge process

The same review-and-merge flow applies across the `agent`, `pulse`, and `agent-skills` repos.

- **One concern per PR.** Keep PRs small and single-purpose, and squash-merge to keep `main` history clean. A larger change ships as a single PR only when its commits share one integration story — one logical commit per concern.
- **Watch CI, then merge on green.** After opening a PR, watch its checks (subscribe to PR activity, or poll the check runs). Once all required checks pass, squash-merge. If CI goes red, push a fix rather than leaving it stranded. A PR-activity subscription only wakes on *failures* and review comments — a green pass emits no event, so confirm success by polling the checks, not by waiting to be notified. Here, merging `main` publishes the canonical skills: symlinked consumers pick them up on their next pull, copied consumers (agent, pulse) only after a manual copy, and the skills-drift checks in agent and pulse compare against `main`. Green CI is the merge gate.
- **Never bypass hooks.** Don't use `--no-verify` / `--no-gpg-sign`, especially on workflow-file changes. If a commit-msg or pre-commit hook fails, fix the cause and make a new commit — don't amend past it.

> CI for this repo is the `validate-skills` workflow (`.github/workflows/validate-skills.yml`),
> which runs `python3 scripts/validate_skills.py` on every pull request and on every push to
> `main`. A push to a branch with no pull request open is not validated. It enforces the
> authoring conventions above mechanically: every skill directory has a `SKILL.md`, the
> frontmatter parses as a YAML mapping, `name` and `description` are present and non-empty,
> `name` equals the directory name, the body opens with an `# ` H1, the body carries a
> `## Self-check` section, and `.claude/skills` still resolves to `.agents/skills`.
> Frontmatter keys beyond those two are allowed. It also runs `output-style-mirror`: below
> the frontmatter, the H1 and the one blank line after it, `.claude/output-styles/baseline.md`
> must equal `communicate/SKILL.md` line for line, trailing blank lines included. And it runs
> `shared-reference-identical`: the `burst` and `proxy` copies of `references/cli-dispatch.md`
> must be byte-identical. Run the same command locally before pushing.
