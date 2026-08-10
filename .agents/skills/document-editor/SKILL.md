---
name: document-editor
description: >-
  Edit and review formal human-facing documents at the document level without
  silently changing their meaning. Use for design docs, RFCs, implementation
  plans, proposals, specs, research reports, guides, decision memos, and review
  docs when the work concerns scope, reader path, structure, abstraction,
  factual grounding, evidence, tradeoffs, registries, structured assets,
  document governance, concision, or reviewability. Do not use for casual notes,
  chat replies, pure sentence-level wording or translation polish, or
  agent-instruction files such as SKILL.md, prompts, workflows, or tool-routing
  docs.
---

# Document Editor

Edit formal human-facing documents so readers can understand them quickly, review them accurately, and act with less friction. Preserve meaning while improving scope, order, explanation, and presentation.

Apply this priority order: **truth and authority → reader contract and scope → decisions and evidence → abstraction and structure → completeness and actionability → concision and presentation**. Apply only the controls relevant to the document type and its owner-defined governance.

## Hard prohibitions (owner-mandated)

These six rules are absolute for every document this skill touches; the rest of this skill is written to be consistent with them.

1. **No patch-style updates.** Never leave update residue: no addenda, errata, changelogs, revision histories, correction notes, "as of"/"updated" markers, or before-vs-after narration. Fold every change into the owning passage so the document always reads as if written correct the first time.
2. **No deferral to other documents.** Never offload content readers need to another document in the same working set through companion-volume pointers, document maps, or directions such as "see the implementation document." The document carries what its reader needs and omits the rest. Evidence citations to externally published sources in research reports establish attribution and are not deferral; retain them.
3. **No cross-references between sections.** No "see chapter 6", "as described above/below", or forward/backward pointers. Order sections so each is understandable where it stands; when another section's fact is needed, restate the minimum inline without naming the section.
4. **Prefer titled bullets over paragraphs.** When 1–5 points suffice, present them as bullet points, each opening with a clear and precise title, rather than paragraph prose.
5. **No unnecessary table columns.** Every column must carry decision-relevant information that varies across rows; drop or merge any column that repeats another, restates the row label, or exists only for symmetry.
6. **No coined vocabulary or jargon.** Use plain words and terms established in the field or in the source material; never invent labels, metaphors, or shorthand names for the document's own concepts.

## Frame the edit

1. Read the full document once without editing. Record the current section order as a compact outline.
2. Identify the document type, intended audience, primary purpose, target language, abstraction level, and reader contract: the decision or action the document promises to support.
3. Identify the concrete bottleneck, failure mode, or uncertainty the document exists to resolve, what readers already know, and what context they need before judging the rest.
4. Identify owner or format constraints, required content slots, governance state, referenced sources, and any content that must be preserved exactly or structurally.
5. Determine which rules in this skill apply. For required or high-risk controls, record an explicit not-applicable reason when one does not. Treat an owner-defined length or structural budget as a constraint; if it must change, expose the content-level cause, follow the owner's approval process, and resolve asset or format conflicts during lossless asset verification.
6. Before a loss-sensitive restructure, split, or compression, build the content and asset mapping described in **Inventory and preserve structured assets**. Keep the mapping only in the editing-session record or an external approval record, never in the edited document. If the owner requires a pre-edit approval gate, present that mapping before editing.
7. Diagnose and fix by dependency in this order: authority and scope → reader contract → bottleneck framing → section order → decision and evidence chain → abstraction boundaries → action path → accuracy → duplication → presentation. Fix any truth issue as soon as it is found; this sequence never delays it.
8. Integrate changes into the owning passages, run the applicable checks, and report unresolved ambiguity instead of hiding it in smoother prose.

## Determine governance applicability

This section only supplements the governance fields allowed when the owner explicitly requires them; it creates no exception to the six hard prohibitions.

