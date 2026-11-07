# Host setup

Use the section for the current host and mode. Where continuation, the owner-ID route or completion wake is unverified, use the corresponding within-turn fallback in passes 2 and 5 until that capability is confirmed.

For Codex, Cursor, Antigravity and Devin, live continuation is established only for the project configurations in **Modes and continuation**. User-scope loading, background-completion wake, host continuation caps and repeated continuation beyond one automatic turn remain unverified live. IDE behavior is not established by these CLI results.

## Registration command

Use Python 3.8 or newer; the scripts need only the standard library. Set `SKILL_DIR` to the resolved absolute directory containing this skill's `SKILL.md`, `SCOPE` to the user or project scope chosen under pass 2's **Host** rule, and `WORKSPACE` to the workspace root.

The installer interface is:

```sh
python3 "$SKILL_DIR/scripts/install_hook.py" --host HOST --scope user|project [--workspace DIR] [--dry-run] [--uninstall]
```

Choose `codex`, `cursor`, `antigravity` or `devin` for `HOST`. If supplied, `--workspace` must name an existing directory; otherwise the project workspace defaults to the current directory's Git top level, or the current directory outside a repository. Use `--dry-run` to print `path: <absolute target path>` followed by the complete resulting JSON, indented by two spaces and ending with a newline, without writing. Use `--uninstall` to remove matching handlers and any event or matcher/named group left empty by that removal; a missing file stays absent.

The installer identifies its handlers by a command containing both `loop_hook.py` and a matching `--host HOST` argument. Installation replaces those handlers in place, preserves unrelated keys and entries, and is idempotent. It creates missing parent directories and writes atomically while retaining an existing file's permission bits. It refuses invalid or non-object JSON, including JSONC with comments, and incompatible container types it needs to edit, without changing the file. Exit codes are 0 for success, 1 for a refused file and 2 for usage errors, an invalid workspace or `--host claude`. Normal installation prints the target path and the host's activation guidance.

The registered command is `python3 <absolute path of scripts/loop_hook.py> --host HOST`, with the resolved path of the script beside the installer shell-quoted and a 30-second hook timeout.

## Hook interface

The hook interface is `scripts/loop_hook.py [--host HOST] [--state PATH]`. `HOST` accepts `claude` (the default), `codex`, `cursor`, `antigravity` or `devin`; `--state` overrides state-file discovery. Let the hook read one JSON event from stdin. It exits 0 and prints one JSON object followed by a newline. Errors, unknown hosts, unexpected, repeated or valueless arguments, and unaccepted events produce `{}`; an accepted Stop also produces `{}` when the queue guards do not grant continuation.

Without `--state`, discovery searches each host root in order, walking upward from each root through the first directory containing `.git`, inclusive, or to the filesystem root. It uses the first `.agent-loop.md` found:

| Host | Search roots, in order |
| --- | --- |
| Claude Code | Event `cwd`, then environment `CLAUDE_PROJECT_DIR` |
| Codex | Event `cwd` |
| Cursor | Strings in event `workspace_roots`, then environment `CURSOR_PROJECT_DIR` |
| Antigravity | Strings in event `workspacePaths` |
| Devin | Environment `DEVIN_PROJECT_DIR`, then `CLAUDE_PROJECT_DIR`, then the hook process's current directory |

Continuation output carries the same `[agent-loop]` instruction in `reason` with `decision: "block"` for Claude Code, Codex and Devin; in `followup_message` for Cursor; or in `reason` with `decision: "continue"` for Antigravity. Devin's `SessionStart` response supplies identity context as its **Owner ID** rule describes, independently of any state file.

## Claude Code

- **Registration and activation:** use pass 2's frontmatter registration. There is no installer command for this host; the installer refuses `--host claude`.
- **Owner ID:** use `${CLAUDE_SESSION_ID}`. If that text appears unexpanded, read the environment variable `CLAUDE_CODE_SESSION_ID`.
- **Continuation limits:** apply the queue budget and pass 6's continuation-cap rule.
- **Completion wake:** use Bash with `run_in_background` for a waiter whose completion reports back to this session.

## Codex

Register with:

```sh
python3 "$SKILL_DIR/scripts/install_hook.py" --host codex --scope "$SCOPE" --workspace "$WORKSPACE"
```

