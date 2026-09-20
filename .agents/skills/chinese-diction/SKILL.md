---
name: chinese-diction
description: >-
  Write natural Chinese that fits its target register — professional, casual, or creative — at the word-choice, phrasing, and register level. Use when the user wants to write Chinese, translate into Chinese, polish Chinese wording, remove translationese, make Chinese sound more idiomatic, or choose better Chinese diction, in any human-facing prose — documents, reports, chat messages, announcements, notices, UI strings, marketing copy, contracts, or casual and creative writing. Preserve meaning and keep code identifiers, acronyms, product names, field names, citations, clause and statute numbers, quoted figures with their units, numbers, and URLs unchanged. This improves wording, phrasing, and register only, not document structure or section order. Do not use for agent-instruction files such as SKILL.md, prompts, workflows, or tool-routing docs.
---

# Chinese Diction

A **methodology, not a lookup table.** It teaches the few principles behind good Chinese prose so you can judge *any* phrasing on your own, rather than match a fixed list of fixes. It works at the level of **diction, phrasing, and register** — word choice and sentence texture, not document structure or section order — in whatever register the text is meant for. Once active it persists across later tasks and sessions until the user explicitly turns it off; it never decides whether to write Chinese, only how, so it governs any Chinese prose you go on to write, translate, or polish for a human reader, and still never applies to agent-instruction files.

Priority order, highest first: **fidelity, preserved meaning, Chinese sentence structure, register fit, wording.** Fidelity outranks every wording rule: where a token is both a literal identifier and an English word with a settled Chinese form, it stays verbatim — `config 文件` keeps `config` because it names an actual file, while a bare `capability` in running prose becomes `能力` under mode 2. Where two wording rules disagree, the one that restores information to the reader outranks the one that removes a word: expand the clipped form (mode 6) before trimming the figure (mode 3), and keep earned concreteness (mode 4) over reflexive plainness.

## The core instinct

Settle five variables first. Infer each from the text and the ask; ask the user only where a setting changes the wording and nothing in front of you decides it. All five select **wording only** — never the document's sections or their order.

- **Register** — professional / casual / creative. [professional]
- **Medium and genre** — what the text is (chat message, notice, article, UI string, slide, email, contract, spoken script) and what it is for (inform, instruct, oblige, warn, persuade). [running prose, to inform]
- **Locale and script** — mainland / Taiwan / Hong Kong / Singapore, and simplified / traditional. Two axes, not one. [mainland simplified]
- **Relationship** — upward / downward / peer / outward to a client or the public. [peer]
- **Domain** — the field whose settled vocabulary governs. [none assumed]

With those settled, write the way a careful native writer writes in that register: **plainly and precisely, with nothing reaching to impress** — where plain means measured exposition in professional prose, conversational ease in casual prose, controlled imagery in creative prose. Before keeping any phrase, ask whether it is (a) English grammar in disguise, (b) an invented, hard-translated, or needlessly English word, (c) vividness the text's purpose doesn't need, (d) off-register — drifting from the target in either direction, or (e) reaching for more force than the claim warrants. If any, rewrite to the form the register calls for.

The one test that resolves most cases: **when two phrasings say the same thing, use the plainer, more measured one.** A figure of speech earns its place by adding *precision* — or, in creative prose, an effect the piece genuinely needs; an absolute word (`只能`/`必须`/`一定`) earns its place only when the claim truly is absolute. If they add mere flavor or force, cut them. Prefer verbs with clear objects over abstract nouns: say what is being identified, compressed, merged, verified, or exposed — `识别改动类型`、`压缩返回内容`、`返回搜索任务清单`、`生成验证核查清单`、`定位受影响文件` over `提升能力`、`优化体验`、`赋能增长`. Plainer means clearer, not shorter — write each word in its complete, natural form, never a clipped shorthand.

## Vocabulary best practices

Use abstraction only when it names a stable, reusable concept. A useful term points to one thing, keeps the same meaning throughout the text, and reduces repetition after being defined. Prefer established domain or technical terms; define any nonstandard term at first use in plain language, then reuse its exact name and meaning.

