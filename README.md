# Agent Skills

Personal agent skills that can be installed or linked into a local agent runtime.

Skills are canonical under `.agents/skills/` (one directory per skill). `.claude/skills`
is a symlink to that directory, so Claude Code discovers the skills when working inside
this repo.

## Skills

- `burst` — orchestrates parallel subagents for research, audit, implementation, and review work.
- `proxy` — acts as a thin proxy that delegates every decision and unit of work — including decomposition and the done/not-done call — to frontier-model subagents.
- `document-editor` — edits formal human-facing documents at the document level without changing their meaning.
- `chinese-diction` — improves Chinese word choice, phrasing, and register for natural professional prose.
- `cr-fe` — comprehensive frontend code review for runtime safety, error handling, hook correctness, code smell, and folder-structure layering.
- `reorient` — reconstructs and verifies working context after a context compaction, then resumes the in-progress task safely.
- `visual-ux-sweep` — reviews and fixes UI/UX regressions in a web app via headless-browser screenshots across routes, viewports, themes, and interaction states.

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
