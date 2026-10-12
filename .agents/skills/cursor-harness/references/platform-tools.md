# Platform tools

Cursor-specific tools and rules that matter for long, concurrent work. Tool availability varies by surface (IDE, Cloud Agent, self-hosted worker) and changes over time. Check what is present before relying on it.

## Dynamic tools (documented)

- Tools in dynamic namespaces (MCP servers, the `cursor` namespace, Cloud Agent diagnostics) must be discovered with `GetDynamicTools` before you call them with `CallDynamicTool`. Aim for one discovery call followed by one invocation.
- Look up a single tool by namespace and name when you know it. That returns its full description, which often contains usage rules (for example, "do not poll subagents").
- A namespace in `needsAuth` or `error` state is unusable until fixed. Authenticate through its `mcp_auth` tool only when you actually need it.

## Built-in `cursor` namespace (documented)

- `AwaitShell`: poll or sleep. See [background-work.md](background-work.md).
- `Task`: subagents. See [delegation.md](delegation.md).
- `TodoWrite`: the in-session todo list. Useful as a view; not a durable ledger.
- Others (`WebFetch`, `WebSearch`, `CreateGoal`/`UpdateGoal`, `GenerateImage`) are available on demand. Read the schema first.

## Cloud Agent diagnostics (`cursor-cloud`, documented)

- `get-message-queue`: the user's pending follow-up messages. Check it before a long blocking wait, and defer slow verification while messages are queued.
- `run-info`: run identity, branch, model, and the run URL.
- `get-events`: run lifecycle events, including MCP authentication failures that otherwise fail silently.
- `list-cloud-agents` and `batch-fetch-details`: other runs and their transcripts. Read large transcripts through a subagent, never directly.

## Subscriptions (`cursor-subscriptions`, documented)

- `subscribe_timer`: one-shot (`once: true` plus `delaySeconds`) or recurring (`cron` or `delaySeconds`) follow-up prompts. After subscribing, say what you are waiting for and end the turn.
- `subscribe_slack_thread`, `subscribe_slack_channel`, `subscribe_linear_issue`, `subscribe_linear_comment`: event-driven wake-ups.
- `list_subscriptions` and `unsubscribe`: include them in turn-start inventory, and remove subscriptions once their ledger entry closes.

## Cloud Agent and self-hosted rules that affect bookkeeping

- Git identity on a self-hosted machine comes from the machine's config. Check `user.name` and `user.email` before the first commit, and set them per-repository only if unset.
- Pull requests go through the PR management tool, not forge CLIs. If it refuses (for example, the forge host is not configured), the refusal is final for the run. Record it in the ledger and tell the user.
- Shell state (working directory, environment variables) persists between shell calls in one session. tmux sessions start from the tmux server's global environment instead.
- The terminals folder holds one file per shell session with a metadata header. Read the first lines to check what is running before starting a duplicate.
- After a context compaction, the conversation is a summary. Run the `reorient` skill, then the ledger inventory, before any irreversible step.