Reject shorthand that merely hides necessary information. If a phrase leaves the reader to infer the subject, condition, action, or result, expand it. Name the actual object (`table`, `field`, `API`, `rule`) and the actual action (`read`, `compare`, `store`, `reject`) instead of using a vague label. Do not ban abstract words mechanically; keep them when their reference is already clear and stable.

Apply three tests:

- **Reference:** Can the target reader identify exactly what the term denotes? Name the mechanism, not the mood — `上下文不足`、`影响范围评估不足`、`组件信息依赖 UI 打标`、`返回内容过长` over vague phrasing like `效果不好`、`提效不明显`、`当前存在一些问题`. ✗ 该员工需在试用期内达成既定目标 → ✓ 该员工需在试用期内完成客户回访、提交月度报表并参加入职培训
- **Stability:** Does the term mean the same thing everywhere? Beware count-based shorthand (`三类异常`、`第四轴`) — it binds the name to a mutable tally that silently breaks when items are added or merged; refer to members by name instead. ✗ 本学期重点考核前两个维度 → ✓ 本学期重点考核课堂参与和作业完成情况. Never let one name denote two different concepts, and never rotate names for one concept: pick one Chinese name for a recurring concept and reuse it across headings, tables, and cross-references, never swapping synonyms for literary variety.
- **Compression:** Does it shorten already-defined repetition rather than conceal unstated information? A productive suffix (`面`/`态`/`位`/`键`) makes coining feel free, but each coinage still owes a definition — ✗ 该字段落入失败面 → ✓ 该字段落入失败处理范围

If any test fails, restore whatever concrete actor or object, condition, action, or result the target reader needs to understand the claim.

**Terms may compress what has already been defined; they must never hide what has not been stated.**

## The seven failure modes

### 1. 翻译腔 — English mechanics wearing Chinese words

Chinese must carry Chinese sentence structure, not transliterated English structure. Tells: long modifier chains stacked before a noun, `被…所…`, connector pile-ups (`由于…因此…并且`), nominalized verbs (`进行…的处理`), parallelism forced for symmetry, subject drift mid-sentence.

- ✗ 一个在类型层无法产出非法结果的受约束的接口
- ✓ 该接口受到约束，在类型层就无法产出非法结果
- ✗ 由甲方在本协议签署之日起三十日内以书面形式提出的解除通知 → ✓ 该解除通知由甲方在本协议签署之日起三十日内以书面形式提出

*Principle:* when modifiers pile up before the noun — more than one `的`-marked pre-modifier on one head noun, or a single pre-modifier that packs an actor, a deadline and a manner around an action before the `的` (由甲方…三十日内…以书面形式提出的), is the countable tell — move them into a main clause or a trailing explanation. Except where the genre needs the noun phrase to carry its own scope, as a contract does (✓ 本协议项下由甲方提供的、经乙方书面确认的技术资料); there the chain is the defining device, not translationese. The chain stays where the noun phrase must delimit a thing the document refers to elsewhere; where it instead states who must do what by when, unstack it into a clause, as the line above does.

### 2. 用词不当 — coined, hard-translated, or needlessly English

Reach for the word that already exists in natural Chinese. Four ways it goes wrong:

- **Coining / hard-translating** — a coinage borrows a shape that looks like a term and asks the reader to supply the meaning; name the thing plainly instead, as ✗ 越界旗 → ✓ 越界标记 does. The test: replace the term with a plain description of what it denotes — if the text loses no information, the term was a coinage. The productive suffixes (`面`/`态`/`位`/`键`) are where this shape appears most.
- **Needless English** (the more common mistake) — default to Chinese; most "engineer English" has a settled Chinese form — ✗ hatch 出一个对象 · 非法 transition → ✓ 生成一个对象 · 非法的状态转移 — and English stays only when there is *no* natural Chinese equivalent: bare acronyms this field's own Chinese writing leaves in English (software `LLM` `API` `SPA` `CFG` `FSM` `MCP`; medicine `CT` `MRI` `PCR`; finance `IPO` `ETF` `ROE`) — the inventory belongs to the settled domain, so read it off that field, not off this list; a term genuinely canonical as English in the field (`agent`); or a literal code identifier / enum (kept verbatim under mode 7).
- **Over-correcting** — don't strip genuine settled terms: `幂等` (idempotent), `回滚` (rollback), `死锁` (deadlock) are real, not coinages. And "looks technical" ≠ settled — a borrowed metaphor merely dressed as a term (`闸口` for a checkpoint, `接缝` for an integration boundary, `魔法整数` for "magic number") only *looks* established and still fails mode 3; use a plain word (关口 / 对接处 / 未说明的常量).
- **Settledness is audience-relative** — a calque that is fixed vocabulary *inside* a field is not a coinage for that field's readers, and is opaque outside it. `爆炸半径` is settled in 混沌工程 and SRE writing and correct there; for a general engineering or business audience write `影响范围`. The same test decides `对赌协议`、`举证责任倒置`、`双盲`: keep the term where the reader owns it, expand it where they do not.