1. Governance apparatus requires a real, external publication or approval lifecycle. An unpublished repository working document read only by repository collaborators carries no signature fields or lifecycle labels; its opening holds only what a reader needs to use the content.
2. Only when the owner explicitly mandates governance for a document with a genuine external lifecycle, provide the requested non-revision metadata: status, accountable owner, approver, and approval date. Governance authorization does not waive any hard prohibition. Revision dates, change histories, and re-review narratives remain excluded; process traces belong in an external governance system.
3. Follow the document's real lifecycle rather than inventing one. Attribute approval only when it exists, return materially changed approved content to the appropriate review state, and record the true reason for re-review in the external lifecycle system.
4. Review history, consequential dissent, and lifecycle evidence belong in an external governance system; the edited document never carries them.

## Inventory and preserve structured assets

This section governs only lossless accounting when content moves; abstraction level belongs to **Definition vs implementation**, while main-text versus appendix placement belongs to **Registries vs decision narrative**.

1. Before editing, inventory the load-bearing assets: decisions, open questions and blockers, conditional branch tables, tradeoff matrices, invariants, non-goals, risks, rollout batches, diagrams, exact contracts, error catalogs, and critical checklists, as applicable.
2. Give every inventoried passage or asset a disposition: preserved in place, moved to a named destination, merged into a named authoritative item, or intentionally removed with a reason and the required authorization. Keep this mapping only in the editing-session record or an external approval record, never in the edited document. Do not use compression as an unreported deletion path.
3. Extend the relocation discipline for registries to every inventoried asset, not only registry entries. Treat conversion to a table or movement to an appendix as relocation under that discipline.
4. Treat exact schemas, interface signatures, identifiers, error definitions, and other contract artifacts as deliverables in their own right. Preserve their completeness and exactness even when surrounding explanation is condensed.
5. Treat an asset's item count or byte identity as a protected baseline only when the owner or delivery format defines it. For a controlled baseline change, keep the pre-change and post-change values and any required authorization only in the editing-session record or external approval record; never place them in the edited document or change the baseline silently.
6. When byte-for-byte identity is required, use the configured checksum or comparison method. Do not modify a protected diagram or native asset without authorization; after an authorized change, keep its reason and basis only in the editing-session record or external approval record, and apply the required rendering or behavior checks.
7. Classify protected-content conflicts by priority. Delete residue that the six hard prohibitions clearly forbid. Retain owner-required governance fields only within the allowed scope above. If a template protection marker directly conflicts with a hard prohibition, escalate to the owner; do not treat the marker as either permission to retain the content or an instruction to delete it automatically. Do not break required document syntax.

## Preserve truth and authority

### Source grounding and current state

1. Preserve the source meaning, facts, scope, and decisions unless the user explicitly requests a substantive change.
2. Do not silently change numbers, dates, owners, names, identifiers, field or API contracts, formulas, requirements, conditional direction, or decisions.
3. Determine authority per claim type. Use implementation or observed behavior for current state, approved requirements or decisions for intended state, and direct observations or primary studies for measured outcomes. Do not apply one global source hierarchy across claim types.
4. When sources disagree, inspect the conflict, use the best-supported claim, and record any difference that affects scope, accuracy, or a decision. Do not choose a source merely because it appears in a preferred category.
5. Before describing a change, distinguish the observed current state, the approved or proposed target state, assumptions, and the gap between them. Do not design against an invented current state.
6. Explain any departure from an established decision and preserve its authorization boundary. Editing authority alone does not authorize a new decision.
7. Flag ambiguity, inconsistency, or missing evidence. Tighten wording noise, not substantive meaning.

### Unknowns, branches, and decisions

1. For a blocking unknown with no established default, record the question, why it is unresolved, the authority or resolver needed, known candidate space, affected decisions or passages, timing or trigger when relevant, and the consequence of remaining unresolved. State a fallback only when a source establishes one.
2. For a branch with an established default, state the default, alternatives, and the criterion that selects among them. Mark confirmation as open without presenting the default as newly invented.
3. Keep each open question independently answerable. When choices must be decided together, present a mutually exclusive and collectively complete decision package; include an explicit unknown or escalation branch when the candidate space is not closed.
4. Never turn an unanswered question into a design conclusion. If the missing answer prevents accurate prose, leave a governed placeholder or registry entry and identify what it blocks.

### Definitions and references

