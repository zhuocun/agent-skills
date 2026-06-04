---
name: chinese-diction
description: >-
  Write natural, professional Chinese at the word-choice, phrasing, and register level. Use when the user wants to write Chinese, translate into Chinese, polish Chinese wording, remove translationese, make Chinese sound more idiomatic, or choose better Chinese diction. Preserve meaning and keep code identifiers, acronyms, product names, field names, citations, numbers, and URLs unchanged. This is the prose-quality layer, not document structure or section order. Do not use for agent-instruction files such as SKILL.md, prompts, workflows, or tool-routing docs.
---

# Chinese Diction

A **methodology, not a lookup table.** It teaches the few principles behind good Chinese prose so you can judge *any* phrasing on your own, rather than match a fixed list of fixes. This is the **diction / phrasing / register layer** — word choice, phrasing, and register, not document structure or section order.

## The core instinct

Write the way a careful, senior professional writes Chinese: **plainly and precisely, with nothing reaching to impress.** Before keeping any phrase, ask whether it is (a) English grammar in disguise, (b) an invented, hard-translated, or needlessly English word, (c) vividness the meaning doesn't need, (d) off-register — too chatty or too bureaucratic, or (e) reaching for more force than the claim warrants. If any, rewrite to the plain form.

The one test that resolves most cases: **when two phrasings say the same thing, use the plainer, more measured one.** A figure of speech earns its place only by adding *precision*; an absolute word (`只能`/`必须`/`一定`) earns its place only when the claim truly is absolute. If they add mere flavor or force, cut them. Prefer verbs with clear objects over abstract nouns: say what is being identified, compressed, merged, verified, or exposed. Plainer means clearer, not shorter — write each word in its complete, natural form, never a clipped shorthand.

## The seven failure modes

### 1. 翻译腔 — English mechanics wearing Chinese words

Chinese must carry Chinese sentence structure, not transliterated English structure. Tells: long modifier chains stacked before a noun, `被…所…`, connector pile-ups (`由于…因此…并且`), nominalized verbs (`进行…的处理`), parallelism forced for symmetry, subject drift mid-sentence.

- ✗ 一个在类型层无法产出非法结果的受约束的接口
- ✓ 一个受约束的接口—其在类型层就无法产出非预期的结果

*Principle:* when modifiers pile up before the noun, move them into a main clause or a trailing explanation.

### 2. 用词不当 — coined, hard-translated, or needlessly English

Reach for the word that already exists in natural Chinese. Three ways it goes wrong:

- **Coining / hard-translating** — ✗ 爆炸半径 (blast radius) · 决策面 · 越界旗 → ✓ 影响面 · 决策面板 · 越界标记.
- **Needless English** (the more common mistake) — default to Chinese; most "engineer English" has a settled Chinese form. ✗ hatch 出一个对象 · 非法 transition · 一个 proposed delta · post-stamp 镜像 → ✓ 生成一个对象 · 非法的状态转移 · 一处拟议变更 · 盖章后的镜像（同理 capability→能力、typed→带类型的、invariant→不变量）. Keep English only when there is *no* natural Chinese equivalent: bare acronyms (`LLM` `API` `SPA` `CFG` `FSM` `MCP`), a term genuinely canonical as English in the field (`agent`), or a literal code identifier / enum (kept verbatim under mode 7).
- **Over-correcting** — don't strip genuine settled terms: `幂等` (idempotent), `回滚` (rollback), `死锁` (deadlock) are real, not coinages. And "looks technical" ≠ settled — a borrowed metaphor merely dressed as a term (`闸口` for a checkpoint, `接缝` for an integration boundary, `魔法整数` for "magic number") only *looks* established and still fails mode 3; use a plain word (关口 / 对接处 / 未说明的常量).

*Principle:* when a Chinese technical text keeps English terms, keep them stable and purposeful. Let English carry fixed names, acronyms, APIs, product names, and identifiers; let Chinese carry explanation, judgment, and action. Clean up spacing and term consistency around mixed Chinese/English tokens.

### 3. 文采型包装 — reaching for vividness the meaning doesn't need

The most common failure in "clever" drafts. Several sub-forms, one principle: cut any figure that adds only flavor.

- **Personification** — ✗ 会自证、会模拟的活对象 → ✓ 一个能自我校验和模拟的实体
- **Branded label** (a plain idea dressed as a coined term) — ✗ 新基座的原语 → ✓ 新系统的基本构件
- **Noun-as-metaphor** — ✗ 这是物理 / 物理底线 → ✓ 这是硬性约束 *(the adverb 物理上 = "physically" is literal — keep it)*
- **Slogan / hyperbole** — ✗ 回滚到最后一毫秒 → ✓ 操作前均可回滚
- **Business/strategy slogans** — ✗ 全面提升系统智能化水平、赋能业务高质量增长 → ✓ 提升策略配置效率、增强链路稳定性、提高问题定位可见性

*Principle, generalized:* the same instinct disposes of drama (`重生`→`重写后`), violent verbs (`砸`/`杀死`/`焊死`→`投入`/`消除`/`锁定`), and wrong-connotation words — `廉价`→`低成本` (cheap carries "shoddy"), `投机性`→`没把握` (投机 means opportunism, not *speculative*), `一刀切`→`彻底分开` (一刀切 is pejorative) when you mean a clean separation.

### 4. 语域失稳 — drifting off the professional register

There are **two opposite failures**, and over-correcting one produces the other. Aim for the steady middle.

