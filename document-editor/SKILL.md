---
name: document-editor
description: Edit formal human-facing documents at the document level without changing their meaning. Use for design docs, RFCs, implementation plans, proposals, specs, guides, decision memos, and review docs when the user wants to improve scope, structure, logical flow, reader fit, factual fidelity, concision, terminology, tables, or reviewability. Do not use for casual notes, chat replies, pure sentence-level wording polish, or agent-instruction files such as SKILL.md, prompts, workflows, or tool-routing docs.
---

# Document Editor

Edit formal human-facing documents so readers can understand them quickly, review them accurately, and act with less friction. Preserve meaning; improve how the document is scoped, ordered, explained, and worded.

## What good looks like

A strong document has these properties (each answers a question the reader is asking):

1. **Logically smooth** — section order follows the reader's decision path and the argument moves forward without jumps. *(What is this about? Why does it matter?)*
2. **Accurate** — preserves the source meaning, facts, scope, and decisions unless the user explicitly asks for substantive changes. *(What is being proposed, defined, or decided?)*
3. **Concise** — each section earns its place; repeated points appear once, in the clearest location.
4. **Natural** — reads like a careful professional wrote it in the target language, not machine-translated or LLM-shaped.
5. **Self-contained** — the reader needs no machine-local paths or off-page local references to grasp the main point, unless the user explicitly asks for them.
6. **Decision-oriented** — helps the reader decide, act, or verify, with source-backed support and executable next steps. *(What are the constraints, tradeoffs, and implications? What support, risk, or action path matters for my decision? What should happen next?)*

## First pass

Before editing, infer or identify — then keep the document aligned to these:

1. Document type
2. Intended audience
3. Primary purpose
4. Intended abstraction level
5. The reader contract: the decision or action the document promises to help the reader take
6. The concrete bottleneck, failure mode, or uncertainty the document exists to resolve
7. What the reader already knows, and what context they need before they can judge the rest

## Truth preservation (hard constraint)

1. Preserve the source meaning unless the user asks for substantive changes.
2. Do not silently change numbers, dates, owners, field names, API names, formulas, requirements, or decisions.
3. If the source is ambiguous, inconsistent, or incomplete, flag it instead of inventing a cleaner version.
4. When tightening prose, remove wording noise, not business meaning.

## Fix in this order

1. Read the full document once without editing. Write the current section order, one line each.
2. When the edit touches claims, scope, structure, evidence, or accuracy, inspect available or referenced source material first; otherwise keep source checks lightweight.
3. Fix issues in this sequence: scope and audience fit → reader contract → bottleneck framing → section order → evidence chain → abstraction layering → logical chain → action path → accuracy → duplication → terminology → wording.
4. Tighten bridges and headings; convert repeated structures into tables, checklists, workflows, or decision aids; separate definitions from implementation.
5. Run the finish checks.

## Section-order patterns

Choose the pattern that best matches the document type.

### High-Level Design / Review Doc
1. Problem / goals
2. Context / domain framing / key definitions
3. Constraints / design principles
4. Proposed solution
5. Success criteria / evaluation model
6. External contracts / interfaces
7. Data model / persistence model
8. Impacted systems / adaptation scope
9. Rollout / implementation adjustments
10. Validation: how the design answers the original goals

Use when the design depends on domain framing or named concepts that must be defined first, or when success criteria depend on understanding the proposed design first.

### Implementation Design Doc
1. Scope
2. Assumptions / prerequisites
3. Current state
4. Target behavior
5. Detailed changes
6. Data flow / edge cases / migration rules
7. Testing / rollout / rollback
8. Risks / open questions

### Decision Memo / ADR / RFC
1. Context
2. Decision to be made
3. Options
4. Evaluation / tradeoffs
5. Recommendation / final decision
6. Consequences

### Technical Solution / Tool / Adoption Doc
1. Positioning summary: what this is, who it is for, the value it promises
2. Problem / why now / concrete bottleneck
3. Existing approach limits or failure modes
4. Proposed capability / design principle
5. Proof: demo, realistic example, measured result, or comparison
6. Quick start / usage path when adoption matters
7. Alternatives / comparison / tradeoffs
8. Technical implementation / architecture / workflow
9. Limitations / known failure modes / mitigations
10. Roadmap / Q&A / next steps

Use for technical sharing, launch, adoption, onboarding, or proposal docs that must help readers understand, try, trust, and maintain a solution. Keep proof and adoption above internals. Move the quick start earlier when the primary reader needs to try the tool before reviewing proof or internals.

### Workflow / Guidance Doc
1. When to use it
2. Trigger conditions / classification rules
3. Inspect / source-grounding steps
4. Guidance, decision table, or operating workflow
5. Verification checklist
6. Escalation / fallback / limitations

Use for runbooks, troubleshooting guides, operating procedures, migration guides, or recurring implementation workflows where the reader must execute a safe sequence.

