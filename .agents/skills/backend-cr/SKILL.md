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

Review backend code, a backend diff, or its tests, and report the defects that would otherwise reach production, with few false alarms. Report a defect only when a reachable trigger breaks a located contract. Judge the code against the project's established responsibilities and contracts; do not design a new architecture.

Priority order: **effective requirements and evidence > authorization, data integrity and business correctness > failure, retry and concurrency behavior > compatibility and deploy safety > test adequacy > necessary simplicity and maintainability > style**. Explicit user or project requirements override this skill's defaults.

## Rules that always apply

- **Investigate read-only.** Do not read credentials or environment files, write to databases, or start or stop shared services without that specific permission. Before running a command, check what it reads, writes and cleans up; test commands often load environment files or reset data, and permission to run tests never covers resetting live or shared data. Record `git status` and diff stats before and after, and report any change you did not make.
- **Review, do not remediate.** Report findings and how to accept a fix; change code or run operational actions only under separate, explicit permission. A check you did not run is pending, not passed.
- **Keep every fix inside the established architecture.** Keep the current boundaries, layers, dependency direction, ports and ownership, and put a repair with the code that owns the rule. If a correct fix needs an architecture change, name it as a separate owner decision needing explicit approval; do not fold it into the fix. Do not invent layers, objects or ports, or block a fix because architecture documentation is missing.
- **Report edge cases, hardening and performance only when a contract covers them.** Before reporting an extreme input, an unusual stored value, a missing check or limit, or a slow path, find the contract or sourced limit that requires it; failing to rule an input out is not proof. Without one it is a suggestion, unless an authorization or data-integrity obligation requires it.
- **Scale to the change.** Run every step, answer the questions that apply, and say briefly which areas do not. Do not infer risk from line count or recommend a mechanism only because this skill names it.
- **Do not invent limits.** When a judgment needs a number (latency, page size, retention) and no source gives one, name the owner who must decide and the conclusion that depends on it.

## Step 1: Map the change

1. Identify the revision, the stated requirements, and earlier review comments to re-check.
2. Read the whole diff, then the code each changed line calls and the code that calls it, far enough to see the guards: middleware, decorators, interceptors, policy checks, repository filters, transaction wrappers, database constraints, and callers that already validate.
3. Name the requirement each changed block serves. A change in outputs, error codes, error order, defaults or side effects that no requirement asks for is a candidate; its contract is the released behavior callers rely on (source 4 in Step 3).
4. Write an inventory in your notes, one line per changed entry point (endpoint, handler, job, consumer, command, migration): the caller and how their identity is obtained; what it reads and decides; each write and its transaction; each external call or publish (payment, email, HTTP, queue, cache, file, other service) and whether it runs before, inside or after the commit; each error handler; each migration, schema, configuration or message-format change; the tests that cover it.
5. List what you could not see (code you were not given, configuration, other services) as coverage gaps. Under a strict boundary set by the user or project, do not inspect or judge code outside it; record it as not covered.

## Step 2: Hunt

For each inventory entry, answer the questions below in order. Before reporting a defect sign, check whether a usually-correct look-alike applies. A sign or a "Candidate" is not a finding until Step 3 confirms it.

### 2.1 Authorization and input

- Where does the caller's identity come from? It must come from the authenticated session or a verified token; taking the caller's user ID, tenant ID or role from the body, query string or a client-set header is a defect. An ID naming the target object is normal; the next question checks it.
- For each object read or changed, where is the check that this caller may act on it (owner, tenant, role, object state)? Does it test the object actually loaded and written, not another ID from the request?
- Does the check run before any write, publish or external call? After a rejection, does the code stop with no write, event or external call?
- Does every entry to the same operation carry the same check: the batch endpoint, the admin route, the job, a second handler calling the same service?
- Is a nested child tied to the parent the caller was checked against (`/orders/{orderId}/items/{itemId}` must confirm the item belongs to that order)?
- Do lists, searches and counts apply the caller's scope before filtering, counting and paging?
- Does the server validate type, required fields, ranges and business rules for every client-editable value? Client-side checks do not count. Do not report missing validation for values the server derives or trusted construction already guarantees.
- With automatically sent credentials (cookies), does each state-changing request pass the project's origin or request-binding check?
- When several checks fail at once, does the first error returned match the contract? Check error order only when a contract states it.