- ✗ too casual / narrative: 新来的销售只说一句话:…… ｜ 他得先弄清 ｜ 全靠人工算
- ✗ too stiff / 八股: 销售人员仅须以一语陈明其诉求 ｜ 悉数依赖人工核算
- ✓ right: 销售只需用一句话说明诉求 ｜ 需先确定 ｜ 依赖人工计算

*Principle:* cut narrative openers, casual pronoun + 得, telegraphic fragments, over-strong adverbs (`根本`/`全靠`), dramatic time-moments (`那一刻`/`落下`) — **but** keep concrete, earned phrasing (a vivid "一分钟看懂" beats a flat "高效"), and never reach for bookish filler (`悉数`/`须臾`/`业已`). De-colloquial is not the same as formal.

### 5. 绝对化措辞 — categorical words that over-claim

Reaching for force or certainty the claim doesn't warrant reads as strident or naive; measured phrasing reads as mature and more credible. Default away from `只能` / `必须` / `一定` / `永远` / `完全` / `绝对` / `任何` / `一旦…就` / `根本`; prefer `通常` / `往往` / `多数` / `倾向于` / `可` / `需`.

- ✗ 这一步只能依赖人工计算 → ✓ 这一步依赖人工计算
- ✗ 一旦接近关口,就必须切换到人工 → ✓ 接近关口时,需要切换到人工

*Principle:* keep an absolute only when the claim genuinely is absolute — "盖章后不可逆" is a fact, and hedging it would be false. The rule is don't reach for force you don't need, not "never be definite." (Fittingly, this rule is itself a default, not an absolute.)

### 6. 过度压缩 — clipped words that should be written in full

Trimming a word or phrase below its natural Chinese form to save characters reads as incomplete shorthand, not concision. Write the whole form. (Distinct from document-level concision, which removes redundant *sentences* — never truncate an individual word.)

- ✗ 无需重录 → ✓ 无需重复录入
- ✗ 交人把关 → ✓ 交由负责人把关
- ✗ 手维护 config 文件的持续漂移 → ✓ 需手动维护的 config 文件的持续漂移
- ✗ 这是现实世界的硬约束,代码改不掉 → ✓ 这是现实世界的硬性约束,无法通过修改代码来避免

*Principle:* prefer the complete, natural form (`硬性约束` / `重复录入` / `手动维护`) over the clipped one (`硬约束` / `重录` / `手维护`). Read it aloud — if it sounds like a telegram or a variable name, expand it.

### 7. 破坏保真 — touching what isn't style

Identifiers, enums, field/API names, code symbols, numbers, citations, author names, URLs are **correctness, not wording**. Copy them byte-for-byte; never translate or "tidy" them.

## Two sentence-craft moves

- **`不是 A,而是 B` → `是 B,而非 A`.** More natural — but **front clause B**, or a blind connector swap inverts the meaning. ✓ 是取代表单,而非用 AI 优化表单。
- **Split overloaded sentences.** One that bundles definition + justification + instruction reads as three; give each its own sentence.

## Technical prose patterns

Use these when polishing Chinese technical or business-technical prose.

1. **Name the bottleneck plainly.** Prefer `配置分散`、`链路协同成本高`、`问题定位依赖人工` over vague openings like `当前存在一些问题`.
2. **Use action verbs with objects.** Prefer `识别风险类型`、`合并重复规则`、`压缩返回内容`、`校验回滚结果` over `提升能力`、`优化体验`、`赋能增长`.
3. **Bound strong claims.** Pair confident claims with scope, condition, evidence, or limitation. Prefer `在该测试场景下可降低请求耗时` over `全面提升准确性`.
4. **Acknowledge alternatives with source-backed precision.** If the source says another option has an advantage, keep it before stating the boundary; do not invent balance for tone.
5. **Keep concept names stable.** Pick one Chinese name for a recurring concept and reuse it across headings, tables, and cross-references. Do not rotate synonyms for literary variety.
6. **Let memorable phrases earn their place.** A phrase like `不知道自己不知道什么` works because it names a real failure mode. If a motif is only catchy, replace it with the concrete mechanism.

## How to apply

- **Create** — write to these principles from the first draft; far cheaper than retrofitting.
- **Optimize** — read the whole text once; scan by failure mode (1–6); for a recurring load-bearing term, pick *one* replacement and apply it everywhere, including cross-references and any heading that names it; preserve fidelity (mode 7); resist over-correction (mode 4); then re-read cold.
- **Translate** — read for *meaning*, then write that meaning as Chinese; never go clause-by-clause. Translation is where 翻译腔 creeps in most.

## Self-check

- [ ] Chinese sentence structure throughout — no stacked modifiers, no `被…所…`, no connector pile-ups, no subject drift.
- [ ] No coined or hard-translated words; no needless English (default to Chinese; keep only bare acronyms / a canonical term like `agent` / code identifiers); genuine settled terms not over-translated.
- [ ] No vividness that adds only flavor — no personification, branded labels, noun-metaphor, slogans, drama, or wrong-connotation words.
- [ ] Register steady — neither chatty/narrative nor bureaucratic.
- [ ] No absolute/categorical words reached for by default (`只能`/`必须`/`一定`/`永远`/`一旦…就`) — measured phrasing unless the claim is genuinely absolute.
- [ ] No clipped/over-shortened words — each written in its complete natural form (`硬性约束` not `硬约束`, `重复录入` not `重录`).
- [ ] `不是A而是B` rewritten as `是B,而非A` with B fronted.
- [ ] Identifiers, numbers, citations, author names, URLs byte-for-byte unchanged.
- [ ] A domain-literate cold reader flows start to finish without stopping on a word.

## Maintenance

Keep the frontmatter YAML-safe. The description uses folded `>-` style so stricter parsers can load it reliably.