*Principle:* when a Chinese technical text keeps English terms, keep them stable and purposeful. Let English carry fixed names, acronyms, APIs, product names, and identifiers; let Chinese carry explanation, judgment, and action. Clean up spacing and term consistency around mixed Chinese/English tokens.

### 3. 文采型包装 — reaching for vividness the meaning doesn't need

The most common failure in "clever" drafts. Several sub-forms, one principle: cut any figure that adds only flavor.

- **Personification** — ✗ 会自证、会模拟的活对象 → ✓ 能自我校验和模拟的实体
- **Branded label** (a plain idea dressed as a coined term) — ✗ 新基座的原语 → ✓ 新系统的基本构件
- **Noun-as-metaphor** — ✗ 这轮降息是市场的强心针 → ✓ 这轮降息短期内提振了市场信心 *(a metaphor borrowed from another field names nothing; state the mechanism and its bound. A literal adverb is not a metaphor: 物理上 = "physically" is literal — keep it.)*
- **Slogan / hyperbole** — ✗ 回滚到最后一毫秒 → ✓ 操作前均可回滚
- **Business/strategy slogans** — ✗ 全面提升 AI 编码效率、赋能业务高质量增长 → ✓ 降低组件选择和场景匹配成本、提高上下文完整性、减少影响范围遗漏
- **Creative target** (the bar moves, the principle does not) — ✗ 夜色如同一位沉默的巨人，笼罩着整座城市 → ✓ 夜色漫过屋脊，一点点罩住整座城市 *(the simile decorates; 漫过 carries the direction and pace, so it earns its place)*

*Principle, generalized:* the same instinct disposes of drama (`重生`→`重写后`), violent verbs (`砸`/`杀死`/`焊死`→`投入`/`消除`/`锁定`), and wrong-connotation words — `廉价`→`低成本` (cheap carries "shoddy"), `投机性`→`没把握` (投机 means opportunism, not *speculative*), `一刀切`→`彻底分开` (一刀切 is pejorative) when you mean a clean separation. In creative registers the bar moves, not the principle: imagery that produces the intended effect is earned; the empty or reflexive figure — and the wrong-connotation word — fails in every register. Persuasive genres get the same carve-out under the same bound: marketing copy and a pitch may reach for a figure, but it must still name something the reader can check — ✓ 十分钟上手，不用读文档 over ✗ 开启高效协作新体验

### 4. 语域失稳 — drifting off the target register

Judge drift against the register, medium and relationship settled up front. 「他得先弄清」 is a defect in a professional document and correct in a peer chat; the settled trio, not the words, decides. There are **two opposite failures**, and over-correcting one produces the other; for a professional target, aim for the steady middle:

- ✗ too casual / narrative: 新来的销售只说一句话：…… ｜ 他得先弄清 ｜ 全靠人工算
- ✗ too stiff / 八股：销售人员仅须以一语陈明其诉求 ｜ 其须先行明确 ｜ 悉数依赖人工核算
- ✓ right: 销售只需用一句话说明诉求 ｜ 需先确定 ｜ 依赖人工计算
- **casual target:** ✗ 关于周末聚餐一事，请各位于明日前予以回复 → ✓ 周末聚餐，大家明天之前回一下哈 *(under a casual target 回一下 is the natural form, not mode 6 clipping — mode 6 measures against the target register, not against the most formal one)*

