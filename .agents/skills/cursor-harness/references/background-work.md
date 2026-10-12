# Background work and waiting

How to run long work without blocking, and how to make sure its end reaches you.

## What Cursor tracks and what it does not

| Launch | Tracked by Cursor? | Completion reaches you via | Status |
| --- | --- | --- | --- |
| Shell call that finishes within `block_until_ms` | yes | the call result | documented |
| Shell call with `block_until_ms: 0`, or one that outlives `block_until_ms` | yes, as a background job | end-of-turn notification for unawaited finished jobs; `AwaitShell` | documented |
| `tmux new-session -d`, `nohup`, `setsid`, `cmd &` | **no**: the launch command returns at once | nothing, unless you add a waiter | verified 2026-10-12 |
| Task subagent with `run_in_background: true` | yes | automatic result delivery after your turn ends | documented |
| `subscribe_timer` (Cloud Agent) | yes | a follow-up prompt when you are free | documented |

Unverified as of 2026-10-12: whether a background shell job that finishes after your turn has ended wakes you right away, and whether background shell jobs survive when the session is reclaimed. Until verified, treat a tmux run plus end marker as the source of truth and use a timer as a safety net for long runs.

## Choosing the vehicle

| Work | Vehicle |
| --- | --- |
| Under a few minutes, and your next step needs it | foreground shell call, `block_until_ms` sized to the expected runtime |
| Longer, but does not need to survive the session | background shell job (`block_until_ms: 0`), then one smoke check of its output file |
| Must survive the session, needs a human to attach, or is an agent CLI run (Codex, Devin, Cursor CLI), a deployment, or a long regression | tmux run with an end marker plus a background waiter job |
| Analysis, review, or coding a subagent can do | background Task subagent ([delegation.md](delegation.md)) |

## Shell job mechanics (documented)

- The output file header carries `pid` and `running_for_ms`, updated every 5 seconds. When the job ends, a footer adds `exit_code` and `elapsed_ms`.
- `AwaitShell` polls a job by id. `pattern` blocks until an RE2 regex matches the output body; it never matches the header or footer. A single call blocks for at most 119 minutes.
- Without a `shell_id`, `AwaitShell` is a plain sleep. Use it instead of `sleep` in the shell.
- If you observe a job's end yourself (for example you killed it), `AwaitShell` it once so a stale notification does not confuse the user later.
- Size waits in slices of 60–270 seconds or 1200 seconds and longer. Avoid round 5-minute waits, which miss the prompt cache.
- Never poll a job the tool result says the user backgrounded manually.

## tmux run plus waiter (verified 2026-10-12)

1. **Launcher script.** Write a script file for each run; do not inline long commands. The script exports any environment the run needs, because tmux sessions inherit the tmux server's global environment, not your shell's. It runs the command, captures stdout and stderr to a log, and **after** the process exits writes an end marker that contains the exit code:

```sh
#!/usr/bin/env bash
set -u
RUN_DIR="$1"; shift
"$@" >"$RUN_DIR/run.log" 2>&1
rc=$?
echo "rc=$rc ended=$(date -Is)" >"$RUN_DIR/run.end.tmp" && mv "$RUN_DIR/run.end.tmp" "$RUN_DIR/run.end"
```

   Use a unique run directory per run, and delete any old end marker before launch so a previous result cannot be mistaken for this one.

2. **Launch** in a uniquely named session: `<task-tag>-<role>-<n>`, so `tmux ls` maps to ledger entries at a glance.

3. **Waiter.** Right after the launch, start a background shell job (`block_until_ms: 0`) that exits when the marker appears:

```sh
S=t3-regress-1; END=runs/t3-regress-1/run.end
while [ ! -s "$END" ]; do
  if ! tmux has-session -t "=$S" 2>/dev/null; then
    [ -s "$END" ] && break
    echo "SESSION-GONE-NO-END"; exit 3
  fi
  sleep 15
done
echo "WAITER-DONE $(cat "$END")"
```

   The re-check after the session disappears closes the race between the marker write and the session exit. The unique final token lets `AwaitShell` match with `pattern: WAITER-DONE|SESSION-GONE`. Cursor now reports the waiter's completion like any other background job.

4. **On completion**, check the exit code, the log tail, and the artifacts, and confirm they belong to this run (modification time after launch). Then update the ledger.

If the waiter itself dies (session reclaimed, turn stopped), the tmux run continues. The turn-start inventory catches it via the end marker.

## Timers as a safety net (Cloud Agent, documented)

- `subscribe_timer` with `once: true` and `delaySeconds` enqueues a prompt that runs when you are otherwise free. Name it after the ledger entry; names deduplicate.
- Set one for any run expected to outlast your turn by more than about 20 minutes. Use the expected end plus a margin, and a prompt such as "Inventory ledger entry R7: check its end marker and process the result."
- Remove timers with `unsubscribe` once the entry closes. Check `list_subscriptions` during inventory.
- For GitHub, Slack, Linear, or CI events, use the `subscribe` skill rather than timers.

## Hangs

- Watch output growth, not just elapsed time. A run with no output growth for far longer than its normal cadence is suspect.
- Before killing anything, save the log, and confirm the PID belongs to this run (the launcher's recorded PID, or the output file header). Never kill by `pgrep -f` or `ps | grep` on prompt text: that matches the waiter and your own shell.
- After killing a hung run, retry once. Escalate or switch vehicles if it fails again, and record both attempts in the ledger.