## Structure rules

1. The title must match the real scope.
2. Add second-level headings where they improve clarity, numbered hierarchically (a `1.` heading with `1.1` / `1.2` subheadings).
3. Put early what the reader needs in order to judge the rest. Preserve the reader journey over the author journey — do not order sections by how the team built the system unless that history is the reader's task.
4. Keep abstraction layers separated. Define concepts before formulas, field mappings, or rollout diffs. If the design depends on a named framework, operating model, or domain term, define that context before using it to justify the design.
5. For architectural or product design docs, replace code-level references, file paths, and implementation labels with business or system concepts unless the user explicitly asks for development-level detail.
6. When the document claims a new solution is better, surface existing baselines or alternatives; if missing, flag the gap instead of inventing them. Do not let future plans compensate for weak present evidence.
7. Separate audience paths when one document serves reviewers, adopters, operators, and implementers.
8. Use guiding-question headings only when they match the reader's likely doubts; too many rhetorical headings make the document feel like a slide deck. When a heading does pose the reader's question, the section's first sentence should answer it, not open with unrelated setup.
9. Keep a stable thesis phrase or named concept for navigation, but repeat it through new evidence or implications instead of copying the same sentence.

### Bridges

Add short bridge sentences only when they help the reader follow causality. Place a bridge at the **start** of the section it introduces — directly under the heading, before the first subsection — not as a trailing "next we will…" sentence on the previous section. Leading bridges signal what's coming and let the reader engage; trailing bridges leak structure across section boundaries. A bridge may be declarative or a concise guiding question that the following subsections answer. In Markdown, prefer rendering bridge lines as blockquotes on their own line when that fits the document's existing style.

Good bridges (preferred blockquote form):

> These metrics require three categories of source data.
>
> Once the persistence model is fixed, the remaining change surface is which existing systems must carry the tracking fields.
>
> 双 ID 在主链路上如何生成与传递？

Bad bridges (trailing meta-narration; same patterns in both languages):
- "This section will now explain..."
- "The following section is about..."
- "This document is written in this order because..."
- "下面说明…"、"接下来介绍…"、"本节将…"、"至此 X 完成，下面 Y…"

## Definition vs implementation

Keep these layers distinct. If a document mixes them, move the definition earlier and the implementation later unless the document is explicitly implementation-focused.

- **Definition layer:** goals; metric meaning; business semantics; responsibility boundaries; conceptual models.
- **Implementation layer:** formulas; aggregation rules; field mappings; API payload details; SQL / pipeline / algorithm specifics; rollout diffs.

## Evidence, claims & actionability

Apply when the document makes important claims, recommends or compares solutions, asks readers to trust an outcome, or describes work the reader must execute.

1. Start from the bottleneck, not the feature. State the constraint or failure mode the document resolves.
2. For important claims, preserve the source-backed chain where available: claim → mechanism → evidence → limitation. If a link is missing, flag it.
3. For improvement claims, identify the baseline, test condition, evaluation criteria, result, and caveat. Quantify against a named baseline, or qualify the narrow test instead of turning it into a universal claim.
4. Keep evidence near the claim it supports, and separate observed result from interpretation. Do not leave metrics, screenshots, or examples disconnected from their interpretation.
5. Treat examples as evidence. A strong example includes input or context, environment or precondition, output or behavior, result quality, and the conclusion the reader should draw.
6. Compare alternatives by criteria such as correctness, reliability, cost, latency, complexity, maintainability, rollout risk, and reversibility. Preserve each option's source-backed strength before stating its boundary; if strengths are not stated, flag the gap instead of inventing balance.
7. Keep implementation detail only when it helps the reader judge feasibility, constraints, reliability, or tradeoffs.
8. Put known failure modes, dependency assumptions, incomplete coverage, and mitigations close enough to the solution that reviewers can judge risk.
9. Tie future plans to current gaps. Distinguish committed work, exploratory direction, and open questions.
10. Use an inspect → classify → guide → verify pattern when work changes by type or risk: ground the classification in source evidence, then tailor guidance, then verify completeness. Separate exploration, decision, execution, and verification when they need different information or checks. For runbooks, separate diagnosis from recovery validation; for postmortems, turn the incident into an updated impact model or checklist without hiding remaining unknowns.
11. Convert tacit expert judgment into reusable, executable forms: checklists, decision tables, phased workflows, risk categories, failure-mode lists, validation criteria — with explicit next steps, owners, prerequisites, inputs, outputs, commands, schemas, or success criteria when the reader must act. Keep checklist items specific enough to execute; avoid vague items like "consider quality" or "handle edge cases" unless expanded into concrete checks.
12. For adoption or onboarding sections, provide a complete path: prerequisites, installation or configuration, invocation, success verification, troubleshooting, and owner or feedback channel when available.

## Tables vs prose