*Principle:* for a professional target, cut narrative openers, casual pronoun + 得, telegraphic fragments, over-strong adverbs (`根本`/`全靠`), dramatic time-moments (`那一刻`/`落下`) — **but** keep concrete, earned phrasing (a vivid "一分钟看懂" beats a flat "高效"), and never reach for bookish filler (`悉数`/`须臾`/`业已`). De-colloquial is not the same as formal. When the target is casual, natural speech rhythm and interjections are correct, not defects — the failure there is stiffness leaking in (`进行沟通` where `聊一聊` belongs). When the target is creative, hold the piece's own voice steady. Whatever the target, *unintended* drift between registers within one text is the failure. Quoted speech, a marked aside, and a deliberate collision in creative prose each hold a register of their own on purpose — set them off as quotation or aside, and keep the surrounding text steady — ✓ 他把报告推回来，说“这个数我不认”，之后我们重做了口径

### 5. 绝对化措辞 — categorical words that over-claim

Reaching for force or certainty the claim doesn't warrant reads as strident or naive; measured phrasing reads as mature and more credible. Default away from `只能` / `必须` / `一定` / `永远` / `完全` / `绝对` / `任何` / `一旦…就` / `根本`; prefer `通常` / `往往` / `多数` / `倾向于` / `可` / `需`.

- ✗ 这一步只能依赖人工计算 → ✓ 这一步依赖人工计算
- ✗ 一旦接近关口，就必须切换到人工 → ✓ 接近关口时，需要切换到人工

Bound a strong claim rather than softening it away: pair a confident claim with scope, condition, evidence, or limitation, and with numbers include the measurement basis when it matters. Prefer `在该测试场景下可降低请求耗时`、`Code 完成度 = 正确实现数 / 功能点总数`、`准确性有限` over `全面提升准确性`、`仍有优化空间`.

The opposite failure is over-hedging into mush: stacking softeners (`可能…也许…或许…`) or weakening the verb itself buries the claim. State the cause→effect flatly and quarantine the single honest qualifier into one measured quantifier.

- ✗ 相关信息可能也许不太会被 AI 考虑到 → ✓ 相关信息若不在 AI 的注意力焦点内，被纳入考虑的概率显著降低

Two carve-outs. **Deontic force:** where the settled genre is one that imposes obligation — contract, policy, safety notice, regulatory text — the categorical word *is* the correct form and softening it is a defect — ✓ 严禁在设备通电时拆卸外壳 · ✓ 未经甲方书面同意，乙方不得转让本协议项下的权利和义务. Contract, policy and safety Chinese carries `应` / `不得` / `严禁`, not `需` / `通常`. **Politeness:** distance is not hedging — writing upward or to a client, ✓ 是否方便本周内给我们一个初步意见 · ✓ 我们这边先把口径对齐 are politeness and do not spend the one-qualifier budget.

*Principle:* keep an absolute only when the claim genuinely is absolute — "盖章后不可逆" is a fact, and hedging it would be false. The rule is don't reach for force you don't need, not "never be definite" — and equally, don't drown a real finding in stacked maybes. In casual or creative prose an intensifier is often voice rather than a claim (✓ 这也太好用了吧) — judge it only where it asserts something. (Fittingly, this rule is itself a default, not an absolute.)

### 6. 过度压缩 — clipped words that should be written in full

Trimming a word or phrase below its natural Chinese form to save characters reads as incomplete shorthand, not concision. Write the whole form. (Distinct from document-level concision, which removes redundant *sentences* — never truncate an individual word.)

- ✗ 无需重录 → ✓ 无需重复录入
- ✗ 交人把关 → ✓ 交由负责人把关
- ✗ 手维护 config 文件的持续漂移 → ✓ 需手动维护的 config 文件的持续漂移
- ✗ 这是现实世界的硬约束，代码改不掉 → ✓ 这是现实世界的硬性约束，无法通过修改代码来避免

*Principle:* prefer the complete, natural form (`硬性约束` / `重复录入` / `手动维护`) over the clipped one (`硬约束` / `重录` / `手维护`). Read it aloud — if it sounds like a telegram or a variable name, expand it.

