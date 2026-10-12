# Task ledger

The ledger is the single list of everything you owe. It replaces memory. If a task or process is not in the ledger, assume you will forget it.

## Where to keep it

Pick the first that applies, and say where it lives in your first progress note:

1. **The project's own tracker.** Some repos have a task document or harness ledger (for example a Coobee Harness `current-*.md`). Use it for the user-facing tasks and keep only the run-level detail below in a side file next to it.
2. **A persistent agent store**, when the system context lists one for the current agent. It survives compactions and new turns for this agent. Use `<store>/ledger.md`.
3. **A scratch file outside version control**, such as a directory the repo already ignores. Never leave a ledger where a broad `git add` would commit it.

The todo tool (`TodoWrite`) is a useful in-session view and renders progress for the user. It does not replace the file: compaction can drop it, and it has no room for completion signals.

## Entry format

One line or short block per entry. Keep it greppable.

```markdown
| id | kind | ask / purpose | owner | state | signal | next on completion | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T3 | task | "user's exact words" | me | running | — | report to user | — |
| R7 | run | regression for T3 | tmux `t3-regress-1` | running | end marker `runs/t3-regress-1.end` + waiter job | verify report, then report to T3 | log path |
| S2 | subagent | review of T3 patch | background Task "Review T3 patch" | running | subagent result | apply or send back issues | — |
| W1 | timer | wake-up for R7 | `subscribe_timer` "r7-check" | armed | timer prompt | inventory R7; unsubscribe if done | — |
```

Kinds: `task` (a user ask), `run` (shell job or tmux run), `subagent`, `timer`, `wait-user` (blocked on a user decision, credential, or acceptance), `guard` (something you must not do while a run is live).

## Guards for runs against shared environments

A run that exercises a deployed environment (an integration test, a regression, a load test) is invalidated by anything that redeploys or reconfigures that environment, including your own actions. Pushes are the common trap: a push to a branch with continuous deployment restarts the service under test, even when the commit only touches documents.

- Before launching such a run, find out what triggers deployments of the target (pushes to which branches, merges, scheduled jobs) and add a `guard` entry naming the forbidden action and the run it protects.
- Check the guard list before every push, merge, deploy, or config change. Commit locally and push after the run ends.
- Brief the executor to accept any build whose relevant code is unchanged from the baseline, instead of pinning one commit. Have it confirm no deployment is in progress before it starts, and check again at the end.

## States

`queued → running → verifying → done` for work, plus `blocked` (with the blocker named), `waiting-user` (with the exact question you asked), `accepted` (user's words quoted), `cancelled` (who cancelled and why), `failed` (evidence and the decision taken).

Rules:

- `done` needs evidence: exit code and artifact for runs, a reviewed result for subagents, an observable outcome for tasks.
- A `task` that the user must sign off stays `verifying` or `waiting-user` until they do. Record their words when they accept.
- A `run` with no live signal is a defect in the ledger. Give it a waiter, a timer, or poll it now.

## Handling interruptions

When a new message arrives mid-work:

1. Inventory first (SKILL.md, step 2), so you do not answer on stale state.
2. Split the message into parts and map each to an entry: new `task`, update to an existing entry, answer-only, acceptance, or stop.
3. Do the cheapest high-value part first, usually the answer or the acceptance bookkeeping, then resume the most blocked work.
4. When the user switches topic, leave the old entries in their real state. Mention them in your turn-end summary until they are closed or the user drops them.

## Reporting

- **Progress notes:** name the entry and its state change in one sentence ("The regression for the redeploy finished: 72 passed, 3 failed; reviewing the failures now").
- **Turn end:** list open entries grouped as running, waiting on you, and queued. Skip closed ones unless they closed this turn.
- **On request** ("what's unfinished?"): read the ledger plus any project trackers, verify each open entry's real state, then answer.
