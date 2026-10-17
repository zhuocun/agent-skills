---
name: backend-cr
description: >-
  Use when reviewing existing backend code, a scoped backend change, or its
  tests for correctness, authorization, data integrity, failure behavior,
  concurrency, compatibility, and verification quality. Do not use for designing
  a system architecture from scratch, whole-system architecture audits, or
  architecture-only assessment of boundaries, layering, dependency direction,
  domain models, ports and adapters, design decisions, or overdesign; route
  those requests to architecture design and review. Do not use for
  frontend-only or prose-only reviews.
---

# Backend Code Review

Review backend code, a backend diff, or its tests, and report the defects that would otherwise reach production, with few false alarms. Report a defect only when you can show a reachable trigger that breaks a located contract, and give each its location, trigger, consequence, evidence and the narrowest fix. Judge the code against the project's established responsibilities and contracts; do not design a new architecture. Reviewing grants no permission to change code, data or services.

Priority order: **effective requirements and evidence > authorization, data integrity and business correctness > failure, retry and concurrency behavior > compatibility and deploy safety > test adequacy > necessary simplicity and maintainability > style**. Explicit user or project requirements override the defaults in this skill.

## Rules that always apply

- **Investigate read-only.** Do not read credentials or environment files, write to databases, or start or stop shared services. Before running a command, check what it reads, initializes, writes and cleans up; test commands often load environment files or reset data. If you need one of these actions, stop and ask for that specific permission. Permission to run tests never covers resetting live or shared data.
- **Review, do not remediate.** Report findings and the steps that would accept a fix. Change code or run operational actions only under separate, explicit permission. A check you did not run is pending, not passed.
- **Keep every fix inside the established architecture.** Propose repairs that keep the current boundaries, layers, dependency direction, ports and ownership, in whatever style the project uses. Put a repair with the code that owns the rule. If a correct fix needs an architecture change, name it as a separate owner decision that needs explicit approval; do not fold it into the fix. Do not invent layers, objects or ports to match this skill's vocabulary, and do not block a fix because architecture documentation is missing.
- **Report edge cases only when the contract covers them.** Before reporting an extreme input, an unusual stored value or a missing defensive check, find the contract that says this input reaches this code. Not being able to rule an input out is not proof that it is covered. Uncovered hardening is a suggestion, not a defect, unless an authorization or data-integrity obligation requires it.
- **Scale to the change.** Run every step of the hunt, but answer only the questions that apply to the code in front of you, and say briefly which areas do not apply. Do not infer risk from line count. Do not recommend a mechanism only because this skill names it.
- **Do not invent limits.** When a judgment needs a number (latency, batch size, retention window) and no source gives one, name the owner who must decide and the conclusion that depends on it.

## What counts as a contract

A contract is a stated or established expectation you can point to. Look for these, in this order:

1. The user's request, the ticket, the requirement or design document for this change.
2. API schemas, interface documentation, comments, and names that promise behavior (`reserveOnce`, `idempotencyKey`, `amountCents`).
3. Database schema: constraints, column types, defaults, unique keys.
4. Existing tests, and the behavior of the released version that callers rely on.
5. Project rules: coding standards, error-code catalogs, review policies.

Every backend also carries these baseline obligations, which count as contracts when the code makes them reachable:

- A caller reads or changes only data their identity is allowed to reach.
- An accepted write is not lost, half applied, or silently overwritten by a stale value.
- A retried or redelivered request does not repeat money movement, messages, or inserts that must happen once.
- Other systems never see an effect for data that was not committed.
- A dependency or processing failure is never reported as success, an empty result, or "not found".
- During a rolling deploy or rollback, old and new versions both work with the data and messages the other writes.
- Money is computed exactly in the currency's units with the stated rounding rule.
- A paged or filtered list returns each item it promises, once, in the stated order.
- The number of queries or remote calls per request does not grow with the size of a user-controlled or data-sized list.
- A test that claims to cover a behavior fails when that behavior breaks.