1. Give each definition, decision, invariant, complete comparison, and document-level disclaimer one authoritative location. Elsewhere, restate only the minimum a reader needs in place; do not maintain competing full copies.
2. Keep classification and evaluation axes orthogonal. Do not mix or substitute criteria that answer different questions.
3. Avoid machine-local paths and refactor-sensitive file, line, class, or method references in the main reading path. Include repository-relative locations or symbols only when implementation review or reproducibility requires them. Preserve stable contract identifiers exactly when they are part of the subject.
4. Apply hard prohibition 1; integrate corrections into the owning passage.

## Choose the reader path

### Common reader paths

Choose and adapt the path that matches the reader's task:

| Document need | Typical reader path |
| --- | --- |
| High-level design or review | Problem and goals → context and definitions → constraints → proposed design → success criteria → contracts and data semantics → affected systems → rollout strategy → risks and validation |
| Implementation design or runbook | Scope and prerequisites → current and target behavior → detailed changes → data flow and edge cases → migration and operations → testing, observability, rollout, and rollback → risks and open questions |
| Decision memo, ADR, or RFC | Context → decision → options → evaluation and tradeoffs → decision or recommendation → consequences and re-evaluation triggers |
| Research report | Question and scope → sources and method → findings and provenance → analysis and limitations → conclusions or recommendations → unresolved questions |
| Technical solution or adoption guide | Audience and bottleneck → current limits → proposed capability → proof → usage path → alternatives → internals → failure modes and mitigations → next steps |
| Workflow or guidance | Applicability → classification or diagnosis → source-grounding steps → operating workflow → verification → escalation and limitations |

Move definitions before evaluation when readers need the concepts to judge the design. Move proof and the usage path before internals when adoption is the primary task.

### Headings, navigation, and transitions

1. Match the title and opening scope to the document's real coverage.
2. Use a consistent semantic heading hierarchy. Add numeric heading labels only when the destination convention or navigation need calls for them.
3. Do not invent parallel module, decision, validation, option, or step ID systems for editorial organization. Use ordered steps when order is operationally meaningful, not as a substitute for semantic names.
4. Provide the necessary context at the point of use.
5. Give each section one clear purpose or reader question and keep neighboring sections non-overlapping.
6. Order sections by the reader's decision path, not by the history of how the team built or discussed the work. Separate audience paths when reviewers, adopters, operators, and implementers need different depth.
7. Use a short bridge only when it clarifies causality. Put it at the start of the section it introduces, and remove trailing meta-narration about what the document will explain next.
8. Use question headings only for genuine reader questions and answer them immediately. Prefer declarative headings in settled decision narratives; do not use staged questions to recreate deliberation.
9. Reuse concept names already established in the source material or domain as navigation anchors; do not coin labels for navigation.
10. Do not front-load lookup blocks. Make each opaque term readable at its first occurrence in place: use plain wording with the exact code in parentheses, such as "rejected: the record is still referenced (error 1042)," instead of a bare code. An identifier that already reads plainly, such as ERR_TEMPLATE_IN_USE, needs no added gloss. Add a front-of-document glossary, error-code table, or quick-reference only when the owner explicitly asks for one.

### Definition vs implementation

This section governs abstraction level; registry placement governs main-text versus appendix location, and asset preservation governs only lossless accounting when content moves.

Keep these layers distinct. Move definitions earlier and implementation later unless the document is explicitly implementation-focused.

- **Definition layer:** goals, domain semantics, responsibility boundaries, conceptual models, invariants, and decision criteria.
- **Implementation layer:** exact contracts, validation and error behavior, persistence and migration rules, algorithms, operational procedures, observability, permissions, and rollout changes.

Keep high-level design focused on decisions, boundaries, semantics, tradeoffs, compatibility, consistency, rollout strategy, and risk. Retain implementation detail only when it helps the intended reader judge feasibility, constraints, reliability, or tradeoffs.

### Multi-document sets

Apply the definition and implementation boundaries when material is split across a set. Each document independently fulfills its reader contract.

## Build decisions, evidence, and actionability

