# agent-loop: feedback from one long orchestration session (2026-11-12)

Status: open. Source: one Claude Code session that owned an agent loop for about a day
while it also ran the `conductor` skill (orchestrator, workers, reviewers, background
waiters). The proposed changes below are suggestions from that one session; none was tested.

## What happened

- The state file `.agent-loop.md` existed, named the session as owner and was outside
  version control. Its last update was about six hours before the user asked whether the
  loop file and hooks were in use.
- In those six hours the session closed four items, opened three and received a user
  decision. It recorded all of this in a separate scratch checklist that the orchestration
  kept, and none of it in the state file.
- The queue held one item with status `done`, and it still listed a closed item as open.
- The hook's companion file `.agent-loop.hook.json` recorded `turns: 4` for the whole
  session. Background agents and their completion notices resumed the session, so turns
  rarely ended with ready work, and the turn-end hook rarely ran.
- After a context compaction the session continued from the summary. The summary carried
  an old status line with `turn 42/50`. The session then wrote `turn 43/50` to
  `turn 50/50` in eight status lines. No hook message supplied those counts.
- The repair took one step: each item had a `done when` criterion and each waiting item
  had a `check`, so the queue was rebuilt from evidence.

## Defects in the skill that these events show

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

5. **The parser accepts a status outside the four allowed values.** The skill states that
   parser acceptance is not validation, and the agent did not check the file.
   - Suggested change: the hook reports any queue line whose status is not `ready`,
     `doing`, `waiting` or `user`, and any queue line it could not match.

## What worked

- The `done when` and `check` fields made the rebuild from evidence fast and mechanical.
- The ownership line and the sidecar gave an exact answer to "did the hook run, and how
  often".

## Not verified

- Whether the hook can read the session's activity time on every supported host.
- Whether a staleness warning at turn end reaches the agent early enough in a session
  that seldom ends turns with ready work.
