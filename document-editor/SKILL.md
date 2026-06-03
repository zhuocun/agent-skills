---
name: document-editor
description: Edit formal human-facing documents at the document level without changing their meaning. Use for design docs, RFCs, implementation plans, proposals, specs, guides, decision memos, and review docs when the user wants to improve scope, structure, logical flow, reader fit, factual fidelity, concision, terminology, tables, or reviewability. Do not use for casual notes, chat replies, pure sentence-level wording polish, or agent-instruction files such as SKILL.md, prompts, workflows, or tool-routing docs.
---

# Document Editor

Edit formal human-facing documents so readers can understand them quickly, review them accurately, and act with less friction. Preserve meaning; improve how the document is scoped, ordered, explained, and worded.

## Core Standard

A strong document is:
1. Logically smooth: section order follows the reader's decision path and the argument moves forward without jumps.
2. Accurate: the rewrite preserves the source meaning, facts, scope, and decisions unless the user explicitly asks for substantive changes.
3. Concise: each section earns its place and repeated points appear once in the clearest location.
4. Natural: the prose reads like it was written by a careful professional in the target language, not mechanically translated or LLM-shaped.
5. Self-contained: the reader should not need machine-local paths or off-page local references to understand the main point unless the user explicitly asks for them.
6. Decision-oriented: the document helps the reader decide, act, or verify an outcome with source-backed support and executable next steps where useful.

A strong document lets the reader answer:
1. What is this document about?
2. Why does it matter?
3. What is being proposed, defined, or decided?
4. What are the constraints, tradeoffs, and implications?
5. What should happen next?
6. What support, risk, or action path matters for my decision?

## First Pass

Before editing, infer or identify:
1. Document type
2. Intended audience
3. Primary purpose
4. Intended abstraction level
5. The decision or action the reader should take after reading
6. The reader contract: what the document promises to help the reader decide or do
7. The concrete bottleneck, failure mode, or uncertainty the document exists to resolve
8. What the reader already knows, and what context they need before they can judge the rest

Keep the document aligned to these inputs.

## Truth-Preservation Rules

1. Preserve the source meaning unless the user asks for substantive changes.
2. Do not silently change numbers, dates, owners, field names, API names, formulas, requirements, or decisions.
3. If the source is ambiguous, inconsistent, or incomplete, flag it instead of inventing a cleaner version.
4. When tightening prose, remove wording noise, not business meaning.

## Section Order Patterns

Choose the pattern that best matches the document type.

### High-Level Design / Review Doc

Recommended order:
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

Use this order when the design depends on domain framing or named concepts that must be defined first, or when the success criteria depend on understanding the proposed design first.

### Implementation Design Doc

Recommended order:
1. Scope
2. Assumptions / prerequisites
3. Current state
4. Target behavior
5. Detailed changes
6. Data flow / edge cases / migration rules
7. Testing / rollout / rollback
8. Risks / open questions

### Decision Memo / ADR / RFC

Recommended order:
1. Context
2. Decision to be made
3. Options
4. Evaluation / tradeoffs
5. Recommendation / final decision
6. Consequences

### Technical Solution / Tool / Adoption Doc

Recommended order:
1. Positioning summary: what this is, who it is for, and the value it promises
2. Problem / why now / concrete bottleneck
3. Existing approach limits or failure modes
4. Proposed capability / design principle
5. Proof: demo, realistic example, measured result, or comparison
6. Quick start / usage path when adoption matters
7. Alternatives / comparison / tradeoffs
8. Technical implementation / architecture / workflow
9. Limitations / known failure modes / mitigations
10. Roadmap / Q&A / next steps

Use this order for technical sharing, launch, adoption, onboarding, or proposal docs that must help readers understand, try, trust, and maintain a solution. Move the quick start earlier when the primary reader needs to try the tool before reviewing proof or internals.

### Workflow / Guidance Doc

Recommended order:
1. When to use it
2. Trigger conditions / classification rules
3. Inspect / source-grounding steps
4. Guidance, decision table, or operating workflow
5. Verification checklist
6. Escalation / fallback / limitations

Use this order for runbooks, troubleshooting guides, operating procedures, migration guides, or recurring implementation workflows where the reader must execute a safe sequence.

## Structure Rules

