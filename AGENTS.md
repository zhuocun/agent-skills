# Agent operations brief

This repo is a collection of portable agent skills distributed by symlink.

## What ships from this repo

Skills are the only product. Each skill is a directory at
`.agents/skills/<name>/SKILL.md` — that is the **canonical location**.
`.claude/skills` is a symlink to `.agents/skills` so Claude Code discovers the
skills when working inside this repo.

Other repos consume these skills by symlinking the directory into wherever their
runtime loads skills — every skill at once (`ln -s …/.agents/skills
~/.claude/skills`) or one skill at a time (`ln -s …/.agents/skills/<name>
~/.claude/skills/<name>`). See `README.md` for the exact clone-and-link steps;
don't duplicate them here.

| Surface | Source | Consumed by |
| --- | --- | --- |
| Skills | `.agents/skills/<name>/SKILL.md` | Claude Code (in-repo via the `.claude/skills` symlink) and other repos (by symlink) |

## Skill authoring conventions

Derived from the skills already in this repo (`burst`, `chinese-diction`,
`cr-fe`, `document-editor`):

- **One directory per skill**, and the directory name must equal the skill's
  `name` frontmatter field. The directory holds a `SKILL.md`, plus optional
  `references/` and `agents/` subdirectories when a skill needs them.
- **YAML frontmatter** with two keys: `name`, and a dense `description`. The
  description carries the routing triggers inline — a "Use when…" clause and,
  where the skill is easily over-applied, a "Do not use for…" clause (see
  `cr-fe`, `document-editor`, `chinese-diction`).
- **Keep the frontmatter YAML-safe.** When the `description` contains
  characters that could break strict parsers, use a folded `>-` block scalar
  rather than a bare string — `chinese-diction` does this and notes it in a
  Maintenance section.
- **Body pattern:** an `# H1` title, a one-paragraph statement of the skill's
  role, an explicit priority order where the work is ranked (e.g. `cr-fe`'s
  "runtime safety → … → layering", `burst`'s orchestrator → worker → reviewer →
  orchestrator chain), the substance as numbered passes or failure modes
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

## PR & merge process

The same review-and-merge flow applies across the `agent`, `pulse`, and `agent-skills` repos.

- **One concern per PR.** Keep PRs small and single-purpose, and squash-merge to keep `main` history clean. A larger change ships as a single PR only when its commits share one integration story — one logical commit per concern.
- **Open a PR before wrapping up.** A task isn't finished until its changes are up for review; don't leave finished work stranded on a pushed branch with no PR. Check for an existing PR on the branch first. If that branch's earlier PR has already merged, branch off fresh `main` and open a new PR rather than pushing onto the dead branch.
- **Watch CI, then merge on green.** After opening a PR, watch its checks (subscribe to PR activity, or poll the check runs). Once all required checks pass, squash-merge. If CI goes red, push a fix rather than leaving it stranded. A PR-activity subscription only wakes on *failures* and review comments — a green pass emits no event, so confirm success by polling the checks, not by waiting to be notified. Merging `main` triggers the production deploy, so green CI is the merge gate.
- **Never bypass hooks.** Don't use `--no-verify` / `--no-gpg-sign`, especially on workflow-file changes. If a commit-msg or pre-commit hook fails, fix the cause and make a new commit — don't amend past it.

> Note: `agent-skills` has no CI yet, so "merge on green" reduces to "merge after review" until CI is added.
