# Agent Skills

Personal agent skills that can be installed or linked into a local agent runtime.

Skills are canonical under `.agents/skills/` (one directory per skill). `.claude/skills`
is a symlink to that directory, so Claude Code discovers the skills when working inside
this repo.

## Skills

- `burst` — orchestrates parallel subagents for research, audit, implementation, and review work.
- `proxy` — acts as a thin proxy that delegates every decision and unit of work — including decomposition and the done/not-done call — to top-tier subagents.
- `document-editor` — authors, edits, and reviews formal human-facing documents at the document level without changing their meaning.
- `chinese-diction` — writes, translates, and polishes Chinese at the word, phrase, and register level for professional, casual, or creative targets.
- `cr-fe` — comprehensive frontend code review for runtime safety, security and data integrity, error handling, hook correctness, type honesty, code smell, and folder-structure layering.
- `reorient` — reconstructs and verifies working context after a context compaction, then resumes the in-progress task safely.
- `communicate` — governs how the agent writes to the user: message shape, register, and the evidence behind claims. Its body is mirrored as the `Baseline` output style in `.claude/output-styles/baseline.md`.
- `status-report` — produces a one-page project status report with fixed slots for a reader who was not watching the work.
- `visual-ux-sweep` — reviews UI and UX regressions, and fixes them when asked, from headless-browser screenshots across routes, viewports, themes, and interaction states.

## Layout

```
.agents/skills/   canonical skill sources (one directory per skill)
.claude/skills    symlink -> .agents/skills (so Claude Code finds them in this repo)
```

## Local Use

Clone the repo, then point your local skills folder at the canonical directory:

```bash
git clone git@github.com:zhuocun/agent-skills.git

# Link every skill at once (when ~/.claude/skills does not already exist):
ln -s "$(pwd)/agent-skills/.agents/skills" ~/.claude/skills

# Or link individual skills into an existing folder:
ln -s "$(pwd)/agent-skills/.agents/skills/cr-fe" ~/.claude/skills/cr-fe
```

Swap `~/.claude/skills` for `~/.agents/skills` if that is where your runtime loads skills.
If a skill or folder with the same name already exists, move it aside before creating the symlink.