1. The title must match the real scope.
2. Add second-level headings where they improve structure and clarity, numbered hierarchically (a `1.` heading with `1.1` / `1.2` subheadings).
3. Put early what the reader needs in order to judge the rest.
4. Keep abstraction layers separated.
5. Define concepts before formulas, field mappings, or rollout diffs.
6. If the design depends on a named framework, operating model, or domain term, define that context before using it to justify the design.
7. For architectural or product design docs, replace code-level references, file paths, and implementation labels with business or system concepts unless the user explicitly asks for development-level detail.
8. Add short bridge sentences only when they help the reader follow causality. Place a bridge at the **start** of the section it introduces — directly under the heading, before the first subsection — not as a trailing "next we will…" sentence on the previous section. Leading bridges signal what's coming and let the reader engage; trailing bridges leak structure across section boundaries. In Markdown documents, prefer rendering bridge lines as blockquotes on their own line when that fits the document's existing style.
9. A bridge may be declarative or a concise guiding question that the following subsections answer.
10. Use tables for repeated structures and prose for causal explanation.
11. Preserve the reader journey over the author journey. Do not order sections by how the team built the system unless that history is the reader's task.
12. When the document claims a new solution is better, surface existing baselines or alternatives; if they are missing, flag the gap instead of inventing them.
13. Separate audience paths when one document serves reviewers, adopters, operators, and implementers.
14. Do not let future plans compensate for weak present evidence.

Good bridge examples in the preferred blockquote form:

> These metrics require three categories of source data.
>
> Once the persistence model is fixed, the remaining change surface is which existing systems must carry the tracking fields.
>
> 双 ID 在主链路上如何生成与传递？

Bad bridge examples (trailing meta-narration; same patterns in both languages):
- "This section will now explain..."
- "The following section is about..."
- "This document is written in this order because..."
- "下面说明…"、"接下来介绍…"、"本节将…"、"至此 X 完成，下面 Y…"

## Definition vs Implementation

Keep these layers distinct.

### Definition Layer

Use for:
1. Goals
2. Metric meaning
3. Business semantics
4. Responsibility boundaries
5. Conceptual models

### Implementation Layer

Use for:
1. Formulas
2. Aggregation rules
3. Field mappings
4. API payload details
5. SQL / pipeline / algorithm specifics
6. Rollout diffs

If a document mixes both layers, move the definition earlier and the implementation later unless the document is explicitly implementation-focused.

## Evidence and Decision Rules

Use these rules when the document makes important claims, recommends a solution, compares approaches, or asks readers to trust an outcome.

1. Start from the bottleneck, not the feature. State the constraint or failure mode the document resolves.
2. For important claims, preserve the source-backed chain where available: claim -> mechanism -> evidence -> limitation. If a link is missing, flag it.
3. For improvement claims, identify the baseline, test condition, evaluation criteria, result, and caveat.
4. Keep evidence near the claim it supports. Do not leave metrics, screenshots, or examples disconnected from the interpretation.
5. Separate observed result from interpretation. Qualify narrow tests instead of turning them into universal claims.
6. Treat examples as evidence. A strong example includes input or context, environment or precondition, output or behavior, result quality, and the conclusion the reader should draw.
7. Compare alternatives by criteria such as correctness, reliability, cost, latency, complexity, maintainability, rollout risk, and reversibility.
8. Keep implementation detail only when it helps the reader judge feasibility, constraints, reliability, or tradeoffs.
9. Put known failure modes, dependency assumptions, incomplete coverage, and mitigations close enough to the solution that reviewers can judge risk.
10. Tie future plans to current gaps. Distinguish committed work, exploratory direction, and open questions.

## Actionability and Expert Knowledge

Good documents transfer expert judgment, not only facts.

1. Use an inspect -> classify -> guide -> verify pattern when a document describes work that changes by type or risk. First ground the classification in source evidence, then tailor guidance, then verify completeness.
2. Separate exploration, decision, execution, and verification when those phases require different information or checks.
3. Convert tacit expert knowledge into reusable forms: checklists, decision tables, phased workflows, risk categories, failure-mode lists, or validation criteria.
4. Make guidance executable. Use explicit next steps, owners, prerequisites, inputs, outputs, commands, schemas, or success criteria when the reader must act.
5. For adoption or onboarding sections, provide a complete path: prerequisites, installation or configuration, invocation, success verification, troubleshooting, and owner or feedback channel when available.
6. For runbooks or troubleshooting guides, separate diagnosis from recovery validation.
7. For postmortems, turn the incident into an updated impact model or checklist without hiding remaining unknowns.
8. Keep checklists specific enough to execute. Avoid vague items like "consider quality" or "handle edge cases" unless they are expanded into concrete checks.

## Tables vs Prose

