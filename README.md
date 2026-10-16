# Agent Skills

Portable skills for coding and writing agents. Each skill is one directory with a `SKILL.md`
whose frontmatter says when to use it, and whose body is the procedure the agent follows.

Every skill works on its own: none names another, depends on another, or hands work to another.
Installed together, each covers a different responsibility, so an agent can load several for
one task without them conflicting.

## Skills

**Planning and orchestration**

| Skill | What it does |
| --- | --- |
| `raise-ambition` | Before a non-trivial task starts, rewrites its brief to aim higher: Altitude, Depth and Range from Felix Rieseberg's essay on ambition, plus a Speed lens. Keeps the user's scope, constraints, permissions and budget, and returns one brief with a definition of done. The agent uses it on its own initiative for every new request that names a deliverable but no method and no acceptance criteria. |
| `burst` | Runs research, audit, implementation and review work through parallel subagents, with a reviewer before integration. The agent keeps the planning, integration and done decisions. |
| `proxy` | Delegates every decision and every unit of work, including how to split the task and whether it is done, to top-tier subagents. For when the user wants subagents, not the main agent, to make those calls. |

**Writing**

| Skill | What it does |
| --- | --- |
| `communicate` | Governs how the agent writes to the user: message shape, register, and what each claim must rest on. Applies to every message to the user. Its body is mirrored as the `Baseline` output style in `.claude/output-styles/baseline.md`. |
| `chinese-diction` | Writes natural Chinese in the target register (professional, casual or creative) at the level of word choice and phrasing. Applies to every chat reply in Chinese, and to any request to write, translate into or polish Chinese. Not for agent-instruction files such as SKILL.md or prompts. |
| `document-editor` | Authors, edits and reviews formal documents (design docs, RFCs, plans, specs, research reports, guides, decision memos) at the document level without silently changing their meaning. |
| `status-report` | Produces a one-page project status report with fixed slots (Tasks, Changes since, Action required, Health, Unverified claims) for a reader who was not watching the work. |

**Review**

| Skill | What it does |
| --- | --- |
| `cr-fe` | Reviews frontend code or a frontend diff for runtime safety, security and data integrity, error handling, hook and effect correctness, type honesty, code smell and folder layering. Reads source and reports findings. |
| `visual-ux-sweep` | Finds UI and UX regressions from headless-browser screenshots across routes, viewports, themes and interaction states, and fixes them when asked. Needs an app that builds and runs locally. |

**Agent runtime**

| Skill | What it does |
| --- | --- |
| `reorient` | After a context compaction, rebuilds the working context from git, PRs, CI and files rather than the summary, then resumes the task. |
| `cursor-harness` | Operating manual for agents running inside Cursor: a task ledger, turn-start and turn-end routines, waiting on background jobs, subagent delegation and Cursor tool quirks. The agent adds newly confirmed facts to its `references/` files as it works. |

## Layout

```
.agents/skills/<name>/          canonical skill: SKILL.md, plus references/ when the skill needs them
.claude/skills                  symlink -> .agents/skills, so Claude Code finds the skills in this repo
.claude/output-styles/          Baseline output style, mirroring communicate
scripts/validate_skills.py      checks every skill; CI runs it on each pull request
docs/                           research notes behind the skills; agents do not load them
```

## Local use

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
A symlinked install picks up changes on the next `git pull`.

## Changing a skill

This repo is the canonical source. The `agent` and `pulse` repos hold copies, not symlinks, so
edit a skill here first and copy it there after it merges. Before pushing, run:

```bash
python3 scripts/validate_skills.py
```

It checks each skill's frontmatter (`name` matching the directory, and a `description`), its
`# ` title and `## Self-check` section, the `.claude/skills` symlink, that `baseline.md`
matches `communicate`, and that the text `burst` and `proxy` share is identical. Authoring
conventions are in `AGENTS.md`.
