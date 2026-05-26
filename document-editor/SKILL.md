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

A strong document lets the reader answer:
1. What is this document about?
2. Why does it matter?
3. What is being proposed, defined, or decided?
4. What are the constraints, tradeoffs, and implications?
5. What should happen next?

## First Pass

Before editing, infer or identify:
1. Document type
2. Intended audience
3. Primary purpose
4. Intended abstraction level
5. The decision or action the reader should take after reading

Keep the document aligned to these five inputs.

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

## Structure Rules

1. The title must match the real scope.
2. Put early what the reader needs in order to judge the rest.
3. Keep abstraction layers separated.
4. Define concepts before formulas, field mappings, or rollout diffs.
5. If the design depends on a named framework, operating model, or domain term, define that context before using it to justify the design.
6. For architectural or product design docs, replace code-level references, file paths, and implementation labels with business or system concepts unless the user explicitly asks for development-level detail.
7. Add short bridge sentences only when they help the reader follow causality. Place a bridge at the **start** of the section it introduces — directly under the heading, before the first subsection — not as a trailing "next we will…" sentence on the previous section. Leading bridges signal what's coming and let the reader engage; trailing bridges leak structure across section boundaries. In Markdown documents, prefer rendering bridge lines as blockquotes on their own line when that fits the document's existing style.
8. A bridge may be declarative or a concise guiding question that the following subsections answer.
9. Use tables for repeated structures and prose for causal explanation.

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

## Tables vs Prose

Use tables for repeated columns of meaning, such as:
1. Goal -> data need -> current gap
2. Metric -> definition -> granularity -> required data
3. Metric -> calculation rule -> formula
4. Field name -> type -> required -> meaning
5. Source field -> storage field
6. Tool / system -> change scope
7. Option -> tradeoff comparison

Prefer prose when:
1. The content explains one idea
2. The reader needs narrative buildup
3. The relationship is causal rather than tabular

If two sections present parallel structures at different abstraction levels, use parallel table shapes.

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

## Workflow

When optimizing a document:
1. Read the full document once without editing.
2. Write down the current section order in one line each.
3. Identify gaps in scope, structure, logic, accuracy, duplication, and language fit.
4. Fix issues in this order: scope and audience fit, section order, abstraction layering, logical chain, accuracy, duplication, terminology, then wording.
5. Tighten bridges and headings.
6. Convert repeated structures into tables where useful.
7. Separate definitions from implementation details.
8. Tighten language for directness, concision, and naturalness.
9. Run the finish checks.

## Communication

If the user asks for a review, report findings first:
1. Structural issues
2. Accuracy or scope-preservation issues
3. Logical-chain issues
4. Abstraction issues
5. Wording or naturalness issues

If the user asks to optimize the document, edit directly and then summarize:
1. What was reorganized
2. What was clarified or left unchanged to preserve accuracy
3. What was removed or deduplicated
4. Any remaining ambiguities or open choices