Use tables for repeated columns of meaning, such as:
1. Goal -> data need -> current gap
2. Metric -> definition -> granularity -> required data
3. Metric -> calculation rule -> formula
4. Field name -> type -> required -> meaning
5. Source field -> storage field
6. Tool / system -> change scope
7. Option -> tradeoff comparison
8. Scenario -> input -> output -> verification
9. Risk -> cause -> impact -> mitigation
10. Phase -> action -> owner -> success criteria
11. Baseline -> proposed approach -> metric -> result -> caveat
12. Audience -> concern -> section or action path

Prefer prose when:
1. The content explains one idea
2. The reader needs narrative buildup
3. The relationship is causal rather than tabular

If two sections present parallel structures at different abstraction levels, use parallel table shapes.

## Media, Code, and Native Blocks

1. Preserve screenshots, videos, diagrams, whiteboards, callouts, chat cards, citations, and other native document blocks unless the user asks to remove or convert them.
2. Every image, video, diagram, table, or code block should have an editorial job: proof, instruction, architecture explanation, workflow explanation, or reference.
3. Introduce code blocks with what they demonstrate and, when useful, summarize the design point after the block.
4. Avoid long raw dumps unless they are necessary for reproducibility, API contracts, schema review, or implementation reference.
5. Preserve existing callouts and use new callouts sparingly for key conclusions, warnings, assumptions, or caveats when the document format already supports them.

## Language Rules

1. Prefer direct, declarative prose.
2. Remove author-facing meta-writing.
3. Replace rhetorical questions and slogan-like phrasing with literal statements.
4. Break overloaded sentences that mix definition, justification, and prescription.
5. Define domain terms once and reuse them consistently.
6. Remove duplicated claims, repeated caveats, and low-information transitions.
7. Avoid generic AI cadence such as mirrored sentence patterns, hedge clusters, and filler transitions.
8. Keep headings specific and professional.

For English:
- Prefer concrete verbs and short, stable sentence shapes.
- Avoid stacked abstractions and vague intensifiers.

For Chinese:
- Avoid literal translation, stiff 翻译腔, and long chained modifiers.

For both languages:
- Prefer precise professional wording over conversational performance.
- Keep personification limited when precision matters.
- Preserve established names, product terms, acronyms, and code identifiers.
- If the document has a clear base language, rewrite stray foreign tokens into that language unless they function as a proper name, fixed term, brand, or identifier.
- Prefer native phrasing over token-level mixing.

## Finish Checks

Before finishing, verify:
1. The title matches the body.
2. The opening scope matches the closing validation.
3. Facts, counts, names, and tables still match the source.
4. Terms are aligned.
5. Named frameworks, operating models, or domain terms are defined before they are used to justify the design.
6. Architectural or product design docs use business or system concepts instead of code-level references, file paths, and implementation labels unless the user explicitly asks for development-level detail.
7. Final sections do not introduce new scope.
8. Repeated points appear once in the strongest location.
9. The document sounds native to the target language and register.
10. Mixed-language terms are preserved only when they are standard names, identifiers, or established domain terms.
11. A cold reader can answer what the document is about, why it matters, what is being proposed or decided, the key constraints or tradeoffs, and what should happen next.
12. The document does not send the reader to machine-local file paths or other local documents unless the user explicitly asks for that form.
13. Major claim, limitation, and actionability gaps are handled by the evidence and actionability rules, or clearly called out as unresolved.

## Workflow

When optimizing a document:
1. Read the full document once without editing.
2. When the edit affects claims, scope, structure, evidence, or accuracy, inspect available or referenced source material before judging those areas; otherwise keep source checks lightweight.
3. Write down the current section order in one line each.
4. Identify the document type, audience, reader contract, bottleneck, and intended decision or action.
5. Identify gaps in scope, structure, logic, evidence, alternatives, limitations, actionability, accuracy, duplication, and language fit.
6. Fix issues in this order: scope and audience fit, reader contract, bottleneck framing, section order, evidence chain, abstraction layering, logical chain, action path, accuracy, duplication, terminology, then wording.
7. Tighten bridges and headings.
8. Convert repeated structures into tables, checklists, workflows, or decision aids where useful.
9. Separate definitions from implementation details.
10. Tighten language for directness, concision, and naturalness.
11. Run the finish checks.

## Communication

If the user asks for a review, report findings first:
1. Structural issues
2. Accuracy or scope-preservation issues
3. Logical-chain issues
4. Abstraction issues
5. Evidence, limitation, or tradeoff issues
6. Actionability or verification issues
7. Wording or naturalness issues

If the user asks to optimize the document, edit directly and then summarize:
1. What was reorganized
2. What was clarified or left unchanged to preserve accuracy
3. What was removed or deduplicated
4. What evidence, limitation, or actionability gaps were improved
5. Any remaining ambiguities or open choices
