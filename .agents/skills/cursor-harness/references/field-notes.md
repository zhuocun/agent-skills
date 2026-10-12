# Field notes

Small, dated Cursor Harness facts that do not yet justify their own topic file. When three or more notes share a topic, move them into a reference file and add it to the table in SKILL.md.

Entry format:

```markdown
### <short imperative title>
- **Status:** verified YYYY-MM-DD | documented | unverified
- **Fact:** what happens, in one or two sentences.
- **Do:** the rule to follow.
```

### Quote tmux exact-match targets in zsh
- **Status:** verified 2026-10-12
- **Fact:** When the agent shell is zsh, an unquoted `tmux has-session -t =name` fails with `name not found`, because zsh expands a leading `=word` into a command path.
- **Do:** Write `-t '=name'` or `-t "=$S"`. Check the shell with `echo $0` first; bash does not do this.

### Do not split command strings through variables in zsh
- **Status:** verified 2026-10-12
- **Fact:** zsh does not word-split unquoted `$VAR`, so `CMD="tool --flag"; $CMD` runs a program literally named `tool --flag`.
- **Do:** Use an array (`CMD=(tool --flag); "${CMD[@]}"`) or call the tool directly.

### Do not rely on a recurring timer's first fire time
- **Status:** unverified (one observation, 2026-10-12)
- **Fact:** A recurring `subscribe_timer` with `delaySeconds: 1200` first fired after about 400 seconds, right after a separate one-shot timer had fired and the agent went idle. The cause is unknown; it could be phase alignment or the scheduler delivering when the agent is free.
- **Do:** Treat a timer as "wakes me no later than roughly the interval", not as an exact schedule. Each fire should run a full inventory that tolerates an early wake. Use a one-shot timer when the timing matters.

### Expect stale timer prompts after a long turn
- **Status:** verified 2026-10-12
- **Fact:** A recurring timer fired at 21:40 while the agent was blocked in a long turn. The prompt was queued and delivered only at 23:13, after the turn ended. By then the timer had been unsubscribed and every action in its prompt was already done.
- **Fact (same day):** A recurring 15-minute timer that fired five times during one long turn delivered all five prompts together when the turn ended, again after it had been unsubscribed.
- **Do:** Treat each timer prompt as "run the inventory now", not as a fresh instruction. Check the ledger and the end markers first, and skip actions that are already done. Note the `firedAt` time against the ledger timestamps. When a batch arrives, run one inventory for the whole batch. Since fires pile up while you block in a turn, prefer an interval longer than your typical blocking wait, or a one-shot timer re-armed at turn end.

### Smoke-check every leg of a multi-process launcher
- **Status:** verified 2026-10-12
- **Fact:** A launcher that runs two agents as `( ... ) &` subshells under `set -u` lost one leg silently: an environment line copied from another script referenced a variable defined elsewhere in that script, so the subshell died with `unbound variable` before creating its log. The other leg kept running, and the combined end marker would still have been written.
- **Do:** After launch, confirm each leg's log file exists and shows the expected model. When you copy environment lines from another script, copy the variables they reference too, or test the copied lines alone under `set -u` first. Prefer one tmux session and one end marker per agent.

### Use printf, not echo, to pipe captured JSON in zsh
- **Status:** verified 2026-10-12
- **Fact:** zsh's builtin `echo` interprets backslash escapes, so `echo "$out" | node ...` turns `\n` inside JSON strings into raw newlines, and `JSON.parse` fails with "Bad control character".
- **Do:** Pipe with `printf '%s' "$out"`, or avoid the variable and pipe the command directly.

### Check list ordering before polling for "the latest" item
- **Status:** verified 2026-10-12
- **Fact:** A deployment list API returned the oldest page first, with a page-size cap. A poller that read only page 1 would never have seen the new deployment and would have spun until it timed out.
- **Do:** Before writing a poller, confirm the sort order and pagination (`hasMore`, page size limit) once by hand. Match on a unique key, such as the commit hash, rather than on "first item".

### Quote heredoc delimiters when the body has backticks or `$`
- **Status:** verified (before 2026-10-12)
- **Fact:** With an unquoted delimiter (`<<EOF`), backticks and `$()` in the body run as commands. One such heredoc accidentally started an agent CLI.
- **Do:** Use `<<'EOF'` for literal text.
