# Risk Checks

Use a section only when its trigger appears in the change, and only the checks the code makes reachable. For each, note the trigger, the contract or sourced limit, the evidence and the result. A check here yields a candidate until the main skill's verification confirms it, and grants no permission for operational actions. Prefer the project's existing mechanisms over a new facility.

## Values, Time and Collections

- **Clocks across machines.** When expiry, leases, scheduling or cleanup compares times from different machines, find the time authority and allowed skew, and check clock jumps both ways. Local timestamp order does not prove global order; skew must not extend an access lifetime past its contract.
- **Elapsed and calendar time.** Measure local timeouts and budgets with a monotonic clock, not wall time. Add days, months and years with calendar operations; a fixed 24 hours is wrong across daylight-saving changes.
- **Numbers in transit.** The stored value must still meet the column's type, scale and constraint, and a conversion must not bypass validation. Check exponent forms (`1e3`) and overflow at parsing. Do not demand exact decimals beyond money and counts.
- **Missing and empty values.** Distinguish a missing field, explicit null, an empty list, blank text, a default and a display value. A whole-record read-then-write must not drop fields the code does not understand.
- **Value semantics.** Equal values must hash equally. Returned or passed-in collections must not let callers change stored state; a read-only view or immutable value needs no copy.
- **Collection identity and limits.** Check the deduplication identity (every part of a compound key), how nulls count, per-group versus overall limits, and exact-limit and limit-plus-one cases. Splitting a batch must not change the whole set's result.
- **Replacements.** A replacement implementation or decorator accepts every input the original did and returns no weaker result; callers must not need to know which one they got.

## Concurrency and Progress

- **Cross-row invariants.** For a rule spanning rows or ranges (no overlapping bookings, a total under a cap, "no active record exists"), list what the decision read and what protects each fact until commit; two transactions can both pass the check and write (write skew). A snapshot read does not protect it either, nor does a one-record guarantee cover partitions or replicas.
- **Locks and waits.** When work takes locks, connections, pool slots or leases, or waits on child work, trace acquisition order for cycles, waits on a task that needs the held slot, and starvation. Repeated timeouts do not prove progress. Do not add coordination to isolated, immutable computation.

## Asynchronous Work and Recovery

- **Authority for async work.** Distinguish a user request, a delayed command acting for a user, and a notice of a fact that already happened. Check the producer, service identity, target tenant and delegation scope; an ID in the payload is not authority. For delayed commands, check the contract on permission changes, revocation and expiry before execution. For completed-fact notices, check origin and permission to process, not that the original user still holds the permission.
- **Acknowledgment.** Order ack, consumer progress, business effect, retry handoff and final-failure handling. Under a durable-handling contract, the effect or a durable handoff precedes the ack; a function return, in-memory queue or fire-and-forget submit is not durable. Check partial batches and a crash at each step.
- **Order.** For effects that do not commute, find the required order, routing key, the scope the broker actually orders within, and sequence evidence. Check gaps, reordering and late arrivals against the contract (wait, reject, reconcile or recover). Partitions and timestamps do not prove global order. Do not demand ordering for commuting effects.
- **Stale writes.** A consumer applying a snapshot must not overwrite a newer one or drop increments the contract keeps.
- **Expired ownership.** When a worker's lease can expire, the final write and the release must check the worker's generation or token, so a stale worker cannot write or release its successor's lease.
- **Recovery after a crash.** Mark each interruption point: external call, local commit, outcome record, compensation, notification. Where recovery is required, the operation's identity and intent survive a crash or are rebuilt from durable data. Distinguish not executed, executed and unknown, compensation included. Manual recovery needs a detection condition, evidence, an entry point and executable steps, not just an owner. Keep an accepted loss window visible; do not invent a stronger promise.
- **Resource lifetime.** Owned resources (connections, files, threads, streams) close through nested scopes and shutdown; borrowed ones stay open for their owner. Restore request context after a nested scope. Failures of async work must be observed, not dropped.

## Budgets and Capacity

- **Executed queries.** At the largest allowed input, check the executed statements: bindings and types, predicates, returned volume, query count and the plan where available. Builder code, an index declaration or a tiny sample does not show how a query runs.
- **Remaining time.** Subtract queuing, processing and backoff from the original budget; before new work or a retry, recompute what remains and pass a deadline on. With none left, start no new requested work and take the contracted failure or fallback; required cleanup or reconciliation runs under its own bounded budget or a durable handoff, never extending the caller's deadline. A retry gets no fresh budget. A tiny remainder must not become zero where zero means "no limit".
- **Total cost.** Where resource use changes, note request rate, concurrency, payload size and depth, and data skew, with sources. Trace parsing, decompression, serialization, lock hold time and retained results; judge total amplification, not per-item cost. Do not require a load test for an unrelated change.
- **Overload and retries.** Check concurrency limits, queue sizes, waits and backoff (with jitter for many clients) against real resource limits. Work running after a timeout still uses resources; do not claim cancellation stopped effects where it does not. Failing fast can be correct. Do not add retries, circuit breakers or a rate-limit service by default.

## Caches and Diagnostics

