---
name: raise-ambition
description: >-
  Rewrite a task's brief before work starts so it aims higher, in any domain, through four
  lenses from Rieseberg's model of ambition: Altitude (the outcome the task serves, one level
  up), Depth (the raw material, methods, hard targets, tested assumptions and outside
  verification a field-leading expert would use), Range (methods from other fields that change
  the result) and Speed (a deadline, an early first check, parallel work and no avoidable waits).
  Keeps the user's scope, constraints, permissions and budget; the result is one brief that
  this agent, a subagent or the user executes. Use when a non-trivial task is about to start and
  its description names only the deliverable: a design or architecture, a research or analysis
  question, a business review, a strategy or plan, a piece of writing, an operational process,
  a personal project. Also use when asked to make a task, prompt or plan more ambitious or to
  raise its standard, and before writing a burst definition of done. Do not use for a trivial or
  mechanical task, a task whose method the user fixed, executing the task, orchestrating
  subagents (use burst), or reviewing finished work.
---

# Raise Ambition

Before work starts, rewrite an ordinary task description into one brief that aims higher and can still be checked. The brief rests on four lenses: **Altitude**, the outcome the deliverable serves, one level up; **Depth**, the raw inputs, methods, numeric targets and outside checks a field-leading expert would use; **Range**, methods borrowed from other fields that change the result; and **Speed**, a schedule that reaches a verified result early. It keeps the user's scope, constraints, permissions and budget, and it puts every change that needs the user's consent in front of the user before any cost is spent. The skill rewrites only: it does not execute the task, decompose or dispatch work, choose models (burst owns those), switch on any model's fast mode, or review finished work or grade an existing plan. Because it only rewrites, it serves a single agent with no subagents, a writing task or a personal project as well as an orchestrated run. The lenses come from Rieseberg's essay on ambition (2026-10-13); Speed is not developed there, and its mechanisms below come from other sources, cited where they are used.

Priority order, highest first: **the user's constraints, safety and permissions → verifiability → Altitude → Depth → Range → Speed → concision.** A target raised beyond what an outside check can confirm is worse than the original target, so verifiability caps every lens. Apply the lenses in the same order: Altitude sets the outcome, Depth sets the standard and methods that reach it, Range adds methods to Depth, and Speed schedules the work the first three define.

Run the skill once per task, in one pass; do not raise a brief that this skill already produced. Scale the rewrite to the task: a small task gets a few lines, and a lens that does not fit is skipped with its reason. Write the brief in the task's language; the slot labels may stay in English. Return one recommended brief, never several alternatives side by side. When proxy is active, do not rewrite the brief yourself: rewriting the task is a planning decision, so send the task, the user's constraints and the resource check to an orchestrator-consultant and follow the brief it returns.

## The brief

Fixed slots, in this order, at most about 40 lines:

```
Task as given:        <the original task, verbatim>
Constraints kept:     <each user constraint, verbatim>
Outcome:              <what the deliverable must cause, one level up, observable>
Targets:              <high target; minimum acceptable target; learning target if novel; guardrails>
Inputs:               <primary sources and raw data>
Methods:              <method or tool → what it produces>
Assumptions to test:  <assumption → test that could disprove it> (2–3)
Verification:         <check outside the author → how to run it → pass condition>
Fields:               <field → method → what it changes> (3–5, one tries to disprove the result)
Schedule:             <deadline; critical path; parallel lines; time of first outside check>
Out of scope:         <what this brief does not cover>
Confirm before starting: <each change to deliverable, audience, access, cost or time>
Lenses skipped:       <lens → reason>
```

## Passes

### 1. Fix the frame and check resources

Copy the task and every explicit user constraint verbatim: scope, deadline, budget, tools, audience, and the actions the user wants asked about first. Then make one read-only check of what actually exists: the data, tools, access, prior work, and who uses the result. Name in the brief only resources the check found. A resource the raised brief needs but the check did not find becomes a precondition in Confirm before starting, never an assumed input.

### 2. Altitude — the outcome the deliverable serves

