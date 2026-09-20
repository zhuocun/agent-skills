# Chinese software-vocabulary evidence notes

These are **evidence notes, not policy.** They record what three research runs could and
could not ground in screened native-Chinese sources, with the auditor's corrections applied.
They were deliberately kept out of the `chinese-diction` skill, which declares itself
"a methodology, not a lookup table" — do not turn this file into the lookup table the skill
refuses to be, and do not cite it as a rule. Use it the way you would use a colleague's
research notebook: check the evidence, then decide.

Two standing cautions. **A blank or NOT-FOUND cell is a finding, not a gap to fill** —
one Chinese form in the source material (`轮值`) was invented rather than observed, and the
audit caught it; nothing ungrounded has been carried into the tables below. And **confidence
here is about the evidence, not about the language** — "weak" usually means one screened
page, not that Chinese speakers are unsure.

## How to read these tables

| Column | Meaning |
| --- | --- |
| Verdict | `SETTLED-CHINESE` · `CONTESTED` (two live forms, no winner) · `PLATFORM-BOUND` (form tracks the product, not the concept) · `KEEP-ENGLISH` (native writing retains the English) · `NOT-FOUND` (no native Chinese form could be grounded) |
| Confidence | `strong` = multi-source or vendor-definitional · `moderate` = sound but one source or one vendor · `weak` = verdict plausible, evidence thin or compromised · `none` = nothing to grade |
| Revised | `yes` where the audit changed the verdict, the confidence, or a Chinese form |

Grades are the **audited** grades. Where a run's own researcher claimed more, the audited
number stands and the note says so.

## 1. English loanwords: does Chinese have a settled form?

Fifteen terms, re-fetched and re-screened by an independent audit. Twelve survive graded,
one was re-verdicted, two stay unresolved.