If the contract is unclear and none of these obligations settles it, the candidate is Uncertain, not Confirmed.

## Step 1: Map the change

1. Identify the revision or diff, the stated requirements, and any earlier review comments you must re-check.
2. Read the whole diff. Then read the code each changed line calls and the code that calls it, far enough to see the guards around it: middleware, decorators, interceptors, policy checks, repository filters, transaction wrappers, database constraints, and callers that already validate.
3. Write a short inventory in your notes, one line per changed entry point (endpoint, handler, job, consumer, command, migration):
   - who calls it and how their identity is obtained;
   - what it reads and what decision it makes from those reads;
   - each write, and the transaction it runs in;
   - each external call or publish (payment, email, HTTP, queue, cache, file, other service), and whether it happens before, inside or after the commit;
   - each error handler;
   - each migration, schema, configuration or message-format change;
   - the tests that cover it.
4. Note what you could not see (code outside the diff you were not given, configuration, other services). These are coverage gaps; list them in the report.
5. If the user or project fixes a strict boundary, do not inspect or judge code outside it; record what lies outside as not covered.

## Step 2: Hunt

Go through the inventory entry by entry. For each entry, answer the questions below in order. Each section lists common defect signs and look-alikes that are usually correct. Before reporting a sign, find out whether a look-alike applies.

### 2.1 Authorization and input

- Where does the caller's identity come from? It must come from the authenticated session or a verified token. Treating a user ID, tenant ID or role from the body, query string or a client-set header as the caller's own identity is a defect. An ID that names the target object is normal; the next question checks it.
- For each object the request reads or changes, where is the check that this caller may act on this object (owner, tenant, role, object state)? Check that it tests the object actually loaded and written, not a different ID from the request.
- Does the check run before any write, publish or external call? After a rejection, does the code stop with no write, event or external call?
- Do all entries that reach the same operation carry the same check: the batch endpoint, the admin route, the job, the second handler that calls the same service?
- For nested resources, is the child tied to the parent the caller was checked against (`/orders/{orderId}/items/{itemId}` must confirm the item belongs to that order)?
- Do lists, searches and counts apply the caller's scope before filtering, counting and paging?
- Does the server validate type, required fields, ranges and business rules for every value the client can edit? Client-side checks do not count.
- When the client sends credentials automatically (cookies), does each state-changing request pass the project's existing origin or request-binding check?
- When several checks fail at once, does the first error returned match the contract? Check error order only when a contract states it.

Defect signs: lookup by ID with no owner or tenant filter; role checked on one route but a second route to the same service skips it; check placed after the update; the same business rule coded twice with different limits; a confirmation step that is not bound on the server to the object, the actor and the current state.

Usually correct: the check lives in middleware, a decorator, a policy object, a tenant-scoped repository or a database row rule; internal jobs using a service identity the project defines; public read-only data. Find the guard before reporting its absence.

### 2.2 Reads, decisions and concurrent writes

For every write that depends on something read earlier (a balance, stock count, status, quota, "does this already exist"), ask: two requests arrive at the same moment and both read the old value; what is stored afterward?

The write is protected when one of these holds:

- it is a single conditional statement (`UPDATE stock SET qty = qty - 1 WHERE id = ? AND qty >= 1`) and the code checks the affected row count;
- a version column is compared in the `WHERE` clause and a zero-row result is handled as a conflict;
- a row lock (`SELECT ... FOR UPDATE`) is taken in the same transaction as the write and held until commit;
- a unique constraint enforces a check-then-insert;
- the transaction is serializable and the code retries on serialization failure.

Defect signs: read, compute in application code, then write the whole value back (lost update); check-then-insert with no unique constraint (duplicates); version read but not used in the `WHERE`; affected row count ignored; lock taken in a different transaction from the write; an in-process lock or mutex guarding data shared by several instances; an invariant across several rows (a total, a schedule with no overlaps) protected only by one row's version; mutable shared memory (static fields, singletons, module-level maps) changed by concurrent requests without synchronization.

