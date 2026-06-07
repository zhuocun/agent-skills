# Agent Skills

Personal agent skills that can be installed or linked into a local agent runtime.

## Skills

- `burst` — orchestrates parallel subagents for research, audit, implementation, and review work.
- `document-editor` — edits formal human-facing documents at the document level without changing their meaning.
- `chinese-diction` — improves Chinese word choice, phrasing, and register for natural professional prose.
- `cr-fe` — comprehensive frontend code review for runtime safety, error handling, hook correctness, code smell, and folder-structure layering.

## Local Use

Clone the repo, then link or copy the skill directories into your local skills folder:

```bash
git clone git@github.com:zhuocun/agent-skills.git
ln -s "$(pwd)/agent-skills/burst" ~/.agents/skills/burst
ln -s "$(pwd)/agent-skills/document-editor" ~/.agents/skills/document-editor
ln -s "$(pwd)/agent-skills/chinese-diction" ~/.agents/skills/chinese-diction
ln -s "$(pwd)/agent-skills/cr-fe" ~/.agents/skills/cr-fe
```

If a local skill with the same name already exists, move it aside before creating the symlink.