1. Start from the bottleneck, not the feature. State the constraint or failure mode the document resolves.
2. For proposals and decisions, use a compact opening summary that states the proposal, benefit, cost, and main uncertainty. State goals and non-goals, including exclusions readers could reasonably assume were in scope.
3. In decision-heavy sections, place the decision before its support and keep the minimum sufficient reasoning for a reviewer to verify that it holds under the stated constraints. Remove process narration only when the mechanism, evidence, tradeoffs, limitations, and risks remain reviewable.
4. For important claims, preserve the available chain: claim → mechanism → evidence → limitation. Flag a missing link instead of smoothing over it.
5. For research documents, use evidence citations to externally published sources or an owner-compatible provenance scheme to distinguish primary evidence, secondary reporting, established consensus, and analysis or inference. Such citations establish evidence attribution and are not deferral to another document.
6. For improvement claims, identify the named baseline, test condition, evaluation criteria, observed result, and caveat. Keep evidence near the claim, distinguish observation from interpretation, and ensure claimed quantities match the underlying material.
7. Treat realistic examples as evidence: give enough context, preconditions, behavior, outcome, and interpretation for the reader to understand what the example proves and what it does not.
8. Compare alternatives on stable criteria such as correctness, reliability, cost, latency, complexity, maintainability, rollout risk, and reversibility. Preserve each option's sourced strengths before its limits; do not invent balance that the sources do not support.
9. Put assumptions, dependencies, known failure modes, incomplete coverage, mitigations, and bounded caveats close to the solution or claim they qualify. Do not use future plans to compensate for weak present evidence.
10. Tie deferred work to a current gap. For a deliberate extension point or non-goal, state the reserved shape, the trigger for revisiting it, and why reserving it now matters; distinguish committed work, exploration, and open questions.
11. When work varies by type or risk, use an inspect → classify → guide → verify flow. Keep diagnosis separate from recovery validation, and apply the complete decision-package rules for unknowns and branches.
12. Convert tacit judgment into executable checklists, decision tables, workflows, risk categories, failure modes, and validation criteria. When readers must act, include the necessary owner, prerequisites, inputs, outputs, and success criteria.
13. For adoption or onboarding, provide a complete path through prerequisites, setup, invocation, success verification, troubleshooting, and an ownership or feedback route when one exists.

## Registries vs decision narrative

This section governs where content appears in the main text or appendix; abstraction level belongs to **Definition vs implementation**, while lossless verification during moves belongs to **Inventory and preserve structured assets**.

Keep three layers distinct:

1. **Decision narrative** (main reading path): only the minimum facts, conditions, conclusions, costs, and re-evaluation triggers needed for the current review. Do not reproduce full ledger entries or point readers to the appendix.
2. **Registries and audit ledgers** (appendix of the same document): the unique, complete open-issue, blocker, and verification ledgers.
3. **Operational detail:** operational details do not enter the decision narrative.

Rules:

1. Relocation is not deletion — a moved entry keeps every field, conditional direction, and decision-bearing relationship; after restructuring, verify the ledger remains complete entry by entry and field by field.
2. Settled items return to the owning decision section; historical recounts of registry size belong in the external lifecycle system, not in live registries.
3. Domain identifier semantics — uniqueness, immutability, recycling, regeneration on copy — belong in the domain model even while an aspect is still open. State the established default and name the open question inline; if no default exists, say so and identify the blocked decision instead of inventing one.
4. A design document carries non-functional targets such as expected volume, query scale, throughput, latency, and capacity ceilings, or names each unknown together with the decision threshold it unblocks. A named unknown with a threshold beats both an invented number and a silent gap.
5. With several external dependencies, include one unified failure-strategy table — dependency unavailable → affected operations → block or degrade → caching allowance — rather than scattering the rules across chapters.
6. When a per-decision comparison matrix outgrows its narrative, move the matrix to the appendix and keep the decision, its preconditions, and its reversal triggers inline.
7. Treat scanability as a placement goal, not a prose quota. Retain causal explanation that changes how reviewers judge assumptions, tradeoffs, or failure modes.

## Use tables, diagrams, media, and code deliberately