Usually correct: last-writer-wins where the contract allows it (a display name, a preference); an atomic increment in the database; a precheck kept for a clear error message while a constraint does the final enforcement.

### 2.3 Transactions and partial failure

- List the writes that must succeed or fail together. Are they in one transaction on one connection?
- Is the transaction really active where you think? Check self-invocation that bypasses a transaction decorator, a second connection or session, autocommit mode, and work handed to another thread or async task.
- For each point that can fail between two writes, what stays committed or visible?
- Does a catch inside the transaction swallow the error and let a partial write commit?
- On a commit timeout or lost response, does the code treat "unknown" as "failed" and repeat a write that must happen once? Unknown outcomes need a lookup or a safe replay.
- Does any path "undo" committed data by deleting it instead of using the contracted follow-up or compensation?

Defect signs: two saves with no transaction around them; a slow external call inside the transaction while row locks are held (rate by impact); a validation that runs after the first write, so a rejection leaves the first write in place.

Usually correct: a single-statement write; logs and metrics written outside the atomic set; a follow-up step the contract says a retrying job completes.

### 2.4 External calls, events and commit order

For each external call or publish in the inventory, place it relative to the commit and ask:

- **Before or inside the commit.** If the transaction then rolls back, the email is sent, the payment taken or the event published for data that does not exist. This is a defect when anyone acts on it.
- **After the commit, with no durable record.** A crash between commit and send loses the effect. This is a defect when the contract requires delivery; the usual fix is the project's outbox or retry mechanism.
- **Remote succeeded, local failed.** The remote effect remains. Is there compensation or a later reconciliation?
- **Response lost (timeout).** The remote side may have done the work. A blind retry repeats it unless the call carries an idempotency key the remote side honors.
- **Message acknowledged before the effect is durable.** A crash after the ack loses the message.

Usually correct: an outbox row written in the same transaction and published by a relay; an after-commit hook where the contract accepts occasional loss; read-only external calls.

### 2.5 Retry, redelivery and duplicates

Ask: the client, a proxy, the job scheduler or the queue sends the same request twice, possibly while the first is still running. What happens?

- If the effect is naturally idempotent (set status to X, upsert by natural key), it is fine.
- If not (charge, send, insert, increment), check the duplicate guard: Is there an idempotency key? Is it enforced by a unique constraint, written in the same transaction as the effect? Is it scoped to the caller? Does a reused key with different content get rejected? Does a replay return the stored result? Is an in-progress record kept from being reported as completed success? Does retention cover the retry window the contract promises?
- Queue consumers: assume at-least-once delivery unless the project's broker contract says otherwise. Is the handler idempotent or deduplicated by message ID?
- Internal retry loops: Do they retry only errors known to be transient and operations safe to repeat? Are attempts bounded with backoff? Does each attempt start a fresh transaction? Does a retry repeat a call whose first outcome is unknown?

Usually correct: retries of reads; retries of an idempotent PUT; a deduplication row with a unique key inserted in the same transaction as the effect.

### 2.6 Errors and cleanup

For each catch, except, recover or error return, say what it does. It is correct when it recovers with a fallback the contract allows, compensates, translates to the contract's error while keeping the cause, or adds context and rethrows.

Defect signs: catch, log and return success, an empty list, a default or `null`; a dependency failure turned into "not found" or "no permissions", so the caller acts on a false fact (creates a duplicate, denies or grants access, deletes); a broad catch that also hides programming errors; the wrong error class or status code (500 for a validation error, 200 with an error body, 404 where the contract says 403); a `finally` block or cleanup error that replaces the original error; a resource not closed on an early return; an ignored error return or an un-awaited async call.

Usually correct: a catch that rethrows with context; a failure of best-effort telemetry that the design deliberately ignores; catching one specific expected error (duplicate key → return the existing record) when the contract describes exactly that.

### 2.7 Money, numbers, time and text

