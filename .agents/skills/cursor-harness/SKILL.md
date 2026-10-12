---
name: cursor-harness
description: >-
  Cursor Harness operating manual: never lose a task, never block on a long process. Use whenever you run as an agent inside Cursor (IDE agent, Cloud Agent, or self-hosted worker) and the work involves more than one task at a time, delegating to Task-tool subagents or external CLIs, background shells, tmux sessions, deployments or test runs longer than a few minutes, follow-up messages that arrive mid-work, or resuming after a context compaction. Covers the task ledger, turn-start and turn-end routines, background-job waiting, subagent delegation, and Cursor tool quirks; the references directory holds topic files that grow over time. Do not use for a single short request that finishes inside one turn with no background work, or inside agents that do not run in Cursor (use that runtime's own guidance).
---

# Cursor Harness

You are running inside Cursor's agent harness. It gives you shell jobs, subagents, timers, and dynamic tools, but it does not remember your work for you: a process you detach is invisible to it, a compaction drops detail, and a new user message can arrive while three things are still running. This skill is the operating loop that keeps every task tracked and every long process watched, so you can delegate freely, take interruptions, and still close every task.

Priority order, highest first: **no task is lost → no finished job goes unnoticed → never sit idle on a wait when other work exists → minimal tool and token cost.** When two conflict, the higher one wins: an extra status check is cheaper than a forgotten run.

## Operating loop

### 1. Keep one ledger

Every piece of work you own lives in one ledger: user asks, subagents, background jobs, tmux runs, scheduled timers, and things waiting on the user. Write it to a durable file, not only to the todo tool, because compactions and new turns erase in-context state. Format, location, and states are in [references/task-ledger.md](references/task-ledger.md).

- Add the entry **before** you start the work or launch the job, not after.
- Each running entry names its completion signal (a shell job, an end-marker file, a subagent result, a timer) and the next action on completion.
- An entry closes only on evidence (exit code, artifact, user acceptance), never on "I think it finished".

### 2. Turn start: inventory before anything new

At the start of every turn, including the turn that delivers a follow-up message or a timer prompt:

1. Read the ledger.
2. Collect completion signals: shell job notifications, end markers, `tmux ls`, subagent results delivered to you.
3. Process what finished (verify, record, trigger the next step), then handle the new message.

If a compaction just happened, run the `reorient` skill first, then this inventory.

### 3. Classify every new message before acting

A new message is one or more of: a new task, a change to an existing task, a question, an acceptance or rejection, or a stop. Update the ledger for each part before you act on any of it.

- A question does not cancel running work. Answer it, then carry on.
- A scope change does not kill a correct running job. Let it finish and add a follow-up entry for the delta. Stop a job only when it is wrong or the user says stop.
- Restate the user's exact words in the ledger entry for new tasks and acceptances.

### 4. Delegate and background by default

Anything longer than a few minutes or independent of your next step runs off your critical path: a background Task subagent, a background shell job, or a tmux run with a waiter. Choose the vehicle with the table in [references/background-work.md](references/background-work.md). Write subagent prompts as self-contained briefs, because subagents cannot see this conversation ([references/delegation.md](references/delegation.md)).

**Never detach without a watcher.** A `tmux new-session -d`, `nohup`, `setsid`, or `&` launch returns at once. Cursor sees only that the launch succeeded and will never report when the real process ends. Pair every detached run with a background waiter job.

### 5. Wait efficiently

- While jobs run, do other independent ledger work. Background jobs and background subagents report on their own.
- Poll only when your next step is blocked on that specific job, or the job needs close monitoring (deployments, long test runs, migrations). Then keep polling until it ends, stalls, or is clearly hung.
- Before a long blocking wait on a Cloud Agent, check the follow-up queue. Handle the user first.

**Always pair the two wait mechanisms** (verified 2026-10-12). Neither is enough alone:

| Mechanism | Strength | Gap |
| --- | --- | --- |
| Blocking wait: `AwaitShell` on a waiter (an **any-end waiter** when two or more runs are going) | reacts within seconds of a run ending | a user message releases it early; it does nothing once your turn ends |
| Safety timer: `subscribe_timer`, recurring, with a prompt that says "run the inventory from the ledger" | wakes you even after your turn ends | reacts only at the next fire, so it can be late by up to one interval |

- While any run is going, keep a safety timer subscribed. Replace it when its prompt goes stale, and remove it when no run is left.
- When you have no other work, block on the any-end waiter ([references/background-work.md](references/background-work.md)). Never block on one run's waiter while another is going.
- **After every interruption, re-arm.** When a user message releases the wait, answer it, run the inventory, start a fresh any-end waiter over the runs still going, and block again in the same turn. Do not end the turn and leave only the timer, unless the user asked you to stop or the runs will take much longer than the timer interval.

### 6. Turn end: leave nothing unwatched

Before your final message:

1. Update the ledger.
2. For every entry still running, confirm it has a live completion signal. A background shell job or waiter that finishes after your turn ends does not wake you; only a timer, a background Task subagent, or a user message does. So when a run will outlast the turn, set a timer where available (one-shot at the expected end, or recurring when the end is uncertain).
3. Tell the user which items are still running, where to look, and what happens when they finish.

## References

Load the topic file when the situation arises. Each file is independent.

| File | Read when |
| --- | --- |
| [references/task-ledger.md](references/task-ledger.md) | Starting multi-task work; picking a ledger location; deciding entry states |
| [references/background-work.md](references/background-work.md) | Running anything long: shell jobs, `AwaitShell`, tmux plus waiter, timers, hangs |
| [references/delegation.md](references/delegation.md) | Dispatching Task subagents or external agent CLIs; verifying their results |
| [references/platform-tools.md](references/platform-tools.md) | Dynamic tools, Cloud Agent diagnostics, subscriptions, self-hosted machine rules |
| [references/field-notes.md](references/field-notes.md) | Before a tool or shell trick you have not used yet here; after you discover a new quirk |

## Maintenance

This skill is meant to grow. When you confirm a reusable Cursor Harness fact or fix:

- Put it in the topic file it belongs to. If no file fits and you have three or more related facts, create a new `references/<topic>.md` and add a row to the table above.
- Small or unproven tricks go to `references/field-notes.md` using its entry format.
- Mark each fact as **verified** (you ran it, with date), **documented** (from Cursor's tool descriptions or docs), or **unverified**. Upgrade or delete entries when evidence changes. Never keep two contradictory statements.
- Keep it machine-agnostic and project-agnostic: no absolute paths, usernames, session IDs, ports, proxy addresses, or credentials. Project-specific lessons belong in that project's memory, not here.
- Keep this file the short loop. Detail goes into references.

## Self-check

- [ ] Every user ask, subagent, background job, tmux run, and timer I own has a ledger entry with a completion signal and a next action.
- [ ] I ran the turn-start inventory before handling the new message, and processed everything that finished.
- [ ] No detached process runs without a waiter or another live completion signal.
- [ ] I did not block on a wait while independent work existed, and I did not poll background subagents.
- [ ] Nothing was marked done without evidence; acceptances quote the user.
- [ ] My final message lists what is still running, where to look, and what happens next.
- [ ] Any new reusable Cursor Harness fact I confirmed this turn was added to the right reference file with its verification status.