- **Existing caches.** The key must include every input that changes the result, including the caller's scope. Distinguish cached success, "not found", dependency failure, expired and approved-stale entries. Check invalidation after writes and rollbacks, and that a slow fill cannot overwrite newer data; expiry alone does not make data fresh. A shared cache must not replace a required per-request authorization check. Do not recommend a cache for request-local reuse.
- **Offline data investigation.** When an authorized investigation reads stored data, keep invalid raw values without widening valid domain states. Record each row anomaly and continue; stop on connection failure or an unknown decisive fact. Online writes must still reject corrupt data. Do not repair investigated data without permission.

## Data Protection and Technical Operations

- **Values reaching technical operations.** Trace client values into SQL, shell commands, file paths, URLs, templates and deserialization. Each must arrive bound, escaped or checked against an allowed set under the real execution rules; pasted into statement text, a value breaks on quotes and changes the statement. Login, business validation or a string check elsewhere does not make it safe there. A dynamic target (file path, outbound URL, class name) must be restricted to the allowed set. Do not demand blanket sanitization of ordinary fields.
- **Personal and secret data.** Trace it through responses, logs, caches, messages, samples, backups and deletion. A debug setting must not disable peer authentication or transport encryption. Secrets are replaceable, not hard-coded. Use the project's classification and mechanisms; do not invent cryptography or apply one protection level to all data.

## Migration, Release and Configuration

- **Live migration of retained data.** Check lock duration, load and waits on business traffic, writes arriving mid-migration, progress tracking, bounded batches, safe re-entry and a stop condition. Reconcile business invariants, not only row counts. Empty-store setup or an approved small offline migration can be simple. Do not override an explicit decision not to migrate.
- **Destructive conversion.** Identify the irreversible step and the promised recovery point, time and allowed loss. The original, a usable copy or a lossless reverse must exist and survive later writes; a backup setting is not proof of restore. Recovery must not overwrite later legitimate writes. Drill only on isolated resources you may use.
- **Release and rollback.** Distinguish "process started", "ready for traffic" and "business correct". Check the stop condition, every reachable mix of code, configuration, data and message versions, and in-flight work at switchover and shutdown. Rollback is viable only with evidence the old version reads new data and handles outstanding work; otherwise record the limit and a forward fix. Never delete new data to make rollback look possible.
- **Live configuration changes.** Check invalid values, which configuration version a request uses, which mixes are safe, and what happens to queued work. Turning a switch back on does not undo durable effects. Validate static settings at startup. Do not recommend dynamic configuration or flags without a requirement.

## Compatibility Evidence

- **Real encoders and decoders.** Test a protocol or format change with versioned actual encoders and decoders: old sender to new receiver and new to old, for requests and responses. Assert an old decoder skips each added field where the protocol allows, or show none was added. Check types, IDs, units, enum values, unknown fields, and old entries still reachable against new checks, or the required version negotiation or approved rejection.
- **How long compatibility must last.** Derive the needed combinations from real client lifetimes, deploy overlap, retained and replayable messages, queued jobs, stored formats and promised backup restores. Deploy overlap does not cover a longer retention promise.
- **Samples.** Produce responses with the delivered producer and requests with the actual client encoding, recording their origin. Contract-derived seed data run through real code in isolation is valid when labeled honestly; handwritten samples alone do not prove the chain.
- **Dependencies of the artifact.** Check dependency declarations, version authority, packaging and the target runtime, and build or package the affected artifacts. A host compile or a matching interface name does not prove runtime compatibility.

## Logs and Detection

- **Useful, safe logs.** At the final error boundary, log the failure class, safe identifiers and the reason for correlation. Logs carry no secrets or whole sensitive payloads, strip control characters from client values, and bound field size. One central log is enough.
- **Detecting silent failure.** Apply when a sourced detection duty exists or a silent failure could hide an accepted write, external effect or completed job. Name the signal, its condition, window and response owner. Distinguish zero traffic, zero errors and a missing signal, and cover "no progress". With no sourced detection time, record the missing owner decision. A metric's existence does not prove business health. Do not instrument every pure function.

## Dependency Upgrades

- **Changed behavior.** List direct and transitive changes and read their release notes. Check serialization, time handling, retries, transactions, exceptions, connections and build reproducibility. Relate published vulnerabilities to reachable runtime conditions; leave unknown exposure marked unknown. A successful compile or a small version bump does not prove unchanged behavior. Do not upgrade unrelated dependencies.

## Test Evidence

- **Fault sensitivity.** When a changed guard or calculation controls authorization, stored data or an irreversible effect, check a test fails for a few relevant faults (flipped boundary, deleted guard, wrong classification, missing effect), by reasoning or an authorized isolated mutation. One caught fault does not prove the suite adequate.
- **Concurrency tests.** Use distinguishable writes and explicit states to drive success, conflict, abort, and confirmed and unknown commit, then check final contents and row counts. Waits must be bounded and fail on timeout. Check storage-specific claims on the real storage engine and settings.
- **Dependency failures.** Drive scripted failures through the real adapter to the entry point, checking call budgets, forbidden and unexpected calls, and unused scripted responses. A stub that always succeeds does not test failure handling.
- **Execution claims.** Keep each claimed result's command, revision, selected tests, outcome and artifact freshness. In-memory stores or a local run cannot prove behavior on the target infrastructure.