- **Money.** Binary floating point (`float`, `double`, a JavaScript `number` with fractions) for amounts that are stored, charged, compared or summed is a defect; use decimal types or integer minor units. Check: currency minor units (JPY has 0 decimals, KWD has 3); the rounding mode and where rounding happens (per line or on the total, as the contract says); that split parts add up to the total (allocate the remainder); integer division that truncates; overflow of 32-bit cents; the sign of refunds and credits; the order of conversion and rounding.
- **Numbers.** Units (milliseconds versus seconds, cents versus units), percentages as 0.15 versus 15, division by zero, parse failures, values out of range for the column type.
- **Time.** Store instants in UTC. Apply date-only business rules (due today, end of month) in the time zone the contract names. Check daylight-saving changes, month ends, leap days, and whether an end time is inclusive or exclusive. Do not compare clocks of different machines as if they were one clock.
- **Text.** Normalize case and whitespace the same way on write and on lookup. Check database collation, and whether a length limit counts bytes or characters.

Usually correct: floats for ratios, scores and metrics that are not money; rounding only for display when stored values are exact.

### 2.8 Boundaries, lists and pagination

- Test each comparison at its edge: `<` versus `<=`, an inclusive end date, a count exactly at the limit, zero items, one item, the last page.
- Pagination: the sort order must be total; add a unique tiebreaker such as the ID. A cursor must encode every sort key and compare in the same direction as the sort. Offset paging under concurrent inserts can skip or repeat rows; this is a defect only when the contract promises a stable listing. The server must cap page size. "Has more" must be right when exactly `limit` rows remain: fetch `limit + 1` rather than testing `rows == limit`. Apply the caller's scope before counting and paging.
- Batches and collections: enforce maximum sizes; handle an empty `IN ()` list; handle duplicate IDs in the input; report errors with the input's original positions when the contract asks for them.

Usually correct: offset paging on an internal list with no stability promise.

### 2.9 Queries and load

- **Per-item queries (N+1).** A query or remote call inside a loop over a result whose size grows with data or user input. Rate it Major on a request path that serves user-sized lists and Minor elsewhere. Usually correct: a loop bounded by a small constant, a batched `IN` fetch, eager loading configured in the ORM, a per-request cache.
- **Unbounded work.** A user-driven query with no limit; a whole table loaded into memory; a new filter on a large table with no index. Cite the schema; do not guess.
- **Values in statements.** Client values must reach SQL, shell commands, file paths and URLs as bound parameters or validated values, not pasted into the statement text. Pasted values break on quotes and change what the statement does.
- **Timeouts.** Every external call needs a timeout. Retries at several layers multiply (3 × 3 × 3 = 27 attempts); a retry gets only the remaining time of the original request.

### 2.10 Compatibility, deploys and migrations

Assume that during a rolling deploy the old and new versions run at the same time, and that a rollback runs old code against data the new code wrote.

- **Migrations.** Adding a NOT NULL column with no default to a table old code still inserts into; renaming or dropping a column or table old code still reads; changing a column type; a new enum value old readers reject; a long-locking change on a large table; a backfill that overwrites rows written after it started; a migration that fails when re-run. The safe pattern is expand then contract: add the nullable or defaulted column, deploy code that handles both, backfill, and remove the old shape in a later release.
- **APIs and messages.** Removing or renaming a field; changing a field's meaning, unit or default; making an optional request field required; a decoder that rejects unknown fields, so an added field breaks old readers. Messages already queued by the old version must still be processed by the new one, and new messages must be readable by old consumers still running.
- **Configuration and flags.** Check the value used when a setting is missing, and both branches of a switch. Turning a flag off must stop the effect, not just hide the entry point.
- **Removal.** Before removing a field, method or endpoint, search every caller, including reflection, configuration, scheduled jobs and other services. Zero local callers does not prove nobody external uses it; report unknown consumers.
- **Released behavior.** A claim that released behavior is preserved needs a comparison with the released artifact or an approved equivalent, not a development branch. If that comparison is unavailable, record it as a pending gate with an owner.

