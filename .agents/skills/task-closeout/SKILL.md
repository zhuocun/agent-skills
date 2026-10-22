---
name: task-closeout
description: >-
  Complete task housekeeping by verifying outcomes, reconciling records and
  documentation, preserving evidence, cleaning working resources, and handing off
  remaining work. Use when finishing or wrapping up a task, before declaring done,
  switching tasks, or ending a session. Do not use for code review, prescribing a
  status report format, or routine mid-task progress updates.
---

# Task Closeout

Bring the deliverables, records, documentation, and working resources into agreement with the task's actual state. Run applicable checks in pass order for software, document, data, or other work. Skip absent surfaces without creating new infrastructure solely for closeout.

Priority order, highest first: **preserve work and respect authorization → verify actual state → reconcile records → synchronize documentation → clean resources → hand off accurately.**

## 1. Verify scope and outcomes

Read the agreed outcome, acceptance requirements, current instructions, and existing authorizations. Identify unfinished delivery and housekeeping work. When switching tasks or ending a session with work unfinished, preserve its state and instructions for resuming it.

Inspect deliverables where they actually live or run. In version control, distinguish uncommitted changes, local commits, pushed changes, merged changes, and deployments. Match checks to the revision and environment they tested. Mark partial outcomes and unverified claims explicitly; memory and tracker entries do not prove completion.

Use authorization already given for the actions it covers. Obtain missing authorization before outward-facing or irreversible actions, including pushing, merging, publishing, deploying, sending external messages, or deleting resources. Continue independent authorized work while a decision is pending.

Before sharing, inspect task artifacts, logs, reports, and commits for credentials, tokens, and other secrets. Redact secrets from shared material and remove them from task scratch files. If a secret appears in a commit or an already delivered record, keep affected sharing pending until authorized remediation is verified.

## 2. Reconcile records and deliveries

Compare the task tracker and the task's own status document with pass 1. Mark verified parts complete and reopen parts incorrectly marked complete. Append verified execution results and evidence to the task's log. Reserve overall task closure for pass 7.

Confirm required feedback submissions, reports, and notifications through the receiving system's response or receipt. For an ambiguous response, check delivery status before retrying to avoid duplicates. Retry failed or unconfirmed deliveries through an authorized alternative route when safe; leave them open when available routes fail or delivery remains uncertain. Label reconstructed submissions as backfills and include only recoverable facts; leave unknown fields unfilled or explicitly unknown.

## 3. Synchronize documentation and identify propagation

Update affected current specifications, designs, rules, guides, indexes, and changelogs. For renamed or removed terms, search current documentation and relevant source material, including code when applicable, until no stale references remain. Leave historical and archived records unchanged. Before removing duplicate or superseded copies, verify that the retained copy has identical content and repair references to the removed copy.

Identify copies, mirrors, consumers, and dependent branches that need the change. Synchronize them within the authorized scope and list any outstanding propagation explicitly.

## 4. Preserve evidence

Retain artifacts needed for reconciliation, pending deliveries, or the handoff before cleaning temporary resources. Keep files linked from records or the final report at reachable, retained locations; repair links when moving them.

## 5. Clean working resources

Inventory resources created for this task and retain those needed for unfinished work. Apply these checks before removal:

- **Temporary worktrees, checkouts, and scratch directories:** Confirm version-controlled changes are committed and merged or pushed, with no uncommitted work. Inspect untracked and ignored files for unique work, and preserve needed scratch content elsewhere. Ask before deleting anything holding unique work or outside the existing authorization. Use non-forcing removal and stop if the tool refuses. Keep branches unless explicitly instructed to remove them.
- **Background work and locks:** Stop task-owned processes, servers, watchers, and remaining agent runs without stopping unrelated work. Release locks only through their owning tool; never delete shared lock files.
- **Shared or external data:** Remove only test data you created, within the authorization from pass 1. Leave data created by others untouched. Record data or irreversible states that cannot be removed for the owner's attention.
- **Capacity after heavy work:** Check applicable disk space, inode, and quota headroom where available. If capacity is constrained, propose cleanup using measured usage and remaining capacity.

## 6. Capture lessons and follow-up work

Record reusable lessons and confirmed user preferences in the existing persistent memory or knowledge store, when available. Keep task-specific state in task records. Present proposed instruction or tooling improvements separately from confirmed lessons.

Register unresolved work as follow-up tasks in the authorized tracker, with an owner or an explicit ownership gap, a next action, and relevant evidence. If no tracker is available, retain these items in the handoff.

## 7. Finalize closure and hand off

Recheck any outcome changed during closeout. Close the overall task in its tracker and status document only after required work, including documentation and cleanup, is finished, the owner explicitly accepts the result, and required closing commands succeed. Verify the resulting recorded status and append the completion record. If a closing condition is unmet, leave the task open and state why.

Report concisely to the owner: verified outcomes with evidence, outstanding work and propagation, residual risks, unverified items, retained resources or data that could not be removed, and decisions or authorizations still needed. Use the report form the task requires, if any.

## Self-check

- [ ] Pass 1: Scope, acceptance requirements, and existing authorizations were read; unfinished work has resumption notes, and outcome claims match the actual revision, destination, and verification environment.
- [ ] Pass 1: Actions stayed within existing authorization, independent authorized work continued while decisions were pending, shared material and scratch files contain no detected secrets, and affected sharing awaits verified remediation where required.
- [ ] Pass 2: Available task records and execution logs match verified progress; delivery receipts were checked, retries avoided duplicates, and failed or uncertain deliveries remain open with backfills limited to recoverable facts.
- [ ] Pass 3: Affected current documentation is consistent, searches found no stale renamed or removed references, historical records are unchanged, removed copies have identical retained content and repaired references, and propagation is completed or listed.
- [ ] Pass 4: Artifacts needed for reconciliation, pending deliveries, or handoff were retained, and linked evidence remains reachable after any moves.
- [ ] Pass 5: Removed resources passed the preservation and authorization checks, branches were kept unless removal was explicit, removal used no force, only task-owned work stopped, locks used their owning tools, only self-created test data was removed, and constrained capacity after heavy work has measured cleanup proposals.
- [ ] Pass 6: Available durable storage holds reusable lessons and confirmed preferences rather than task state; proposed improvements are separate, and unresolved work is tracked or retained in the handoff with ownership and next actions.
- [ ] Pass 7: Closure meets every stated condition and has a verified status and completion record, or the task remains open with the reason; the handoff includes evidence, outstanding work, risks, unknowns, retained resources or data, and required decisions.