Defect signs: lookup by ID with no owner or tenant filter; a role checked on one route but skipped on a second route to the same service; check placed after the update; one business rule coded twice with different limits; a confirmation step not bound on the server to the object, the actor and the current state.

Usually correct: the check lives in middleware, a decorator, a policy object, a tenant-scoped repository or a database row rule; internal jobs using the project's service identity; public read-only data. Find the guard before reporting its absence.

### 2.2 Reads, decisions and concurrent writes

For every write that depends on an earlier read (a balance, stock count, status, quota, "does this already exist"), ask: two requests both read the old value at once; what is stored afterward? The write is protected by one of:

- a single conditional statement (`UPDATE stock SET qty = qty - 1 WHERE id = ? AND qty >= 1`) whose affected row count is checked;
- a version column compared in the `WHERE`, with zero rows handled as a conflict;
- a row lock (`SELECT ... FOR UPDATE`) taken in the write's transaction and held until commit;
- a unique constraint enforcing a check-then-insert;
- a serializable transaction retried on serialization failure.

Defect signs: read, compute in code, write the whole value back (lost update); check-then-insert with no unique constraint (duplicates); version read but not used in the `WHERE`; affected row count ignored; lock taken in another transaction than the write; an in-process lock guarding data shared by several instances; a rule across rows (a total, no overlapping bookings) protected only by one row's version; shared mutable memory (static fields, singletons, module-level maps) changed concurrently without synchronization.

Usually correct: last-writer-wins where the contract allows it (a display name, a preference); an atomic database increment; a precheck for a clear error message while a constraint enforces.

### 2.3 Transactions and partial failure

- Are the writes that must succeed or fail together in one transaction on one connection?
- Is the transaction really active? Check self-invocation bypassing a transaction decorator, a second connection or session, autocommit, and work handed to another thread or async task.
- If it fails between two writes, what stays committed or visible?
- Does a catch inside the transaction swallow the error and let a partial write commit?
- On a commit timeout or lost response, does the code treat "unknown" as "failed" and repeat a write that must happen once? Unknown needs a lookup or safe replay.
- Does any path "undo" committed data by deleting it instead of the contracted compensation?

Defect signs: two saves with no transaction; a slow external call inside the transaction while row locks are held (rate by impact); a validation after the first write, so a rejection leaves that write in place.

Usually correct: a single-statement write; logs and metrics outside the atomic set; a follow-up the contract says a retrying job completes.

### 2.4 External calls, events and commit order

Place each external call or publish relative to the commit:

- **Before or inside the commit.** On rollback, the email, payment or event exists for data that does not; a defect when anyone acts on it.
- **After the commit, with no durable record.** A crash between commit and send loses the effect; a defect when the contract requires delivery (usual fix: the project's outbox or retry mechanism).
- **Remote succeeded, local failed.** Is there compensation or reconciliation for the remote effect?
- **Response lost (timeout).** The remote side may have done the work; a blind retry repeats it unless the remote side honors an idempotency key.
- **Message acknowledged before the effect is durable.** A crash after the ack loses the message.

Usually correct: an outbox row in the same transaction, published by a relay; an after-commit hook where the contract accepts occasional loss; read-only calls.

### 2.5 Retry, redelivery and duplicates

Ask: the client, a proxy, the scheduler or the queue sends the same request twice, possibly while the first still runs. What happens?

- A naturally idempotent effect (set status to X, upsert by natural key) is fine.
- Otherwise (charge, send, insert, increment), check the duplicate guard: an idempotency key enforced by a unique constraint in the effect's transaction, scoped to the operation and caller; a reused key with different content rejected; a replay returning the stored result; an in-progress record never reported as completed; retention covering the promised retry window.
- Queue consumers: assume at-least-once delivery unless the broker contract says otherwise. Is the handler idempotent or deduplicated by message ID?
- Internal retry loops: only transient errors and operations safe to repeat? Bounded attempts with backoff? A fresh transaction per attempt? No repeat of a call whose outcome is unknown?

Usually correct: retried reads or idempotent PUTs; a unique-keyed deduplication row inserted with the effect.

### 2.6 Errors and cleanup

For each catch, except, recover or error return, say what it does. It is correct when it uses a fallback the contract allows, compensates, translates to the contract's error keeping the cause, or rethrows with context.

Defect signs: catch, log and return success, an empty list, a default or `null`; a dependency failure turned into "not found" or "no permissions", so the caller acts on a false fact (duplicates, denies or grants access, deletes); a broad catch that also hides programming errors; the wrong error class or status code (500 for a validation error, 200 with an error body, 404 where the contract says 403); a `finally` block or cleanup error that replaces the original error; a resource not closed on an early return; an ignored error return or an un-awaited async call.

Usually correct: rethrowing with context; deliberately ignored best-effort telemetry failures; catching one expected error the contract describes (duplicate key → return the existing record).

### 2.7 Money, numbers, time and text

- **Money.** Binary floating point (`float`, `double`, a JavaScript `number` with fractions) for amounts stored, charged, compared or summed is a defect; use decimals or integer minor units. Check: currency minor units (JPY 0 decimals, KWD 3); the rounding mode and where it happens (per line or on the total, per the contract); split parts adding up to the total (allocate the remainder); integer division that truncates; overflow of 32-bit cents; the sign of refunds and credits; the order of conversion and rounding.
- **Numbers.** Units (milliseconds versus seconds, cents versus units), percentages as 0.15 versus 15, division by zero, parse failures, values out of range for the column type.
- **Time.** Candidate: an instant stored in local time or with no offset; confirm it when the schema, a contract or another reader expects UTC. Apply date-only rules (due today, end of month) in the contract's time zone. Check daylight-saving changes, month ends, leap days, and inclusive versus exclusive end times. Do not treat clocks of different machines as one clock.
- **Text.** Normalize case and whitespace the same way on write and lookup. Check collation, and whether a length limit counts bytes or characters.

Usually correct: floats for ratios, scores and metrics that are not money; rounding only for display when stored values are exact.

### 2.8 Boundaries, lists and batches

- Test each comparison at its edge: `<` versus `<=`, an inclusive end date, a count exactly at the limit, zero items, one item, the last page.
- Pagination: the sort order must be total (a unique tiebreaker such as the ID). A cursor must encode every sort key and compare in the sort's direction. Offset paging under concurrent inserts can skip or repeat rows; a defect only when the contract promises a stable listing. "Has more" must be right when exactly `limit` rows remain: fetch `limit + 1`, do not test `rows == limit`. Apply the caller's scope before counting and paging. Candidate: a page size the client can raise with no server cap.
- Batches and collections: handle an empty `IN ()` list and duplicate IDs in the input; report errors with the input's original positions when the contract asks for them. Candidate: a batch with no maximum size.

Usually correct: offset paging on an internal list with no stability promise.

### 2.9 Queries and load

- **Per-item queries (N+1).** A query or remote call inside a loop over a result whose size grows with data or user input is a candidate. Confirm it only when the list size is user- or data-driven on a request path and a contract or sourced latency limit applies; otherwise it is a suggestion. Rate it by measured or sourced impact. Usually correct: a loop bounded by a small constant, a batched `IN` fetch, eager loading configured in the ORM, a per-request cache.
- **Unbounded work and timeouts.** Candidates: a user-driven query with no limit; a whole table loaded into memory; a new filter on a large table with no index (cite the schema); an external call with no timeout; retries at several layers multiplying (3 × 3 × 3 = 27 attempts).

### 2.10 Compatibility, deploys and migrations

When the project deploys by rolling update or can roll back, assume old and new versions run together and a rollback runs old code on data new code wrote.

- **Migrations.** A NOT NULL column with no default on a table old code still inserts into; renaming or dropping a column or table old code reads; a column type change; a new enum value old readers reject; a long-locking change on a large table; a backfill overwriting rows written after it started; a migration that fails on re-run. The safe pattern is expand then contract: add the nullable or defaulted column, deploy code handling both, backfill, remove the old shape later.
- **APIs and messages.** Removing or renaming a field; changing its meaning, unit or default; making an optional request field required; a decoder rejecting unknown fields, so an added field breaks old readers. The new version must process messages the old one queued, and old consumers still running must read new messages.
- **Configuration and flags.** Check the value used when a setting is missing and both branches of a switch. Turning a flag off must stop the effect, not just hide the entry point.
- **Removal.** Before removing a field, method or endpoint, search every caller, including reflection, configuration, scheduled jobs and other services; zero local callers does not rule out external ones, so report unknown consumers.
- **Released behavior.** "Released behavior preserved" needs a comparison of inputs, outputs, defaults, failures, ordering and side effects with the released artifact or an approved equivalent, not a development branch. Keep it a separate gate; if unavailable, record it as pending with an owner. For a first release, say why it does not apply.
- **Documentation.** When behavior changes, check that the API schema, interface comments and error catalog describe the new nullability, units, failures and effects; a stale description callers rely on is a finding.

Usually correct: an added nullable column; an added optional response field when clients ignore unknown fields.

### 2.11 Tests

For each changed behavior and test, ask: if the change were reverted or the guard deleted, would a test fail?

Defect signs: no assertion; asserting only not-null, no exception or status 200; an expected value computed by the code under test; asserting back a mock's own return value; verifying a mock call but never the result or stored state; a catch in the test swallowing failures; a disabled test; fixed sleeps or identical payloads standing in for a concurrency test; a test name that promises a behavior the assertions do not check; only the happy path for a change that adds a rejection.

A missing test is a test-adequacy finding, not a production defect, unless a project rule requires it. A test that claims to cover a behavior but cannot fail is a finding; rate it by what it lets through. Say which tests or commands you ran, on which revision, with what result; reading code is not running it.

### 2.12 Deeper checks

Open a [Risk Checks](references/risk-checks.md) section only when its trigger appears in the inventory.

| Trigger in the change | Section in Risk Checks |
| --- | --- |
| Clocks across machines, expiry; value equality, collection identity, replacement implementations | Values, Time and Collections |
| Cross-row rules, locks, connection pools or waits on other work | Concurrency and Progress |
| Queues, jobs, async commands, work leases, compensation, resource lifetimes | Asynchronous Work and Recovery |
| Deadlines, expensive input, shared capacity, retry chains | Budgets and Capacity |
| An existing cache, or an offline data investigation | Caches and Diagnostics |
| Client values reaching queries, files, processes or deserialization; personal or secret data | Data Protection and Technical Operations |
| Live migration of retained data, destructive conversion, rollback, dynamic configuration | Migration, Release and Configuration |
| Protocol or format changes | Compatibility Evidence |
| Failure logging, or a silent failure that could hide accepted work | Logs and Detection |
| Direct or transitive dependency upgrades | Dependency Upgrades |
| Concurrency, failure or numeric claims needing stronger test evidence | Test Evidence |

## Step 3: Verify each candidate

Try to disprove each candidate and each earlier review comment you must re-check, as if someone else had raised it.

1. **Name the contract.** A contract is a stated or established expectation you can cite. Look in this order: (1) the request, ticket, requirement or design document; (2) API schemas, interface docs, comments, and names that promise behavior (`reserveOnce`, `idempotencyKey`, `amountCents`); (3) the database schema: constraints, types, defaults, unique keys; (4) existing tests and the released behavior callers rely on; (5) project rules: coding standards, error-code catalogs, review policies. These baseline obligations also count when the code makes them reachable:
   - a caller reaches only data their identity is allowed to;
   - an accepted write is not lost, half applied, or overwritten by a stale value;
   - a retried or redelivered request does not repeat money movement, messages or inserts that must happen once;
   - other systems never see an effect for uncommitted data;
   - a dependency or processing failure is never reported as success, an empty result or "not found";
   - where the project deploys by rolling update or can roll back, old and new versions both work with the data and messages the other writes;
   - money is exact in the currency's units with the stated rounding;
   - a paged or filtered list returns each promised item once, in the stated order;
   - a test that claims to cover a behavior fails when that behavior breaks.
2. **Write the trigger.** Give the concrete input, state or timing, through a real entry point, that reaches the line. "Could be null" is not a trigger; "`POST /refunds` accepts `amount: \"19.99\"`, line 88 parses it as a double and truncates `amount * 100` to an integer, so 1998 cents are refunded instead of 1999" is.
3. **Search for the defense.** Check middleware, decorators, the caller, the schema, the transaction wrapper, framework defaults and tests. If a defense stops the trigger, drop the candidate.
4. **Trace the consequence.** What goes wrong, for whom, and is it recoverable?
5. **Classify.** Confirmed: the trigger is reachable and violates a located contract. Uncertain: the trigger is reachable and a contract source plausibly governs it but is silent or ambiguous, or one decisive fact is unknown; name the source and the question. Not substantiated: a defense stops it, the path is unreachable, or you checked the five sources and the baseline list and none covers the input; if still worth doing, it may be a suggestion. Impact, experience, a missing test or a hypothetical caller alone confirms nothing.

If a project rule requires a verifier other than the proposer, record that check as a pending gate; it does not downgrade a demonstrated defect.

## Step 4: Rate severity

Rate by impact and reachability, not style or missing tests. A project's own scheme overrides this one.

- **Blocker:** reachable in normal use or routine conditions (a retry, two concurrent users, a deploy), causing unauthorized access, data loss or corruption, wrong money, a duplicate irreversible effect, or an outage or failed deploy.
- **Major:** a wrong result or failure with limited scope or easy recovery; a Blocker-class impact that needs uncommon but realistic conditions; a hot path that breaks a contracted or sourced latency limit.
- **Minor:** small impact, rare conditions, simple recovery.

## Step 5: Propose the fix

- Give the narrowest fix that removes the trigger, inside the established architecture. Do not remove valid validation, error classification, concurrency guards or negative tests as duplication.
- Acceptance steps, in order: a test failing on the current revision on the target assertion (not on compilation, environment or skipped tests, and never by changing expectations); the minimal complete fix; the same test passing; review by someone other than the fix's author; the project's quick checks, and release checks before release.
- For an Uncertain candidate or open business choice, give the question, evidence, owner, and three options with consequences: change the code, document the current behavior, or leave it. Documenting or leaving it cannot waive a mandatory requirement. An approved exception names its approver, scope and expiry and does not waive its whole category.

## Step 6: Report

Use the compact report for one bounded change. Write "None" for an area checked and clean, "Not checked: <reason>" for one you skipped, and omit empty sections.

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
Workspace: <changes before and after the review, or "unchanged">
Pending gates: <required checks or approvals not yet done, each with an owner>
```

Order findings by severity; keep Uncertain items and suggestions out of them. Do not hedge by keeping a weak candidate as a suggestion; count a not-substantiated one and leave it out. List at most three suggestions.

For several independent concerns, or when asked for a full report, keep the finding format and add a requirement → evidence map (missing, inapplicable and unverified items marked), one block per concern, every candidate's disposition and reason, owner decisions, remediation and release steps (for a released fix: the signal to watch, its owner, the stop condition) and, when Step 2.10 applied, compatibility evidence.

Recommend acceptance only within what you verified, never unconditionally while a mandatory requirement is unmet or decisive evidence is missing. A clean review does not prove a fix, a release or production behavior.

## Self-check

- [ ] Every finding has a location, a reachable trigger, a located contract, a consequence, evidence, the narrowest fix, and no existing defense that stops it.
- [ ] I mapped each changed block to a requirement and ran every Step 2 section on every inventory entry, noting which do not apply.
- [ ] Edge-case, hardening and performance findings rest on a contract or sourced limit; the rest are suggestions.
- [ ] Uncertain items name the source, the question, the owner and the options; they are not in the findings list.
- [ ] Every fix stays inside the established architecture; any architecture change is a separate owner decision.
- [ ] I changed no code, data or services, read no credentials or environment files, recorded the workspace before and after, and marked checks I did not run as pending.
- [ ] A single bounded change gets the compact report, ordered by severity, with no empty sections.