Ask what happens after the deliverable lands: who uses it to make which decision, and what would stop this task from recurring. Write the Outcome one level up from the deliverable, in observable terms, and keep the deliverable's type. A rise that would replace the deliverable or change its audience goes to Confirm before starting, not into the brief's working plan. Altitude fits best when the result feeds a discussion or a decision; for work judged mainly on taste, such as fiction, visual design or a personal letter, apply it lightly and put the ambition into Depth and Range.

### 3. Depth — the standard a field-leading expert would hold

Answer the essay's four questions: what would a top practitioner do beyond the ordinary version, which raw material would they start from, which methods and tools would they use, and which outside signal would show the result is right. Fill the slots from those answers:

- **Inputs** are primary sources and raw data, not someone else's summary of them.
- **Methods** name concrete methods or tools and what each produces.
- **Targets** carry a number and a unit each. Set one high target and one minimum acceptable target, so the result can be reported honestly against both. For a novel or complex task (a design, a study, a strategy) add a learning target, such as "compare at least N distinct approaches before choosing": on complex tasks a hard outcome target alone tends to narrow the search too early (Locke & Latham, 2002). Add guardrails, the qualities that must not get worse, because a single pursued metric degrades what it does not measure (Goodhart's law; Ordóñez et al., 2009, on the side effects of goals).
- **Assumptions to test** are the two or three the result rests on, each with a test that could disprove it.
- **Verification** is a check the author does not grade: a test suite, held-out data, a measurement, a second reviewer working from the criteria without seeing the conclusion, a pilot. State how to run it and what counts as a pass. Self-assessment is not verification; models in particular rarely fix their own reasoning without an outside signal (Huang et al., 2024). The brief may aim at new knowledge, provided held-out data or another outside check is reserved to confirm it.

### 4. Range — methods from other fields

First restate the deliverable as a verb goal ("a deck" becomes "in 30 minutes, convince the decision-makers of one causal chain and get a decision"), then pick the fields that are good at that verb. Each Fields line names a concrete method and the result it changes, never a persona or a tone ("think like an economist" is not a method; "estimate the effect with a difference-in-differences design" is). One line always tries to disprove the conclusion: a reviewer who argues the opposite from the same evidence, or a challenge review of the design's weakest point. Phrase that line in those terms and avoid security-testing vocabulary, because some model providers stop a run whose brief reads as security testing. For a small task, Range shrinks to one borrowed method and one disproof check.

### 5. Speed — time to a verified result

Speed shortens the time to a result that has passed its outside check, not the time to an unchecked draft. It rests on four mechanisms (drawn from Collison's "Fast" list, Little's law, Amdahl's law, the OODA loop and the theory of constraints):

1. Set a tight deadline at the start.
2. Get the first outside check early: a slice, a sample, a pilot, a draft review.
3. List the lines of work that can run in parallel and name the serial critical path, since the critical path, not the parallel work, sets the finish time.
4. Remove avoidable waits: batch the questions and approvals at the start, get data and access in place before work begins, and cut work that does not serve the Outcome.

Never buy speed by skipping verification, and never write "faster" without a mechanism. Speed is about the schedule; do not infer from it that a model's fast mode should be switched on.

### 6. Close the brief

Fill Out of scope with what the brief deliberately leaves out. Fill Confirm before starting with every item that changes the deliverable, its audience, access, cost or time, including any proposal to relax a user constraint, and stop for the user before starting. Raises of methods, targets and verification that stay inside the original constraints need no consent: state them in the brief and proceed. Fill Lenses skipped with each skipped or lightened lens and its reason.

## Guardrails

- **Deeper is not larger.** Every addition changes a method, an input, a target or the verification. The number of deliverables stays the same unless the user agrees.
- **Constraints first.** A constraint is relaxed only by asking, through Confirm before starting.
- **No new permissions.** Do not obtain access, spend money, contact anyone outside, or take an irreversible action on the strength of the raised brief.
- **Report honestly.** When the work misses the high target, report it against the minimum target as it stands; never lower a target quietly after the fact.

## Hand-offs to other skills

- **burst**: run this skill first; burst takes its definition of done from the brief, turns Fields lines into method-specific worker briefs, uses the Schedule's parallel lines when planning dispatch, and has its reviewer or verifier run the Verification.
- **document-editor**: when the deliverable is a document, this skill sets the standard and document-editor owns the document's structure.
- **communicate**: governs how the brief and any later report are written to the user. Gloss each lens name in plain words on first use.

## Examples

Short extracts; a real brief fills every slot.

**Software — "Design the architecture of a multi-tenant notification service."**
- Outcome: each tenant's messages arrive correct, on time and exactly once; a new channel needs only configuration; the on-call engineer finds the cause of a failed delivery within 5 minutes.
- Targets: high, p99 ≤ 1 s at 10× peak; minimum, tenant isolation at current peak; guardrail, cost per message does not rise. The numbers are placeholders until checked against real traffic.
- Methods: a queueing capacity model, a load simulation with one tenant flooding the queue, a TLA+ model of retries and deduplication, a failure-mode table.
- Fields: SRE (failure drills that switch off a dependency), scheduling theory (weighted fair queueing), email deliverability (sender-reputation isolation), FinOps (unit cost); a reviewer argues the design fails when one tenant floods the queue.
- Verification: model-checker output, load data, a replay of historical peaks, an independent review that reads the test code.
- Confirm before starting: access to production logs.

**Research — "Summarize the research on whether remote work lowers productivity, for the company's office policy."**
- Outcome: a policy decision the executives can defend, plus how it will be checked after rollout.
- Methods: a systematic search with stated inclusion criteria, effect-size extraction, weighting by study design, separate analysis by task type.
- Assumptions to test: productivity means output, not hours.
- Verification: a second reviewer applies the inclusion criteria without seeing the conclusions; conclusions are written down before the internal data is opened.
- Fields: labor economics (causal identification), organizational psychology (team coordination); one line argues the opposite policy from the same evidence.
- Confirm before starting: use of internal HR data.

**Business — "Prepare the quarterly business review deck."** (the essay's example)
- Outcome: leadership spots problems earlier and makes resource decisions.
- Methods: start from the raw data, find the three most urgent decisions, and give the case for and against each.
- Confirm before starting (Altitude one more level): design a mechanism that catches problems before the quarterly review and run it alongside the current process for one quarter.

## Failure modes

1. **New vocabulary, same method** — the brief sounds bolder but no method, input, target or check changed.
2. **Scope growth passed off as depth** — more deliverables instead of a higher standard for the same ones.
3. **Altitude too high or swapped** — an outcome nobody can act on, or a different task quietly replacing the one given.
4. **Self-assessment as verification** — the author or the same model grades its own result.
5. **Role-play instead of method** — a persona or tone where a concrete method belongs.
6. **Targets without numbers** — "fast", "scalable", "best-in-class".
7. **Secondhand inputs only** — summaries where the raw material exists.
8. **False speed** — "faster" with no mechanism, or speed bought by skipping the check.
9. **Overstepped bounds** — a constraint, permission or cost crossed without asking.
10. **One metric chased** — no guardrails, or no minimum target, so the result cannot be reported honestly.
11. **Invented resources** — data, tools or access the resource check did not find.
12. **Full process on a small task** — thirteen filled slots for a two-line job.
13. **A generic brief** — one that would fit a different task unchanged.

## Self-check

- [ ] The task and constraints are copied verbatim; the number of deliverables is unchanged or the change is in Confirm before starting.
- [ ] The Outcome is observable, one level up, and does not replace the task.
- [ ] Every target has a number and a unit; there is a high target and a minimum target, a learning target if the task is novel or complex, and guardrails.
- [ ] Inputs are primary sources; Methods name concrete tools; two or three assumptions each have a test that could disprove them.
- [ ] Verification comes from outside the author and states how to run it and what passes.
- [ ] Each Fields line names a method and what it changes, with no persona, and one line tries to disprove the result in challenge-review wording.
- [ ] The Schedule has a deadline, the critical path, the parallel lines, questions and approvals moved to the start, and the time of the first outside check.
- [ ] Every change to deliverable, audience, access, cost or time is in Confirm before starting, and work waits for the user on those items.
- [ ] Skipped lenses carry reasons; the brief is one recommendation of at most about 40 lines, in the task's language, and every resource it names was found by the check.