*Bound by medium.* A display slot has its own complete form: a button, menu item, table header, form label or empty state is correctly short, and expanding it is the error — a button reads ✓ 另存为, not ✗ 另存为其他文件; an empty state reads ✓ 暂无数据, while the same idea in an email is ✓ 目前还没有相关数据. Casual chat likewise has its own full forms (✓ 收到 · ✓ 在忙，晚点回). Run this mode over running prose in the settled medium; the read-aloud test judges a sentence, not a label.

### 7. 破坏保真 — touching what isn't style

Some spans are **correctness, not wording**. The test: if altering the span could change what the text asserts, it is not wording. In software that means identifiers, enums, field/API names, code symbols, numbers, citations, author names, URLs; in other domains it means a statute or clause number (`《劳动合同法》第三十九条`), a drug name and its dose (`阿托伐他汀 20 mg`), a quoted figure with its unit, a trademark.

Copy them byte-for-byte; never translate, "tidy", **or** convert them between simplified and traditional. A 简繁 pass over the prose stops at every one of them.

## Three sentence-craft moves

- **`不是 A，而是 B` can be natural.** Keep it when A/B are comparable and the contrast is the point. Rewrite to `是 B，而非 A` only when it improves flow and does not invert emphasis; **front clause B**. ✓ 是取代表单，而非用 AI 优化表单
- **Split overloaded sentences.** One that bundles definition + justification + instruction reads as three; give each its own sentence — unless the genre binds them, as a contract clause does, where a condition and its consequence belong in one sentence (✓ 甲方应于收到发票之日起三十日内付款；逾期的，按未付金额每日万分之五计付违约金).
- **Weld related clauses with native paired connectives.** When two clauses are one causal or contrastive thought the reader would otherwise parse as separate facts, join them with `之所以…是因为…` / `与其…不如…` / `这本质上是…` / `换句话说，…` — the Chinese way to mark the link explicitly. This is the positive counterpart to mode 1's warning against stacked Western connectors (`由于…因此…并且`): one native connective binds, a pile-up of them is translationese. ✗ 精度有限。原因是上下文不足 → ✓ 精度有限，这本质上是上下文不足

## Technical prose patterns

Use these wherever the prose makes claims a reader will act on — technical, business, policy, medical, financial, academic. The examples below are software; the patterns are not. They do not govern casual chat, taglines, or creative prose, where bounding a claim is not the job — a tagline is correctly ✓ 十分钟上手，不用读文档 with no scope clause attached, and a chat reply is correctly ✓ 这个方案我觉得能成

1. **Bridge problem to method through the mechanism.** When moving from problem to solution, use a short bridge: name the surface problem, state the underlying mechanism, then introduce the method. Example: `多模态识图在复杂 UI 中精度有限；这本质上是上下文不足。因此，工具需要先压缩并结构化 Figma 信息。`
2. **Acknowledge alternatives with source-backed precision.** If the source says another option has an advantage, keep it before stating the boundary (`静态工具样式还原度高，但依赖组件打标`); do not invent balance for tone.
3. **Let memorable phrases earn their place.** `最短交互路径` works because it names a product goal; `不知道自己不知道什么` works because it names a failure mode. If a motif is only catchy, replace it with the concrete mechanism.

## How to apply

- **Create** — write to these principles from the first draft; far cheaper than retrofitting.
- **Optimize** — read the whole text once and settle the five variables; scan by failure mode (1–6); run the three vocabulary tests (reference, stability, compression) on every nonstandard term; for a recurring load-bearing term, pick *one* replacement and apply it everywhere, including cross-references and any heading that names it; preserve fidelity (mode 7); resist over-correction (mode 4); then re-read cold.
- **Translate** — read for *meaning*, then write that meaning as Chinese; never go clause-by-clause. Translation is where 翻译腔 creeps in most.

## Self-check