- **Configuration:** expect `Stop` under `hooks` in `$CODEX_HOME/hooks.json` for user scope, defaulting to `~/.codex/hooks.json`, or in `<workspace>/.codex/hooks.json` for project scope. Skill frontmatter does not register Codex hooks.
- **Activation:** have the user open `/hooks`, select the handler, inspect it and press `t` to trust it. Project hooks also need a trusted project.
- **Modes and continuation:** in codex-cli 0.167.0, `codex exec` and `codex exec resume` fire the project Stop hook with `--dangerously-bypass-hook-trust` and project trust supplied through `-c`. On exec resume, `decision: "block"` starts one automatic turn whose Stop has `stop_hook_active: true`; `stop: done` returns `{}` with no automatic turn. The shared core supports initial-exec and interactive CLI continuation, but live continuation in those modes and mode parity remain unverified.
- **Owner ID:** read `CODEX_SESSION_ID` through a model-invoked shell command and use its value as `owner:`:

  ```sh
  printf '%s\n' "$CODEX_SESSION_ID"
  ```

  In the project exec configuration in **Modes and continuation**, the command's value equals Stop's `session_id`, which stays unchanged on exec resume. The 0.167.0 identity represents a shared session tree, not a unique concrete thread or fork; live child/fork behavior is unverified. Do not substitute `CODEX_THREAD_ID`.
- **Continuation limits:** let the hook budget govern; the 0.167.0 shared core has no numeric cap on consecutive Stop continuations.
- **Completion wake:** do not rely on ordinary background `unified_exec` completion to wake an idle model. The 0.167.0 exit watcher emits a tool completion event but does not enqueue a model turn. Other client or daemon wake paths are unverified.

## Cursor

Register with:

```sh
python3 "$SKILL_DIR/scripts/install_hook.py" --host cursor --scope "$SCOPE" --workspace "$WORKSPACE"
```

- **Configuration:** expect `hooks.stop` in `~/.cursor/hooks.json` for user scope or `<workspace>/.cursor/hooks.json` for project scope. The installer supplies `version: 1` when that key is absent and preserves an existing value. The CLI skill loader does not register hooks from skill frontmatter.
- **Activation:** trust the workspace in the interactive CLI. Current IDE approval and trust procedures are unverified.
- **Modes and continuation:** in CLI 2026.11.05-86047df, the interactive CLI started with `--trust` runs the project `stop` hook. Its `followup_message` starts one automatic turn whose Stop has `loop_count: 1`; `stop: done` returns `{}` with no automatic turn. Print-mode (`agent -p`) Stop firing and continuation remain unverified; do not rely on them. Current IDE end-to-end continuation is also unverified.
- **Owner ID:** read `CURSOR_CONVERSATION_ID` through the agent's Shell tool:

  ```sh
  printf '%s\n' "$CURSOR_CONVERSATION_ID"
  ```

  Use this value for ordinary UUID CLI sessions: it equals Stop's raw `conversation_id` in the interactive project configuration in **Modes and continuation**, and its filesystem encoding leaves UUIDs unchanged. For custom IDs or IDE sessions, use only a value confirmed equal to that raw field. Equality is not guaranteed for custom IDs and is unverified in the current IDE; live resume and child-agent identity are also unverified. Do not use `generation_id`.
- **Continuation limits:** the installer sets the native stop handler's `loop_limit` to `null`, which removes that handler's native continuation limit.
- **Completion wake:** the 2026.11.05 interactive CLI implementation schedules a new run in the owning conversation when a host-managed background shell completes while idle, but live wake behavior remains unverified. Pending completions are dropped after a user-aborted turn. An arbitrary detached process started with shell `&` has no established wake guarantee. Current IDE wake support is unverified.

## Antigravity

Register with:

```sh
python3 "$SKILL_DIR/scripts/install_hook.py" --host antigravity --scope "$SCOPE" --workspace "$WORKSPACE"
```

