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

Each `agent` and `pulse` copy also carries `.claude/output-styles/baseline.md`;
when syncing, make its body equal `communicate`'s body as `output-style-mirror`
compares them (below the frontmatter, the H1 and one blank line, trailing blank
lines included), since `skills-drift` does not check it.

| Surface | Source | Consumed by |
| --- | --- | --- |
| Skills | `.agents/skills/<name>/SKILL.md` | Claude Code (in-repo via the `.claude/skills` symlink), local runtimes (by symlink), and the `agent` and `pulse` repos (by copy) |

## Skill authoring conventions

Derived from the skills already in this repo (`conductor`, `chinese-diction`,
`frontend-cr`, `document-editor`, `status-report`), from the Agent Skills
specification and vendor skill-authoring guidance, and from the standard their
audits apply:

- **One directory per skill**, and the directory name must equal the skill's
  `name` frontmatter field: 1–64 lowercase ASCII letters, digits and single
  hyphens, not starting or ending with a hyphen. Give the skill a short name
  that says what it does. The directory holds a `SKILL.md`, plus optional
  `references/`, `scripts/`, `assets/` and `agents/` subdirectories when a skill
  needs them.
- **YAML frontmatter** with two required keys, `name` and `description`; other
  keys are allowed, and an optional `compatibility` value has 1–500 characters.
  The description states only what the skill does and when to use it, in at
  most 1024 characters with no `<` or `>`, which some hosts display as HTML
  entities. It opens with the key use case and its trigger words, because a host
  may shorten or drop descriptions when many skills are installed, and it
  includes the other triggers, keywords and exclusions that route requests, with
  a "Use when…" clause and, where the skill is easily over-applied, a "Do not
  use for…" clause (see `frontend-cr`, `document-editor`, `chinese-diction`).
  Operating rules, output form and rationale belong in the body.
- **Keep the frontmatter YAML-safe.** When the `description` contains
  characters that could break strict parsers, use a folded `>-` block scalar
  rather than a bare string — `chinese-diction`, `cursor-harness` and others
  do this.
