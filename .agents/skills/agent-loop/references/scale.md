# Scale

These rules hold, beside every rule in `SKILL.md`, while the state file exceeds 100 lines, `parallel` exceeds 1, or a worker does an item.

- [Status command](#status-command)
- [Workers](#workers)
- [Waves](#waves)
- [Integration](#integration)
- [Growing queue](#growing-queue)
- [Notes](#notes)
- [Budget](#budget)

## Status command

```sh
python3 "$SKILL_DIR/scripts/loop_hook.py" status [--state PATH] [--limit K]
```

`SKILL_DIR` is this skill's directory. Without `--state`, the command looks for `.agent-loop.md` from the current directory upward to the repository top, so run it inside the workspace or pass the path. It never writes a file. Exit code 0 means it read the file, with any problems listed in its output; exit code 2 means it found no state file or could not read it, and its message on stderr says what to try.

Its output has a fixed size whatever the queue length. `K`, 5 by default, caps every list, and a capped list ends with `+N more`. The sections, in order:

1. the path, then `goal`, `owner`, `stop`, `async gates`, `budget` and `parallel`;
2. `counts:` doing, ready with dependencies met, ready but blocked, waiting, need you, closed;
3. `doing:` the full lines of `doing` items;
4. `next:` the first K unblocked `ready` items, in queue order;
5. `wave:` only when `parallel` exceeds 1, the IDs that may run together now;
6. `waiting:` and `need you:` the full lines of `waiting` and `user` items;
7. `problems:` each problem with its line number, reason and fix, or `none`.

- **Use:** on each iteration that does not read the whole file, run the command in place of that read. Take the first unblocked item in `doing:`, else the first in `next:`, as **Pick** directs. Where the script cannot run, read the whole file instead.
- **Problems:** when `problems:` is not `none`, read the whole file, repair each listed problem from evidence, and run the command again before picking. Several of these problems end the hook's automatic continuation without a message.
- **Edits:** change the file one line at a time, finding each line by its ID. Never rewrite the file from the command's output, which shows only part of it.

## Workers

A worker is an agent you dispatch to do one item.

- **Brief:** give each worker one item and a self-contained brief: the item's line with its `done when` and `writes:`, the check to run, the whole `## Notes` section, the absolute path for its detail file, and the result form below. A worker never edits the state file.
- **Copy:** give a worker that changes files an isolated copy of the repository when the host offers one, made from the current integrated state, so that it holds the closed work its item depends on.
- **Result:** the worker writes its full account (commands, output, reasoning, failures) to its detail file, for example `.agent-loop.d/<ID>.md` at the workspace root, which the `/.agent-loop.*` exclude line already keeps out of version control, and returns only:

  ```
  item: <ID>
  result: done | failed: <one-line reason> | blocked: <one-line question>
  evidence: <absolute path of the detail file>
  files: <changed paths, comma-separated, or none>
  ```

  Treat `done` as a claim to confirm under **Check**. Open the detail file only when the result or your check needs it.
- **Held items:** an item is `doing` while its worker holds it. When the turn ends before the worker returns, set the item `waiting` with `wake: worker <name>` and a `check:` that shows the worker's result exists, such as a test that its detail file is present.

## Waves

A wave is a set of items in progress at the same time. Work sequentially unless all three hold:

- `parallel: <N>` in the header is above 1. Absent, it is 1. Keep a value the user set.
- The items are listed in the command's `wave:` output now.
- **Pilot:** one to three items of the same kind have already closed one after another. Items are of one kind when the same steps, brief and check apply to each, such as moving one module each to a new package. Close a second or third pilot item when the one before it needed a change to its brief, check or scope, and record what the pilot taught in `## Notes`.

`writes: <path or glob>, <path or glob>` on an item lists every file it may change. `wave:` fills the free slots, which are `parallel` minus the open `doing` and `waiting` items that have `writes:`. It walks the unblocked `ready` items in queue order and takes an item only when its scopes overlap no scope of an item already taken or of an open `doing` or `waiting` item. An item without `writes:` never joins a wave. Two scopes overlap when the part of one before its first `*`, `?` or `[` is a prefix of that part of the other. So:

- Write the narrowest scope that covers the item, such as `java/billing/invoice/**` rather than `java/**`. A scope that starts with a wildcard overlaps every other scope.
- Change a file that many items touch, such as a shared build file, in an item of its own that runs alone.
- While wave items are open, take only items that `wave:` lists, whether you do one yourself or dispatch it.

## Integration

- **One at a time:** take the wave's results one by one. For each, check that every changed file, by the `files:` line and by the change itself, lies inside the item's `writes:`; bring the change into the shared working state; confirm the item under **Check**; and close it under **Log**.
- **Rejects:** a result that conflicts with integrated work or changes a file outside its `writes:` returns its item to `ready` with `tries:` raised under **Attempts**. Keep its detail file and name it in the next attempt's brief.
- **Regression check:** after the wave's last result, run one check over the integrated state, such as the project's full build and test suite, and record its result in the evidence of the wave's last closure. Start no further wave until it passes; to fix a regression in closed work, add an item that names the failure and the closed IDs.

## Growing queue

- **Children:** an item may close by adding child items. Give each child the parent's ID with a numbered suffix (`T4.1`, `T4.2`), add them in dependency order with each below the items it needs, and list them in the parent's closure line, such as `- <UTC date and time> T4 closed — inventory in docs/billing.md; added T4.1, T4.2, T4.3`.
- **Open parent:** closing a parent meets every dependency on it. When an open item needs the children's work rather than the parent's, keep the parent open instead: add the children above it, give it `after:` naming them, and close it when they have closed.

## Notes

`## Notes` is an optional section between Queue and Log, or after Log; the hook and the command ignore it. When the same problem or convention appears a second time, record it there as one line, such as `- Value objects are Java records in domain/model, with no setters.` Keep the section short: merge lines, and delete each line that no longer holds.

## Budget

One automatic turn can close many items, so set `budget` for a large queue from the number of turns the run is expected to take, not from the number of items. A value the user set wins.