- **Configuration:** expect the named group `agent-loop` with a flat `Stop` handler array in `~/.gemini/config/hooks.json` for user scope or `<workspace>/.agents/hooks.json` for project scope. Use this configuration route; skill-frontmatter hook registration is unverified.
- **Activation:** if the CLI asks whether to trust the workspace, choose "Yes, I trust this folder". The print configuration in **Modes and continuation** loads project hooks without a pre-existing workspace entry in `trustedWorkspaces`; do not generalize that to other permission modes. In the IDE, inspect or toggle hooks through **... > Customizations > Hooks**; its exact project-trust approval procedure is unverified.
- **Modes and continuation:** in agy 1.5.2 print mode (`-p --mode accept-edits`, with `--conversation` to resume), the project Stop hook fires on initial and resumed runs. A resumed run accepts `decision: "continue"` and starts one automatic turn; with `stop: done`, it returns `{}` and no automatic turn follows. Live continuation on an initial print run remains unverified. CLI interactive and IDE interactive hook support is documented, but live firing and parity with this print configuration remain unverified.
- **Owner ID:** in the CLI, read the command runner's injected `ANTIGRAVITY_CONVERSATION_ID`:

  ```sh
  printf '%s\n' "$ANTIGRAVITY_CONVERSATION_ID"
  ```

  In the print configuration in **Modes and continuation**, this value equals Stop's `conversationId`, and resumed Stops retain that ID. Reading the variable again after resume, child-agent identity, and the variable's availability and equality in IDE tool commands remain unverified live.
- **Automatic-turn tracking:** the hook uses the sidecar's optional `pending` marker because Stop has no established automatic-turn flag. A grant sets it to the conversation ID; a matching marker classifies the next Stop as automatic, and an owned Stop that permits ending clears it. The established print configuration includes this set-and-clear sequence. Known limit: if a host cap or user interruption suppresses a granted continuation without another Stop, the next human turn can count once as automatic, so the no-progress guard can end continuation at most one turn early; send a further human message to reset that guard and resume.
- **Continuation limits:** the CLI cap `maxStopHookContinuations` is present in the 1.3.3 implementation. Its effective default, supported user-facing configuration route, reset behavior, behavior in 1.5.2 and the IDE's effective cap are unverified; do not invent a default or a flag to change it.
- **Completion wake:** CLI 1.3.3 supports background-task completion waking the session, including a background command that completes after the first print-mode turn; live wake behavior, including in 1.5.2, remains unverified. Exact IDE waiter wake behavior is unverified. Stop's `fullyIdle` reports whether background work remains, not whether a particular queue waiter exists.

## Devin

Register with:

```sh
python3 "$SKILL_DIR/scripts/install_hook.py" --host devin --scope "$SCOPE" --workspace "$WORKSPACE"
```

- **Configuration:** expect both `Stop` and `SessionStart`, each using matcher groups with command hooks. User scope merges under `hooks` in `~/.config/devin/config.json`; project scope writes the hooks object directly to `<workspace>/.devin/hooks.v1.json`, without an outer `hooks` key. Use these hook files; skill-frontmatter registration is unverified.
- **Activation:** with workspace trust enabled, trust the directory interactively before using print mode; print mode cannot present the prompt and fails in an untrusted directory. `--respect-workspace-trust false` skips that check and is the explicit override used by the print configuration in **Modes and continuation**.
- **Modes and continuation:** in Devin 3000.12.17 print mode (`-p`, with `-r` to resume), project hooks run with `--respect-workspace-trust false`. `Stop` fires on initial and resumed runs; a resumed run accepts `decision: "block"` and starts one automatic turn whose Stop has `stop_hook_active: true`. On resume with `stop: done`, it returns `{}` with no automatic turn. `DEVIN_PROJECT_DIR` reaches the Stop hook and names the workspace. Live continuation on an initial print run remains unverified. Interactive lifecycle hooks are documented, but live interactive parity remains unverified.
- **Owner ID:** start a new session after registration and take the ID from the SessionStart context beginning `[agent-loop] This session's ID is <id>.` The registered hook returns that context through `hookSpecificOutput.additionalContext`; use the supplied ID for `owner:`. In the print configuration in **Modes and continuation**, the agent receives this ID and it equals later Stop events' `session_id`, including after `-r` resumes the same session. Child-agent identity remains unverified live. Do not substitute an inherited Claude session variable.
- **Continuation limits:** no numeric Stop-hook continuation cap is documented; do not assume unlimited continuation. Apply the hook budget and pass 6.
- **Completion wake:** shell completion starting a new model turn is unverified. Background subagent completion notifies and resumes the parent through a separate mechanism; do not infer a shell-waiter wake from it.