Usually correct: an added nullable column; an added optional response field when clients ignore unknown fields.

### 2.11 Tests

For each changed behavior and each new or changed test, ask: if the change were reverted or the guard deleted, would a test fail?

Defect signs: no assertion; asserting only not-null, no exception or status 200; an expected value computed by the code under test; a mock that returns a value the test then asserts back; verifying a mock call but never the result or stored state; a catch in the test that swallows failures; a disabled test; fixed sleeps or identical payloads standing in for a concurrency test; a test name that promises a behavior the assertions do not check; only the happy path for a change that adds a rejection.

A missing test is a test-adequacy finding, not a production defect, unless a project rule requires the test. A test that claims to cover a behavior but cannot fail is a finding; rate it by what it lets through. Say exactly which tests or commands you ran, on which revision, and with what result; reading code is not running it.

### 2.12 Deeper checks

Open [Risk Checks](references/risk-checks.md) only for a section whose trigger appears in the inventory.

| Trigger in the change | Section in Risk Checks |
| --- | --- |
| Clocks across machines, leases, expiry; collection identity and limits | Values, Time and Collections |
| Locks, connection pools or waits on other work; deduplication facilities | Concurrency and Progress |
| Queues, jobs, async commands, leases on work, compensation, resource lifetimes | Asynchronous Work and Recovery |
| Deadlines, expensive input, shared capacity, retry chains | Budgets and Capacity |
| An existing cache, or an offline data investigation | Caches and Diagnostics |
| Client values reaching queries, files, processes or deserialization; personal or secret data | Data Protection and Technical Operations |
| Live migration of retained data, destructive conversion, rollback, dynamic configuration | Migration, Release and Configuration |
| Protocol or format changes, released-behavior preservation | Compatibility Evidence |
| Failure logging, or a silent failure that could hide accepted work | Logs and Detection |
| Direct or transitive dependency upgrades | Dependency Upgrades |
| Concurrency, failure or numeric claims that need stronger test evidence | Test Evidence |

## Step 3: Verify each candidate

Before a candidate becomes a finding, try to disprove it as if someone else had raised it. Do this for your own candidates and for every earlier review comment you were asked to re-check.

1. **Name the contract.** Quote or cite where it is stated, or name the baseline obligation above.
2. **Write the trigger.** Give the concrete input, state or timing, entering through a real entry point, that reaches the line. "Could be null" is not a trigger; "`POST /refunds` accepts `amount: \"19.99\"`, line 88 parses it as a double and truncates `amount * 100` to an integer, so 1998 cents are refunded instead of 1999" is.
3. **Search for the defense.** Look in middleware, decorators, the caller, the database schema, the transaction wrapper, the framework's defaults and the tests. If a defense stops the trigger, drop the candidate.
4. **Trace the consequence.** Say what goes wrong, for whom, and whether it can be recovered.
5. **Classify.** Confirmed: the trigger is reachable and violates a located contract. Uncertain: the trigger is reachable but the contract, or one decisive fact, is missing; name what is missing. Not substantiated: a defense stops it, the path is unreachable, or no contract or obligation covers it. Impact, experience, a missing test or a hypothetical caller alone is not enough to confirm.

If a project rule requires a reviewer other than the proposer to verify findings, record that check as a pending gate. A pending verifier does not downgrade a demonstrated defect.

## Step 4: Rate severity

Rate by impact and reachability, not by style or the absence of tests. A project's own severity scheme overrides this one.

- **Blocker:** reachable through normal use or routine conditions (a retry, two concurrent users, a deploy) and causes unauthorized access, data loss or corruption, wrong money, a duplicate irreversible effect, or an outage or failed deploy.
- **Major:** a wrong result or failure with limited scope or easy recovery, or a Blocker-class impact that needs uncommon but realistic conditions; a severe slowdown on a hot path.
- **Minor:** small impact, rare conditions, simple recovery.

## Step 5: Propose the fix

