# agent-loop: feedback from one long orchestration session (2026-11-12)

Status: open. Source: one Claude Code session that owned an agent loop for about a day
while it also ran the `conductor` skill (orchestrator, workers, reviewers, background
waiters). The suggestions below were untested at the time of that report. The original
session trace was not available for the 2026-11-13 review; its incidents remain reported
history, distinct from the baseline source and script checks described below.

## What happened

- The state file `.agent-loop.md` existed, named the session as owner and was outside
  version control. Its last update was about six hours before the user asked whether the
  loop file and hooks were in use.
- In those six hours the session closed four items, opened three and received a user
  decision. It recorded all of this in a separate scratch checklist that the orchestration
  kept, and none of it in the state file.
- The queue held one item with status `done`, and it still listed a closed item as open.
- The hook's companion file `.agent-loop.hook.json` reportedly recorded `turns: 4`.
  The session attributed this to background completions resuming work and few turns
  ending with ready work. That value cannot establish how often the hook ran: `turns`
  counts continuation grants for the current goal, with early returns that do not
  increment it and a reset when the goal changes.
- After a context compaction the session continued from the summary. The summary carried
  an old status line with `turn 42/50`. The session then wrote `turn 43/50` to
  `turn 50/50` in eight status lines. No hook message supplied those counts.
- The repair took one step: each item had a `done when` criterion and each waiting item
  had a `check`, so the queue was rebuilt from evidence.

## Session interpretations and suggestions

These suggestions record the original report, including alternatives not adopted.
Baseline review at `4c1acb13807f248d76bb8675600fae40de84ce64` found existing rules for
reload, one scheduling record, evidence-based closure and hook-sourced counts. The
accepted wording clarifications put reconciliation before scheduling and reporting,
use the state file as the running checklist, and specify count provenance; they do
not establish a behavioral fix. Timer, sidecar-count and parser-diagnostic suggestions
remain future options outside that change.

1. **No rule binds the status line to the state file after a compaction.** The skill says
   to read the skill and the state file on resume or after compaction. It does not forbid
   a status line before that read. A summary can carry a complete, plausible status line.
   - Suggested rule: after a compaction or resume, write no status line until the state
     file is read in the current context.

2. **The turn count has one source, and a summary can copy it.** Pass 7 takes the count
   from the latest `[agent-loop]` hook message and omits it otherwise. A summarized
   conversation keeps an old count without the hook message that produced it, and nothing
   marks that count as stale.
   - Suggested change: state that a count carried by a summary or by an earlier status
     line is never a source, and that the agent never increments a count.
   - Possible support in the hook: expose the count in a form the agent can read on
     rebuild, so that a file is the source and the conversation is not. (The sidecar
     already holds `turns`; the skill currently says only that the agent must not edit
     the sidecar, and does not say whether the agent may read it.)

3. **A second scheduling record can replace the state file without notice.** Pass 1
   permits a reference to an existing task tracker for acceptance criteria and evidence.
   It does not cover a second running checklist that another loaded skill requires
   (`conductor` requires one). In this session the checklist received every update and the
   state file received none.
   - Suggested rule: when another instruction requires a running checklist, the state file
     stays the scheduling record; every closure and every status change goes to the state
     file first, and the checklist is referenced from the queue lines or the log.

4. **The hook does not detect a stale state file.** It runs only at turn end. In a session
   that background completions resume, few turns end with ready work.
   - Suggested change: when the hook runs, compare the state file's modification time with
     the current time and with the sidecar's last write, and print a warning when the file
     is old while the session is active. The threshold needs a test; this session's gap
     was six hours.
   - Suggested rule in pass 3: a completion notice or a delegate's hand-back counts as a
     wake, and the first action on a wake is the rebuild step, which includes recording
     the result in the state file.

5. **Matched invalid statuses are rejected; unmatched queue text can be ignored.** The
   original report alleged acceptance of `done`. The baseline's
   [parser](../../.agents/skills/agent-loop/scripts/loop_hook.py) rejects a matched row
   such as `- [done] T9 ...`; its main handler catches the error and emits the host's
   no-continuation output. Text that does not match a queue row, such as `- [done]`
   without an ID, is ignored. Baseline script checks confirmed both behaviors; neither
   establishes the original row's exact form. Parser acceptance still does not validate
   the complete file, which the owner must check.
   - Possible future change: report invalid matched statuses and unmatched queue text
     while preserving the host protocol and existing continuation guards.

## What worked

- The `done when` and `check` fields made the rebuild from evidence fast and mechanical.
- The ownership line identified the reported owner. The sidecar counted continuation
  grants for its current goal, not total hook invocations or confirmed executed turns.

## Not verified

- The original long-session incidents, including the six-hour state gap and hook
  invocation frequency, without the original trace.
- Whether the wording clarifications improve behavior in long sessions or after real
  compaction; source and script checks do not demonstrate that effect.
- Whether the hook can read the session's activity time on every supported host.
- Whether a staleness warning at turn end reaches the agent early enough in a session
  that seldom ends turns with ready work.
