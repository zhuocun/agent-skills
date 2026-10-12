# Delegation

How to hand work to subagents and external agent CLIs from inside Cursor without losing track of it. Which model or vehicle to pick for a role is decided by the `burst` skill's model selection and its `references/cli-dispatch.md`. This file covers the Cursor-side mechanics.

## Task-tool subagents (documented)

- **Prompt is the whole world.** A subagent sees neither the user's messages nor your earlier steps. Give it the goal, the files and paths, constraints, what not to touch, the exact deliverable, and the format of its final message. Write the brief in a file when it is long or will be reused, and point the subagent at it.
- **Background by default** for anything you do not need for your very next step: `run_in_background: true`. You cannot poll or await a background subagent, and should not try. Its result is delivered after your turn ends, so keep working or end the turn.
- **Parallel launch:** put independent Task calls in one message so they start together.
- **Resume** a finished subagent with its agent id to send a follow-up, for example a reviewer's issues back to the worker verbatim. Resuming a subagent that is still running fails. Wait for its result first.
- **Model:** pass a slug from the available model list only. An invalid slug fails the call. Use `inherit` unless the user or the routing table asks for a specific model.
- **Cloud subagents** (`environment: cloud`) run on their own VM and branch. Use them only when the user asks for cloud. Afterwards, follow the user's instruction on whether to merge, check out, or ignore that branch.
- **Descriptions** are the subagent's visible name. Make them concrete and distinct ("Review T3 patch r2"), and reuse the name in the ledger.

## External agent CLIs (Codex, Devin, Cursor CLI, Claude Code)

- Run them as tmux runs with an end marker and a waiter ([background-work.md](background-work.md)). They often run for many minutes and can outlive your turn.
- Export network settings such as proxy variables inside the launcher script. A tmux session does not inherit your shell's environment.
- Give each run a unique result path and confirm the result's modification time is after launch before you trust it.
- A non-empty "last message" file proves output, not completion. Completion needs the end marker or another exit signal.

## Verifying delegated results

- Treat a subagent's or CLI's report as a claim. Check the diff, run the test, or open the artifact before you mark the ledger entry done.
- When a reviewer returns issues, pass them to the worker verbatim and record the round in the ledger. Do not silently fix and claim the worker's result.
- Record each delegate in the ledger with its kind, name, model and speed, and the brief path, so a later turn can resume or audit it.

## Keeping the overview

- Delegate the work, not the bookkeeping. The ledger, acceptance records, and the final decision stay with you.
- Before launching a wave, write all its ledger entries first. Then launch, then confirm each one started.
- When delegates finish out of order, process each result as it arrives. Do not wait for the whole wave unless the next step needs all of it.