1. Use tables for stable repeated columns such as options and tradeoffs, risks and mitigations, contracts and meanings, scenarios and verification, or phases and success criteria. Use prose for causality, ambiguity, hidden assumptions, and nuanced caveats.
2. Use parallel table shapes for parallel structures, and do not force uncertain reasoning into apparently precise cells. Tables improve placement; they do not replace the decision narrative.
3. Preserve existing diagrams, images, videos, code blocks, callouts, evidence citations, and other native blocks unless the user requests a change or a source-backed edit requires one. Give every retained or added block an editorial job: evidence, instruction, architecture, workflow, or reference.
4. Use a diagram only when it explains a spatial, temporal, boundary, state, or relationship model more clearly than prose. Use a format supported by the destination and its maintainers; do not impose one tool or syntax on every document.
5. Give every figure that must be understood independently the minimum in-place legend needed to read it. Keep semantics consistent by using the same wording in each figure's legend; do not create a shared legend center. Check decision-tree branches for mutually exclusive and collectively complete coverage.
6. Place an overview diagram after the framing needed to interpret it and before the details it organizes. Validate an editable diagram with its actual renderer after changes; if rendering cannot be checked, report that limitation.
7. Introduce code blocks with what they demonstrate and summarize the design implication when it is not obvious. Avoid raw dumps unless required for reproducibility, contract review, or implementation reference.

## Review and verify

1. For high-risk edits, separate editing from independent verification when available. Use a capability tier and reasoning depth sufficient for the document's domain and risk; do not bind the skill to a vendor, model name, or fixed role topology.
2. When author-reviewer separation is required, keep the independent review read-only and return requested changes to the editor. Let the accountable owner or a designated adjudicator who did not perform the edit resolve disagreements independently; an author's self-report is not verification.
3. Programmatically check every applicable deterministic constraint: declared lengths or counts, protected-asset inventory and byte identity, diagram rendering, target-format validity, prohibited patterns, terminology cleanup, identifier and evidence-citation existence, and diff hygiene.
4. Use semantic review for truth, authority, decision quality, evidence, and reader fit. Deterministic checks cannot establish those qualities, and semantic confidence cannot replace a failing hard check.
5. Confirm that the document has no section-jump internal links. Verify that every figure, table, attachment, evidence citation to an externally published source, and self-reported quantity resolves to real content. Report checks that could not run.

## Language and terminology boundary

Keep the owner-specified target language, register, and terminology scheme consistent while applying the authoritative-definition and identifier-fidelity rules for truth and authority. Sentence-level word choice, phrasing, naturalness, and register are outside this skill's scope — treat them as separate wording work. Within this skill, enforce only the document-level constraints: stable concept names across headings, tables, and every repeated mention, and byte-exact identifiers, numbers, and quoted contracts.

## Communication

**Review mode** — report findings first, grouped by truth and authority, scope and reader path, abstraction and registry placement, decisions and evidence, actionability and governance, then presentation.

**Optimize mode** — edit directly, then summarize what was reorganized, what remained unchanged to preserve truth, what was removed or deduplicated, how protected content was accounted for, which evidence or actionability gaps improved, which checks ran, and what ambiguity remains.

## Self-check

- Did the edit follow the priority order and apply every owner-required or high-risk control, with explicit reasons for important exclusions?
- Are current state, intended state, assumptions, unknowns, and source conflicts distinguishable, with no silent change to meaning or exact contracts?
- Does the title, section order, abstraction boundary, and audience path support the reader contract?
- Does each definition and decision have one authoritative location, and are decision narrative, registries, and operational detail still separated?
- Does each important claim retain its mechanism, evidence, limitation, relevant alternatives, risk, and actionable consequence?
- Does every moved or protected asset have a verified disposition with its fields, conditions, and required measurements intact?
- Did all applicable deterministic checks and renderers pass, or are skipped checks and their consequences reported?
- Is the document free of internal contradictions, duplicate rules, editor-process residue, and project- or task-specific assumptions that the owner did not request?
- Do all six hard prohibitions hold: no update residue, no deferral to other documents in the same working set, no cross-references between sections, titled bullets where 1–5 points suffice, no unnecessary table columns, and no coined vocabulary?