| English | Verdict | Chinese form(s) | Conf. | Revised | Evidence |
| --- | --- | --- | --- | --- | --- |
| canary / rollout | SETTLED-CHINESE | 灰度发布 (head term); 金丝雀发布 (vendor-stated 又名, narrower) | strong | — | [aliyun SAE](https://help.aliyun.com/zh/sae/perform-a-canary-release-for-an-application) · [aliyun MSE](https://help.aliyun.com/zh/mse/use-cases/service-release-strategies) · [aliyun ALB](https://help.aliyun.com/zh/slb/application-load-balancer/use-alb-to-implement-canary-releases) |
| observability | SETTLED-CHINESE | 可观测性 (clipped 可观测) | strong | — | [aliyun what-is](https://help.aliyun.com/zh/what-is/what-is-observability) · [aliyun Well-Architected](https://help.aliyun.com/zh/well-architected/observability-design-principles) |
| tracing | SETTLED-CHINESE | 链路追踪; 分布式跟踪 for distributed tracing; 链路数据 / 调用链 for the object | strong | — | [aliyun ASM](https://help.aliyun.com/zh/asm/user-guide/enable-distributed-tracing-in-asm) · [aliyun what-is](https://help.aliyun.com/zh/what-is/what-is-observability) |
| technical debt | SETTLED-CHINESE | 技术债 (prose) / 技术债务 (formal) | strong | — | [Meituan tech](https://tech.meituan.com/2026/05/07/Agent-AI-Coding.html) · [vivo team](https://www.cnblogs.com/vivotech/p/18499182) |
| build artifact | SETTLED-CHINESE | 构建产物 (build output); 制品, 制品仓库 (stored, versioned) | strong | — | [aliyun Yunxiao quickstart](https://help.aliyun.com/zh/yunxiao/getting-started/web-side-quick-start) · [aliyun 制品仓库](https://help.aliyun.com/zh/yunxiao/user-guide/what-is-a-product-repository) |
| pull request | PLATFORM-BOUND | Pull Request kept in English (Gitee); 合并请求 (Huawei CodeArts Repo, GitLab-derived); 拉取请求 (GitHub zh) | moderate | conf. ↓ | [Huawei CodeArts](https://support.huaweicloud.com/usermanual-codeartsrepo/codeartsrepo_03_0072.html) · [Gitee help](https://help.gitee.com/base/pullrequest/comment) (unreachable at audit) · [GitLab jh](https://docs.gitlab.cn/jh/user/project/merge_requests/) |
| postmortem | SETTLED-CHINESE | 故障复盘 (复盘 alone once context is set) | moderate | conf. ↓ | [aliyun fault-recovery](https://help.aliyun.com/zh/well-architected/fault-recovery) · [aliyun 2573892](https://help.aliyun.com/zh/document_detail/2573892.html) |
| fallback | KEEP-ENGLISH | none single; 降级 = the degrade event, 兜底 = the prepared substitute, Fallback = the API | moderate | note added | [aliyun AHAS weak-dep](https://help.aliyun.com/zh/ahas/user-guide/degradation-based-on-weak-dependency) · [JavaGuide](https://javaguide.cn/high-availability/fallback-and-circuit-breaker.html) |
| breaking change | SETTLED-CHINESE | 破坏性变更 (also 不兼容变更 in Alibaba SDK register) | moderate | note added | [aliyun ES upgrade](https://help.aliyun.com/zh/es/user-guide/upgrade-the-version-of-a-cluster) · [aliyun SDK policy](https://help.aliyun.com/zh/sdk/product-overview/alibaba-cloud-sdk-support-policies) |
| feature flag | **CONTESTED** | 功能开关 vs 特性开关 / 『特性』开关 — both on the cited page | weak | **verdict changed** | [Gitee FeatureProbe](https://gitee.com/featureprobe/FeatureProbe) · [Tencent community](https://cloud.tencent.com/developer/article/2263930) |
| on-call | CONTESTED | 值班 (the duty), 排班 (the roster); On-Call / Oncall kept in English — split by register | weak | conf. ↓, form removed | [aliyun ARMS scheduling](https://help.aliyun.com/zh/arms/alarm-operation-center/create-scheduling-policies) · [aliyun OIC](https://help.aliyun.com/zh/oic/user-guide/what-is-scheduling-management) · [Flashcat](https://flashcat.cloud/blog/what-is-oncall/) (compromised) |
| boilerplate | SETTLED-CHINESE | 样板代码 | weak | conf. ↓ | [Tony Bai](https://tonybai.com/2026/02/08/go-boilerplate-code-vs-rust-data-refutes-stereotypes/) |
| flaky test | KEEP-ENGLISH | none; 不稳定的测试 is a descriptive gloss, not a term | weak | conf. ↓ | [TesterHome 34542](https://testerhome.com/topics/34542) · [TesterHome 34109](https://testerhome.com/articles/34109) |
| runbook | **NOT-FOUND** | — (do not coin) | none | — | see note |
| happy path | **NOT-FOUND** | — (do not coin) | none | — | see note |

### Notes on the contested and revised entries

**feature flag — the verdict that had to change.** The research called it SETTLED-CHINESE on
功能开关, citing "17 occurrences" on the FeatureProbe Gitee README. The audit counted **3**,
and found the competing root on the same page, written with brackets so a bare grep misses
it: `『特性』开关` ×2, `特性管理` ×3, `『特性』管理` ×1, `特性粒度` ×2, with the project's own
self-definition reading `FeatureProbe 是一个开源的 **『特性』管理** 服务`. One page showing two
roots is contestation, not settlement. A third form, 功能标志, appears in the material but only
on a page that turned out to be a translation of Martin Fowler, so it is **not** native evidence.
Practical shape: pick one form and be consistent inside a document; no claim about which is commoner survives.

**on-call — a Chinese form was struck.** The research answer read "值班 (with 排班 for the roster
and **轮值** for the rotation)". 轮值 occurs **zero times** on either cited source. It is the one
invented form in the source material and it is not in the table above. The Flashcat leg is also
compromised: the 快猫运营团队 byline is genuine, but the body says `原文提到 AWS、Google Cloud、阿里云…`
— it is summarising someone else's 原文 — and it carries the 核心摘要 / FAQ / 继续探索 shape of
SEO/LLM-assisted content. The CONTESTED verdict survives on the Alibaba leg alone (值班 and 排班
used exclusively; no English on-call term on the page), at weak confidence.

**runbook — NOT-FOUND, twice, independently.** The single substantial Chinese treatment
(`运行手册` ×44) is an explicit translation: `作者 Fatih K. 原文：https://fatihkoc.net/posts/sre-observability-slo-runbooks/`.
AWS's zh_cn docs supply 运行手册 / 执行手册 / 行动手册 and are likewise translations. Four
already-screened Chinese SRE pages contain those forms zero times. What native formal Chinese
reaches for instead is **预案** (53 occurrences in the CAICT stability guide) or SOP outright —
related, not equivalent. Keep the English, or write 预案 / 操作手册 with the English alongside.

**happy path — NOT-FOUND, and the trap named.** The only dedicated Chinese explainer uses
`Happy Path` 46 times and renders it in Chinese zero times; the later audit screened that page
out as a content-farm repost (`本文内容系天翼云实名用户自发贡献`, same title on three platforms),
so it is directional, not citable. The dictionary gloss 幸福之路 is a lexicographic artefact with
no currency in Chinese software writing — proposing it would be exactly the invented translation
this file exists to prevent.

**boilerplate — contested across runs.** The later run grounds 样板代码 on one screened native
source (the term is in the article's own title, audit-verified) and grades it weak — a single
derivative source, since the quoted sentence renders an English study's conclusion. An earlier
run reached **NOT-FOUND** for the same term after its audit disqualified both of its sources
(a guest-user Q&A excerpt and an undisclosed translation of an English newsletter). Treat 样板代码
as attested but thin.

**pull request / postmortem / breaking change / fallback — one-source caveats.** postmortem was
downgraded from strong (one page in that run; the cross-run Alibaba and CAICT sources restore it
to moderate). breaking change rests on one first-party attestation; a second Alibaba register
writes 不兼容的 API 变更 and keeps the English "Break Change", so do not rank 破坏性变更 against
不兼容变更. fallback's two citations are the same vendor and the same product (AHAS) — effectively
one attestation. pull request's Gitee leg was unreachable from the audit's network (connection
reset ×3, 503 via WebFetch); the Huawei leg was verified hard ("Pull Request" zero occurrences in
visible text while 合并请求 runs throughout). GitHub's zh page carries its own machine-translation
disclaimer, so 拉取请求 is listed as that platform's label, not as evidence of native usage.

## 2. Chinese-origin short forms: settled term or ad-hoc clipping?

Not loanwords — these are Chinese clippings, blends and coinages. The question is whether the
short form has independent currency or is only a clip licensed by a nearby long form.

| Form | Verdict | Conf. | Evidence |
| --- | --- | --- | --- |
| 联调 | Settled. 联合调试 is a **different** term (debugger / embedded 软硬件 sense), not its expansion | strong | [aliyun EDAS](https://help.aliyun.com/zh/edas/developer-reference/overview-of-application-testing-and-the-interconnection-between-on-premises-and-cloud-applications) · [CSDN 122845396](https://blog.csdn.net/QuietSnow_wuyaya/article/details/122845396) (联调 88 / 联合调试 0) · [counter-sense](https://www.cnblogs.com/lidabo/p/17076849.html) |
| 压测 | Settled; 压力测试 is also current, so it is settled by currency, not by the expansion sounding wrong | strong | [aliyun PTS](https://help.aliyun.com/zh/pts/product-overview/what-is-pts) (41/0) · [Huawei CodeArts PerfTest](https://support.huaweicloud.com/usermanualnew-cpts/cpts_02_0053.html) (8/0) · [Huawei consent string](https://support.huaweicloud.com/qs-cpts/cpts_qs_0003.html) |
| 灰度 | Settled at vendor level, two vendors. **Not** settled at standards level | strong | [aliyun SAE](https://help.aliyun.com/zh/sae/implementation-of-full-link-gray-based-on-java-service-gateway) (66/0) · [Huawei ASM](https://support.huaweicloud.com/usermanual-asm/asm_01_0036.html) (58/16, defines 灰度版本 out of bare 灰度) |
| 埋点 | Settled — and not an abbreviation; there is no long form | strong | [Meituan](https://tech.meituan.com/2017/03/02/mt-mobile-analytics-practice.html) · [Sensors Data manual](https://manual.sensorsdata.cn/sa/docs/visual_auto_track/v0203) |
| 扩缩容 | Settled — a coordinate blend of 扩容 + 缩容, not a clipping | strong | [aliyun ACK HPA](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/horizontal-pod-autoscaling) |
| 兜底 | Settled — an idiom turned term; used unglossed inside a 名词解释 glossary entry | moderate | [aliyun SAE](https://help.aliyun.com/zh/sae/implementation-of-full-link-gray-based-on-java-service-gateway) · [Tencent community](https://cloud.tencent.com/developer/article/1660973) |
| 打标 | Settled in the traffic-routing sense; one vendor only (打标 10 / 打标签 0) | moderate | [aliyun MSE](https://help.aliyun.com/zh/mse/user-guide/implementation-of-full-link-gray-scale-based-on-cloud-native-api-gateway) · aliyun SAE (above) |
| 提测 | Settled as a term (zero expansions, four sources, dense family) but **register-bound**: process writing, near-absent from product docs | moderate | [Meituan](https://tech.meituan.com/2018/05/11/quality-operation-in-zcm.html) · [JD Cloud](https://developer.jdcloud.com/article/3406) |
| 自测 | Same shape and same register caveat as 提测 | moderate | [Meituan Sonic](https://tech.meituan.com/2022/03/17/Java-HotSwap-Sonic.html) · [JD Cloud](https://developer.jdcloud.com/article/3406) |
| 全量 | Settled **as an attributive** (全量上线 / 数据 / SQL). The bare-predicate use (完成全量) is in-house blog register only | moderate | [Tencent Cloud docs](https://cloud.tencent.com/document/product/1364/78618) |
| 冒烟 | **Do not treat as settled.** 冒烟测试 is settled; every bare use sits inside a passage already headed 冒烟测试 | moderate | [JD Cloud](https://developer.jdcloud.com/article/3406) |
| 回归 | **Do not treat as settled.** Anaphoric clip (22 bare vs 20 full on the densest page), plus a live homonym hazard: 逻辑回归 | moderate | [cnblogs](https://www.cnblogs.com/imyalost/p/17767836.html) · [Huawei CodeArts](https://support.huaweicloud.com/bestpractice-testman/cloudtest_14_0005.html) |
| 放量 | Thin. Mostly bound to 灰度放量; no first-party doc found | weak | [Tencent community](https://cloud.tencent.com/developer/article/1749651) |
| 切量 | Thin — one running-prose occurrence in the whole corpus; the rest is sidebar and titles. Native writing more often says 切流 | weak | [CSDN 133191780](https://blog.csdn.net/qq_39839075/article/details/133191780) |
| 拉齐 | Thin — two occurrences total, locked to 拉齐 + 认知 / 信息 | weak | [Sensors Data](https://manual.sensorsdata.cn/sa/docs/ai_tracker/v0300) · [JD Cloud](https://developer.jdcloud.com/article/3406) |
| 复测 | Thin, **not** absent. A real named bug-lifecycle state; zero occurrences across ~40 other fetched pages | weak | [CSDN 162350419](https://blog.csdn.net/2402_87794035/article/details/162350419) |

**The discriminator that survived.** Two parts, both required: (1) can the short form appear on
*first mention*, as subject or head, in a text where the long form never appears at all? and
(2) does it head its own compound family (全链路压测 / 压测平台 / 压测报告)? Family membership
alone over-licenses — 冒烟 and 回归 both grow families yet fail part (1).

## 3. Borrowed metaphors

| Term | Verdict | Conf. | Evidence |
| --- | --- | --- | --- |
| 复盘 (retrospective / postmortem) | **Settled term, not a live metaphor.** Unglossed, in headings, capability names and document types; 围棋 appears zero times across all sources. 故障复盘 = postmortem; **迭代复盘会**, not 回顾会议, is the first-party Chinese for the agile retrospective | strong | [aliyun 2573892](https://help.aliyun.com/zh/document_detail/2573892.html) (复盘 13 / 故障复盘 7) · [aliyun Yunxiao 迭代复盘](https://help.aliyun.com/zh/yunxiao/use-cases/8-how-to-do-a-good-iterative-re-disk) (复盘 49 / 迭代复盘 24) · [CAICT guide (PDF)](https://13115299.s21i.faiusr.com/61/1/ABUIABA9GAAgp43RkgYokZSF9QE.pdf) |
| 代码坏味道 (code smell) | Settled **in the refactoring register**, absent from vendor code-inspection docs (0 occurrences on two Alibaba pages). Prefer the specific named smell (重复代码, 过长函数, 过长参数列表, 上帝类) in ordinary prose. 代码异味 is a **real minority form** — do not assert it is unused | moderate | [Refactoring 2e ch.3 zh](https://book-refactoring2.ifmicro.com/docs/ch3.html) · [Huawei community](https://bbs.huaweicloud.com/blogs/371691) · [Tencent community](https://cloud.tencent.com/developer/article/1835315) (坏味道 26) · [代码异味 attested](https://developer.aliyun.com/article/873025) |

## 4. 基线 and its neighbours

| Question | Answer | Conf. | Evidence |
| --- | --- | --- | --- |
| 安全基线 | Settled, and 基线 in security/ops Chinese has drifted toward "mandatory floor / red line", stronger than neutral English *baseline*. 安全基准 is **not** a thing | strong | [aliyun 云安全中心](https://help.aliyun.com/document_detail/479212.html) (defines 基线 as 配置红线) · [安全内参](https://www.secrss.com/articles/29021) · GB/T 35283-2017, YD/T 2698/2700/2701/2702-2014 |
| 性能基线 | Settled; shipped as UI strings (设为基线 / 基线设置) | strong | [aliyun PTS](https://help.aliyun.com/zh/pts/performance-test-pts-2-0/user-guide/set-a-performance-baseline) |
| 配置基线 | Settled — in Chinese national standard titles, stronger than the research claimed | strong | GB/T 35283-2017《信息安全技术 计算机终端核心配置基线结构规范》 |
| 基线测试 vs 基准测试 | 基准测试 is the standard word for benchmarking and dominates by roughly an order of magnitude. 基线测试 is marginal: it means either "the run that establishes the baseline" or a transparently calqued category arriving with *Baseline Testing* in parentheses | moderate | [cnblogs 9630843](https://www.cnblogs.com/imyalost/p/9630843.html) · [cnblogs 10642822](https://www.cnblogs.com/timePasser-leoli/p/10642822.html) · [native counterexample](https://blog.csdn.net/IT_LanTian/article/details/135460016) |
| 基线 vs 基准 | A tendency, not a rule: 基线 = the frozen snapshot you measure drift against; 基准 = the yardstick, and the fixed half of 基准测试. In project management they are simply two translations of one English word — a Chinese PM reference says so outright: 基线（PMBOK资料一般翻译成基准） | moderate | [信管网](https://m.cnitpm.com/pm/4484.html) (single-source concentration — four evidence slots) |
| 基线要求 | Only where a specific X基线 is already on the table (安全配置基线要求). For the bare English sense "minimum acceptable level", Chinese takes 基本要求 / 最低要求 | moderate | GB/T 47686-2026《网络安全技术 政务云安全配置基线要求》 vs GB/T 22239-2019《网络安全等级保护基本要求》, GB/T 45654-2025 |
| Clinical / epidemiological 基线 | Settled family: 基线调查 / 基线情况 / 基线描述 / 基线资料 / 基线特征 | moderate | [CKB cohort](http://ckbiobank.pku.edu.cn/xcgz/jxdc.htm) · [基线特征表](https://cloud.tencent.com/developer/article/1701944) (基线特征 ×28) · [基线资料](https://www.iikx.com/news/article/6168.html) |
| ML 基线 | 基线 / 基线性能 are live in Chinese ML writing. 基线模型 specifically could not be verified (Zhihu 403s reproducibly) | weak | [CSDN 150991520](https://blog.csdn.net/m0_74462934/article/details/150991520) (基线 ×57) |
| Bare 基线 in general Chinese | Defaults to the surveying / legal line (领海基线), not the engineering sense. 基线 wants a domain word bolted on; alone in prose it reads underspecified | moderate | [MFA statement](https://www.mfa.gov.cn/web/ziliao_674904/tytj_674911/tyfg_674913/200904/t20090409_9866755.shtml) |

## 5. Two patterns that generalize

**Clipping is register, not contestation.** Chinese technical vocabulary routinely clips a
compound's disyllabic tail, and both forms stay correct — 技术债务 → 技术债, 可观测性 → 可观测.
The split is predictable: the clipped form dominates running prose (Meituan: 技术债 23 times,
技术债务 zero) while the full form surfaces in definitional and formal positions. Seeing both
forms in a corpus is **not** evidence of contestation. Real contestation needs two different
roots (灰度发布 vs 金丝雀发布, 功能开关 vs 特性开关), not one root with and without its tail.

**Translation status is a property of the page, not of the domain.** One domain
(`flashcat.cloud`) served both an explicit translation carrying `原文：https://fatihkoc.net/...`
and in-house originals. Screening a site once and trusting its other pages is how a research run
ends up citing translations as native usage. Corollary: a parenthetical English gloss after a
Chinese term — 可观测（Observability）, 破坏性变更（Breaking changes）— is **not** a translation
marker. It is a native writer propping up a loan, and it is a positive signal that the Chinese
form is real but still consolidating. A stronger machine-readable marker exists on Alibaba pages:
`{"value":false,"key":"autoTranslation","desc":"非自动翻译"}`.

## 6. What the audits struck

Recorded so nobody re-derives them. None of these appears in the tables above.

- **轮值** as the Chinese for the on-call rotation — invented; zero occurrences on both cited sources.
- **幸福之路** for *happy path* — a bilingual-dictionary artefact with no currency in Chinese software writing.
- **运行手册 / 执行手册 / 行动手册** for *runbook* — attested only in translations of English source material.
- **脆弱测试** as *the* term for flaky test — one author's coinage, chosen in print because it 读着更顺一些.
- **工件** as a calque for *build artifact* — 制品 is the term.
- **功能开关 "17 occurrences"** — actually 3; the inflated count carried a SETTLED verdict that did not hold.
- **"灰度 is settled at standards level"** — the one standards citation has both tokens in a single clause where bare 灰度环境 sits beside 灰度发布环境; that is coordinate ellipsis, the exact structure used to disqualify 冒烟 and 回归.
- **"联合调试 does not circulate at all"** — false. It circulates in the debugger / embedded sense; it is a different term, which is a better reason for 联调's independence than absence would have been.
- **"复测 has 0 occurrences"** — true of a 40-page corpus, false as a claim about Chinese.
- **"代码异味 is unused"** — false; it is a live minority form.
- **"基线测试-as-a-category appears only on machine-translated pages"** — falsified by an ordinary native CSDN article.
- A Tencent **故障复盘** article framed as a first-party vendor disclosure — it is a community post under a personal byline.

## 7. Method and its limits

Sources were fetched with `curl`, screened page by page for translation markers (translator
credit, `原文` link, MT banner), and every quote string-matched against the saved bytes; the
independent audits re-fetched all cited URLs and re-counted. Quote discipline was clean in
three of the four audited runs — 45/45 exact on short forms, 26/26 on 基线, and 19/19 of the
reachable loanword citations. The fourth, on borrowed metaphors, scored 22/26: two quotes were
altered, one was truncated, and one was fabricated outright — a string attributed to an Alibaba
Cloud page that does not appear on it in any form. That run is the reason nothing from it
reached this document except the two findings its auditor re-grounded independently.

Known limits, all of which bound how far these notes can be pushed:

- **Term counts drift.** Several were raw-byte counts including nav, metadata and JSON-LD: On-Call 84 → 64, 值班 18 → 12, 技术债 26 → 23, 功能开关 17 → 3. Counts here are the audited, visible-text ones where the audit supplied them; treat any number as approximate and re-count before relying on it.
- **Corpus denominators are partly unauditable.** One run stated "40+ fetched pages" while citing 27 distinct URLs, and another's "~105 hits across ten pages" identifies only four of the ten. Negative findings resting on those denominators are weaker than they read.
- **Fetch gaps shape the evidence.** Zhihu returns 403 reliably; GitHub 403'd; Tencent Cloud's first-party docs and some Docusaurus sites serve a JS shell to `curl`; `help.gitee.com` was unreachable from the audit's network. CSDN returns 200 with a `Referer` header. Terms are grounded where pages were fetchable, which is not the same as where they are commonest.
- **No corpus instrument was available.** Everything here measures what pages print, not what Chinese engineers type.

*Compiled from three research-plus-audit runs. Where research and audit disagreed, the audit wins.*