- **Body pattern:** an `# H1` title, a one-paragraph statement of the skill's
  role, an explicit priority order where the work is ranked (e.g.
  `frontend-cr`'s "runtime safety → … → layering", `status-report`'s "grounded
  evidence → … → fixed form"), then the rules that must hold for the whole task,
  worded as standing rules rather than one-time steps because a host may
  re-attach only the start of a long skill after compaction, then the substance
  as numbered passes or failure modes (`frontend-cr`'s review passes,
  `chinese-diction`'s seven failure modes), and a terminal `## Self-check` the
  agent runs before declaring done.
- **Fit the body to the context budget.** Keep `SKILL.md` at most 500 lines
  and its body under 5,000 tokens, because a host may re-attach only the first
  5,000 tokens of a skill after compaction, and a longer body then loses its
  end, including the Self-check. Move material the agent needs only in some
  cases into `references/` files. Keep in `SKILL.md` every output form the
  agent must produce, the precedence of that form over other loaded
  instructions and standing preferences, and every limit that holds even
  against a user request, because an agent may not open a reference file.
- **Point to every reference file directly from `SKILL.md`**, by a relative
  link or by its `references/` path in inline code, not only from another
  reference file. Word each pointer as a standing rule that says when to read
  the file in full and to read it again after a compaction. Make every relative
  link in a skill's files resolve to an existing file. Start a reference file
  longer than 100 lines with a table of contents: a list, before its first `## `
  heading, that links to the anchor of each of its `## ` headings.
- **Make bundled scripts run unattended.** A script in `scripts/` states its
  interpreter and dependencies and takes input from arguments, environment
  variables, files or stdin, never from an interactive prompt. On failure it
  reports in the form its caller reads: when an agent runs it, a message that
  says what went wrong, what was expected and what to try; when a host runs it
  under a fixed protocol, the output that protocol defines. Ship tests with the
  script.
- **In `chinese-diction`, every register- or genre-conditional exception ships
  with a ✓ example** in the register or genre it excuses. A case named only in
  a waiver is not covered by the skill, it is merely exempted, and a model will
  read the waiver as licence to skip the rule rather than as a different
  standard to meet.
- **Make each skill stand alone and compose.** A skill works with no other skill
  loaded and does not conflict with skills loaded beside it. It does not name
  another skill, use terms only that skill defines, depend on its outputs or add
  a rule for its case; an exclusion describes the other domain instead. The only
  exception is `ensemble`, which loads its listed skills on explicit request. A
  skill whose subject is not specific to software also works outside software.
- **Write for an agent, not a human reader.** Skills are instructions a model
  follows; keep them imperative, concrete and self-contained. The body holds
  only text the executing agent uses, including the reasons that help it apply a
  rule. It holds no maintainer notes, provenance or attribution, and it states a
  source's ideas as the skill's own rules. Make skills clear, precise, concise
  and natural: give each sentence one reading, use one term for each concept
  throughout the skill, and prefer standard professional terms to coined jargon.
  Do not run the prose-editing skills (`chinese-diction`, `document-editor`) on
  SKILL.md files — they explicitly exclude agent-instruction files.
- **Keep tool and product facts correct as products change.** Choose a model,
  tool or product mode by a stable property, such as its place in the provider's
  own lineup, with a fallback for when nothing qualifies. Check each fact a
  skill states about a tool or product against that tool's or product's current
  documentation or observed behaviour.
- **State each rule once within a skill**, with its exceptions inside it; a
  Self-check line is its rule's check, not a second statement. A cross-reference
  names a section, a bold label or a number such as "pass 6", never a relative
  position such as "the last rule".
- **Rewrite a rule when you change it**, so it reads as if written that way from
  the start, not as the old rule plus an appended clause, exception or sentence.
  Do not word a rule as a reply to an earlier version, such as a "no longer",
  "even when" or "not X but Y" that answers removed text. When you relax a rule,
  widen it only by the cases the change is meant to allow, and keep its limiting
  words, such as "only".
- **Examples only illustrate**, including the ✓ examples `chinese-diction`
  requires: with every example deleted, the rule text alone must still give the
  right result.
- **Match each Self-check line to its rule exactly**, no stricter and no
  looser.
- **Keep cuts behaviour-neutral.** A cut removes only text whose removal changes
  no behaviour; make a behaviour change as its own deliberate decision.
- **Claim a routing or behaviour improvement only from a behaviour test.** The
  test runs the new and the previous version, each in a fresh context, on cases
  the editor has not seen: requests routed from descriptions alone, including
  near-miss requests that must not route to the skill, or scenarios given to
  fresh readers who see only the skill. Run each case more than once, on each
  model the skill is expected to run with, because results vary between runs and
  models. A result equal to the previous version's shows only that those cases
  did not regress. Build and run the test as `skill-optimize`'s
  `references/behavior-testing.md` directs.

## Repo conventions

- **Commits**: imperative subject; concise body explaining *why*. Never
  include AI model identifiers in commits, PR titles/bodies, or code comments.

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
> which runs on every pull request and on every push to `main`. A push to a branch with no
> pull request open is not validated. The workflow first runs `python3 -m unittest discover`,
> with the standard library only, in each `.agents/skills/*/scripts/` directory that holds
> `test_*.py` files, and fails if a directory runs no tests. It then installs PyYAML and runs
> `python3 scripts/validate_skills.py`. The validator enforces only these checks
> mechanically; review and behaviour tests cover the rest: every skill directory has a
> `SKILL.md` of at most 500 lines; the frontmatter parses as a YAML mapping; `name` and
> `description` are present, non-empty strings; `description` is at most 1024 characters (the
> Agent Skills specification's cap) and contains no `<` or `>`; `name` equals the directory
> name and is 1–64 lowercase ASCII letters, digits and single hyphens, not starting or ending
> with a hyphen; `compatibility`, if present, is 1–500 characters; the body opens with an `# `
> H1; the body's last `## ` heading outside fenced code is `## Self-check`; every relative
> Markdown link, inline or reference-style, in a skill's `.md` files resolves to an existing
> file (`#` anchors are not checked); every file under a skill's `references/` is linked, or
> named by its `references/` path in inline code, from its `SKILL.md`; every reference `.md`
> file longer than 100 lines has, before its first `## ` heading outside fenced code, a list
> linking to the anchor of each of its `## ` headings; `.claude/skills` still resolves to
> `.agents/skills`; and the `output-style-mirror` check holds: below the frontmatter, the H1
> and the one blank line after it, `.claude/output-styles/baseline.md` must equal
> `communicate/SKILL.md` line for line, trailing blank lines included. Frontmatter keys
> beyond those listed are allowed. Run the same commands locally before pushing.