Use tables for repeated columns of meaning, such as:
1. Goal → data need → current gap
2. Metric → definition → granularity → required data
3. Metric → calculation rule → formula
4. Field name → type → required → meaning
5. Source field → storage field
6. Tool / system → change scope
7. Option → tradeoff comparison
8. Scenario → input → output → verification
9. Risk → cause → impact → mitigation
10. Phase → action → owner → success criteria
11. Baseline → proposed approach → metric → result → caveat
12. Audience → concern → section or action path

Prefer prose when: the content explains one idea; the reader needs narrative buildup; the relationship is causal rather than tabular; or the content explains a caveat, tradeoff, or hidden causal chain.

If two sections present parallel structures at different abstraction levels, use parallel table shapes. Use tables only when the columns are stable and comparable; forcing ambiguous reasoning into a table can hide nuance. Concision means putting detail in the right medium, not minimizing word count.

## Media, code & native blocks

1. Preserve screenshots, videos, diagrams, whiteboards, callouts, chat cards, citations, and other native document blocks unless the user asks to remove or convert them.
2. Every image, video, diagram, table, or code block should have an editorial job: proof, instruction, architecture explanation, workflow explanation, or reference.
3. Introduce code blocks with what they demonstrate and, when useful, summarize the design point after the block.
4. Avoid long raw dumps unless necessary for reproducibility, API contracts, schema review, or implementation reference.
5. Preserve existing callouts; use new callouts sparingly for key conclusions, warnings, assumptions, or caveats when the format supports them.
6. Shorten generic motivation once the core problem is clear; spend words on hidden complexity, causal chains, tradeoffs, and concrete failure modes.

## Language & voice

1. Prefer direct, declarative prose. Replace rhetorical questions and slogan-like phrasing with literal statements; remove author-facing meta-writing.
2. Break overloaded sentences that mix definition, justification, and prescription.
3. Define domain terms once and reuse them consistently. Remove duplicated claims, repeated caveats, and low-information transitions.
4. Avoid generic AI cadence such as mirrored sentence patterns, hedge clusters, and filler transitions.
5. Keep headings specific and professional.
6. Prefer action verbs with clear objects. Replace vague phrases like "improve capability" with concrete actions such as "classify requests", "merge checks", "reduce payload size", or "validate rollback".
7. Make strong claims bounded — pair confident wording with scope, condition, evidence, or limitation instead of broad intensifiers. Reserve emphasis for load-bearing words. Prefer binding the qualifier into the claim over deleting the strong word: write "accurate within the tested range" or "limited-but-real" so the limiter rides in the same sentence as the strong word, rather than dropping "accurate" or leaving it unbounded.

**English:** prefer concrete verbs and short, stable sentence shapes; avoid stacked abstractions and vague intensifiers.

**Chinese:** avoid literal translation, stiff 翻译腔, and long chained modifiers. Use Chinese for explanation, judgment, and action when the base document is Chinese. Keep English only for fixed field terms, APIs, product names, tool names, and identifiers; clean up spacing and term consistency around mixed Chinese/English tokens. Prefer precise verbs that describe the actual operation; avoid vague verbs such as 提升、优化、赋能 unless the mechanism is clear.

**Both languages:** prefer precise professional wording over conversational performance; keep personification limited when precision matters; preserve established names, product terms, acronyms, and code identifiers. If the document has a clear base language, rewrite stray foreign tokens into it unless they function as a proper name, fixed term, brand, or identifier. Prefer native phrasing over token-level mixing. Avoid copying catchy motifs, slogans, or metaphors unless grounded by evidence and useful as navigation anchors.

## Finish checks

Final scan for high-risk slips not already obvious from the rules above (see Truth preservation, Structure rules, Evidence/claims/actionability):

1. Numbers, names, dates, or table values silently changed against the source.
2. Title drifts from the body's actual scope, or the opening scope and the closing validation no longer match.
3. A closing or final section introduces new scope.
4. A rule the document itself states is contradicted elsewhere in the document.
5. A claim left without its supporting evidence or interpretation.
6. A strong claim whose caveat or limitation sits sections away from it, instead of bound to the claim where the reader meets it (e.g., a header promising "precise" while the limitation hides in a later section).
7. The reader is sent to machine-local file paths or other local documents without the user asking for that form.

## Communication

**Review mode** — if the user asks for a review, report findings first, grouped:
1. Structural issues
2. Accuracy or scope-preservation issues
3. Logical-chain issues
4. Abstraction issues
5. Evidence, limitation, or tradeoff issues
6. Actionability or verification issues
7. Wording or naturalness issues

**Optimize mode** — if the user asks to optimize, edit directly, then summarize:
1. What was reorganized
2. What was clarified or left unchanged to preserve accuracy
3. What was removed or deduplicated
4. What evidence, limitation, or actionability gaps were improved
5. Any remaining ambiguities or open choices
