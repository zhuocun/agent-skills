# Agent Skills

Portable skills for AI agents. Each skill is one directory with a `SKILL.md`
whose frontmatter says when to use it, and whose body is the procedure the agent follows.

Ordinary skills work on their own: none names another, depends on another, or hands work to
another. `ensemble` is the explicit skill-loading shortcut: it names its members, each of
which still works independently. Installed together, ordinary skills cover different
responsibilities, so an agent can load several for one task. `burst` and `proxy` are alternatives:
both run a task through subagents but differ on who makes the final calls, so a task loads one
of them; their descriptions say which fits.

## Skills

**Planning and orchestration**

| Skill | What it does |
| --- | --- |
| `ensemble` | Explicit shortcut that loads every skill in its maintained member list as if each were explicitly invoked, again on every invocation, including members already loaded. Uses the host's skill-loading mechanism or supported instruction-file reading, and reports unavailable members and host limits. For an explicit request only, not automatic selection, model voting or work coordination. |
| `raise-ambition` | Before a non-trivial task starts, rewrites its brief to aim higher, in any domain, through four lenses: Altitude (the outcome the task serves), Depth (the methods, targets and checks an expert would use), Range (methods from other fields) and Speed (a deadline and an early outside check). Keeps the user's scope, constraints, permissions and budget, and returns one brief laid out under those four lenses, with a definition of done. The agent uses it on its own initiative when a new non-trivial request names a deliverable but no method and no acceptance criteria. Also used when asked to make a task, prompt or plan more ambitious. Unless the user asks, not for trivial tasks, fixes whose cause is known, tasks that already have a spec, or questions that need only an answer. |
| `burst` | Runs research, audit, implementation and review work through parallel subagents, with a reviewer before integration. The agent keeps the planning, integration and done decisions, and consults advisors on the strongest available models, over as many rounds as needed, on any hard decision it is still unsure about. Needs a way to launch subagents; not for a tiny single-step task. |
| `proxy` | Delegates every decision and every unit of work, including how to split the task and whether it is done, to top-tier subagents. For when the user wants subagents, not the main agent, to make those calls. Needs a way to launch subagents; not for a trivial single-step task. |

**Writing**

| Skill | What it does |
| --- | --- |
| `communicate` | Governs how the agent writes to the user: message shape, register, and what each claim must rest on. Applies to every message to the user; not for code, commit messages, documents, specs or product copy. Its body is mirrored as the `Baseline` output style in `.claude/output-styles/baseline.md`. |
| `chinese-diction` | Writes natural Chinese in the target register (professional, casual or creative) at the level of word choice and phrasing. Applies to every chat reply in Chinese, and to any request to write, translate into or polish Chinese. Not for agent-instruction files such as SKILL.md or prompts. |
| `document-editor` | Authors, edits and reviews formal documents (design docs, RFCs, plans, specs, research reports, guides, decision memos) at the document level without silently changing their meaning. Not for chat replies, routine status updates, sentence-level wording or translation polish, or agent-instruction files. |
| `status-report` | Produces a one-page project status report with fixed slots (Tasks, Changes since, Action required, Health, Unverified claims) for a reader who was not watching the work. |

**Architecture and review**

| Skill | What it does |
| --- | --- |
| `ddd-hexagonal` | Designs, reviews, audits and plans the evolution of backend architecture against textbook Domain-Driven Design with hexagonal (ports and adapters) architecture as the default standard: bounded contexts and aggregates, use-case inbound ports and consumer-owned outbound ports, inward dependency direction, an explicit composition root, executable architecture guards, persistence and consistency, failure semantics, migration and compatibility, and unnecessary complexity. Not for line-by-line diff correctness or for frontend code. |
| `backend-cr` | Reviews backend code or a backend diff for correctness against its requirements and contracts: authorization and validation order, normal, boundary and failure behavior, transactions and external calls, concurrency, compatibility and regression, test effectiveness, and documentation drift, with every finding resting on a reachable trigger and a located contract, and each proposed fix kept within the system's established architecture. Not for designing a system's architecture or for frontend code. |
| `frontend-cr` | Reviews frontend code or a frontend diff for runtime safety, security and data integrity, error handling, hook and effect correctness, type honesty, code smell and folder layering. Reads source and reports findings. Not for visual design or page layout, or for backend code. |
| `visual-ux-sweep` | Finds visual, UX and accessibility regressions in a web app from headless-browser screenshots across routes, viewports, themes and interaction states, and fixes them when asked. Needs an app that builds and runs locally. Not for building new features or pages. |

**Agent runtime**

| Skill | What it does |
| --- | --- |
| `reorient` | After a context compaction, or when it is unclear what is finished, checks the summary against git, PRs, CI and the files, then resumes the task. |
| `cursor-harness` | Operating manual for agents running inside Cursor: a task ledger, turn-start and turn-end routines, waiting on background jobs, subagent delegation and Cursor tool quirks. The agent adds newly confirmed facts to its `references/` files as it works; with a symlinked install, those edits land in your clone of this repo. |

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
git clone https://github.com/zhuocun/agent-skills.git

# Link every skill at once (when ~/.claude/skills does not already exist):
mkdir -p ~/.claude
ln -s "$(pwd)/agent-skills/.agents/skills" ~/.claude/skills

# Or link skills one at a time (when ~/.claude/skills is a regular folder):
mkdir -p ~/.claude/skills
ln -s "$(pwd)/agent-skills/.agents/skills/frontend-cr" ~/.claude/skills/frontend-cr
```

Swap `~/.claude` for `~/.agents` in these commands if that is where your runtime loads skills.
If a skill or folder with the same name already exists, move it aside before creating the symlink.
A symlinked install picks up changes on the next `git pull`; when a skill is renamed, recreate any link made under its old name.

## Changing a skill

This repo is the canonical source; make skill changes here. Before pushing, run:

```bash
python3 scripts/validate_skills.py
```

It checks that every skill directory has a `SKILL.md` whose frontmatter parses as YAML with a
non-empty `name` (matching the directory) and `description`, that the body opens with a `# `
title and has a `## Self-check` section, that `.claude/skills` links to `.agents/skills`, that
`baseline.md` matches `communicate`, and that `burst` and `proxy` have identical copies of
`references/cli-dispatch.md` and of the shared parts of their Model selection sections. Keep the
rest of the text they share in step by hand. It needs PyYAML (`pip install pyyaml`). Authoring
conventions are in `AGENTS.md`.