- [ ] Chinese sentence structure throughout — no head noun carrying more than one `的`-marked pre-modifier, and none whose single pre-modifier packs an actor, a deadline and a manner around an action before the `的` (unless the genre needs the noun phrase to delimit a thing the document names elsewhere), no `被…所…`, no connector pile-ups (`由于…因此…并且`), no nominalized `进行…的处理`, no subject drift.
- [ ] No needless English — every English token left in the text is a bare acronym that this domain's own Chinese writing leaves in English (mode 2: software `LLM` `API` `SPA` `CFG` `FSM` `MCP`; medicine `CT` `MRI` `PCR`; finance `IPO` `ETF` `ROE`; for any other field, read the inventory off the settled domain), a term canonical as English in that field (`agent`), or a code identifier; genuine settled terms (`幂等`/`回滚`/`死锁`) are not over-translated into Chinese.
- [ ] No coinage — every nonstandard term, and every `面`/`态`/`位`/`键` suffix form, passes the substitution test: replaced by a plain description of what it denotes, the text loses no information. A term settled for this audience stays; one settled only inside a narrower field is expanded.
- [ ] No vividness the text's purpose doesn't need — no personification, branded labels, noun-metaphor, slogans, drama, or wrong-connotation words; in creative and persuasive prose, each figure earns its effect and still names something checkable.
- [ ] Register, medium and relationship match what was settled — professional / casual / creative, the medium's own forms, upward / downward / peer / outward — and hold steady, never mixing within the text except where the text quotes a speaker, marks an aside, or stages a deliberate collision in creative prose, each set off as quotation or aside.
- [ ] No absolute/categorical words reached for by default (`只能`/`必须`/`一定`/`永远`/`一旦…就`) — measured phrasing unless the claim is genuinely absolute, or the settled genre is one that imposes obligation — contract, policy, safety notice, regulatory text — where `应`/`不得`/`严禁` are the correct form; and no over-hedge mush (`可能…也许…或许`) — one qualifier, placed precisely, not counting distance markers written upward or to a client (`是否方便…`/`我们这边…`), which are politeness rather than hedging.
- [ ] No clipped/over-shortened words in running prose — each written in its complete natural form (`硬性约束` not `硬约束`, `重复录入` not `重录`); display slots and casual chat keep their own short forms.
- [ ] Contrast phrasing preserves emphasis: `不是A而是B` kept when natural, or rewritten as `是B，而非A` only with B fronted and meaning unchanged; one-thought clauses welded with a native connective (`之所以…是因为`/`这本质上是`), not left as disjointed facts; sentences bundling definition + justification + instruction are split, except where the genre binds a condition to its consequence in one clause (a contract).
- [ ] Identifiers, numbers, citations, author names, URLs, statute and clause numbers, drug names and doses, quoted figures with units, and trademarks are byte-for-byte unchanged — including through any 简繁 conversion.
- [ ] Technical claims name a mechanism, dependency, or scope; generic praise or business outcomes like `全面提升`、`智能化水平`、`高质量增长`、`赋能` are replaced with concrete substance, not swapped for milder slogans, unless the source truly supports them.
- [ ] Every advantage, tradeoff and limitation stated in the source appears in the output; no source-stated negative was dropped or softened, and none was invented for balance.
- [ ] Every nonstandard term passes the three vocabulary tests — defined at first use, one meaning everywhere (no count-bound shorthand, no one-name-two-concepts), and compressing defined repetition rather than hiding an unstated subject, condition, action, or result.
- [ ] Locale and script match the settled setting — mainland `软件`/`数据`/`网络` against Taiwan `軟體`/`資料`/`網路`; no simplified and traditional mixed in one text; the 简繁 pass did not run over identifiers or quoted source.
- [ ] Chinese punctuation is fullwidth throughout (，。：；、——……); halfwidth marks appear only inside identifiers, URLs, quoted English, or where they are the surrounding non-Chinese sentence's own punctuation around a cited Chinese phrase.
- [ ] Re-read cold: every term the three vocabulary tests flagged was either replaced or defined at first use, and no sentence needed a second pass to parse.

## Maintenance

Keep the frontmatter YAML-safe. The description uses folded `>-` style so stricter parsers can load it reliably.

Every register-conditional exception in this file ships with a ✓ example in the register it excuses. A register named only in a waiver is not covered by the skill, it is merely exempted, and a model will read the waiver as licence to skip the rule rather than as a different standard to meet.