- Give the narrowest fix that removes the trigger, inside the established architecture (see Rules). Keep behavior and robustness: do not remove valid validation, error classification, concurrency guards or negative tests as duplication.
- Give the acceptance steps in order: a test that fails on the current revision for the target behavior; the minimal complete fix; the same test passing; review of the fix by someone other than its author; the project's quick checks, and its release checks before release.
- For an Uncertain candidate or an open business choice, state the question, the evidence, the owner, and three options with consequences: change the code, document the current behavior, or leave it unchanged. Documenting or leaving unchanged cannot waive a mandatory requirement. An approved exception must name its approver, scope and expiry; a single exception does not waive its whole category.

## Step 6: Report

Use the compact report for one bounded change. Use the full report when the review spans several independent concerns or the user or project asks for it. Write "None" for an area you checked and found clean, and "Not checked: <reason>" for one you did not check. Do not add sections that would be empty.

Compact report:

```
Verdict: Mergeable | Mergeable after fixes: F1, F2 | Not mergeable: F1
Scope: <revision or diff>; entry points reviewed; not covered: <what and why>

Findings
F1 [Blocker] <one-line title>
  Location: <file:line, plus related lines>
  Trigger: <concrete input, state or timing, through which entry point>
  Contract: <what must hold, and where it is stated>
  Consequence: <what goes wrong, for whom, recoverable or not>
  Evidence: <decisive code facts; tests or commands run and their results>
  Fix: <narrowest change within the current design>
  Verify: <test that fails now and passes after the fix>

Uncertain
U1 <question> — owner: <who decides>; missing: <fact or contract>; options: change code / document / leave as is, with consequences

Test gaps and suggestions (not defects)
- <item>

Checked, no finding: <areas from Step 2 that applied and were clean>
Candidates: <n> checked — <c> confirmed, <u> uncertain, <d> not substantiated
Checks run: <commands and results, or "none; review by reading">
Pending gates: <required checks or approvals not yet done, each with an owner>
```

Order findings by severity. Keep Uncertain items and suggestions out of the findings list. Do not keep a weak candidate in the report as a suggestion to hedge; if it is not substantiated, count it and leave it out. List at most three suggestions.

The full report uses the same finding format and adds:

1. A coverage map: each stated requirement mapped to the code, the evidence and the conclusion, with missing, inapplicable and unverified items marked.
2. For each independent concern: its scope, entry points, contracts, who reviewed it, and its findings and gaps.
3. Every candidate with its disposition and the decisive reason.
4. Owner decisions with the options above.
5. Remediation and release steps: acceptance tests, reviewer role, quick and release checks, and for a released fix the signal to watch after release, its owner and the stop condition.
6. Compatibility evidence when Step 2.10 applied: old and new sender and receiver pairs, how samples were produced, and the released-behavior comparison as its own gate.

Recommend acceptance only within what you verified. Never recommend an unconditional merge while a mandatory requirement is unmet or decisive evidence is missing. A clean review does not prove a fix, a release or production behavior.

## Self-check

- [ ] Every finding has a location, a concrete reachable trigger, a located contract or baseline obligation, a consequence, evidence and the narrowest fix.
- [ ] For every finding I searched for an existing defense (middleware, constraint, caller, transaction wrapper, framework default) and found none that stops the trigger.
- [ ] I went through every inventory entry for authorization, concurrent writes, transactions, commit order, retries, errors, money and numbers, boundaries and pagination, queries, deploy and migration compatibility, and tests, and noted which do not apply.
- [ ] Edge-case findings rest on a contract that covers the input; uncovered hardening is listed as a suggestion.
- [ ] Uncertain items name the missing fact, the owner and the options; they are not in the findings list.
- [ ] Every proposed fix stays inside the established architecture, and any needed architecture change is named as a separate owner decision.
- [ ] I changed no code, data or services and read no credentials or environment files; checks I did not run are marked pending.
- [ ] The report is the compact form for a single bounded change, ordered by severity, with no empty sections.
