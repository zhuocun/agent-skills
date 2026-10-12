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

### A detached launch looks like success
- **Status:** verified 2026-10-12
- **Fact:** A long regression started with `tmux new-session -d` finished without any notification. It was only found during a manual check, after its result had already gone stale.
- **Do:** Always pair a detached run with a waiter job. See background-work.md.

### Quote heredoc delimiters when the body has backticks or `$`
- **Status:** verified (before 2026-10-12)
- **Fact:** With an unquoted delimiter (`<<EOF`), backticks and `$()` in the body run as commands. One such heredoc accidentally started an agent CLI.
- **Do:** Use `<<'EOF'` for literal text.
