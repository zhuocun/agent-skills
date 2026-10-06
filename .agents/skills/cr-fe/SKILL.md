---
name: cr-fe
description: Comprehensive frontend code review focused on runtime safety (JS errors from null/undefined access, type coercion, unguarded boundary data), security and data integrity (XSS, dangerouslySetInnerHTML, javascript-URL and attribute injection, lost user input), error handling (try-catch, async/await, error boundaries), React hook dependencies and effect correctness (stale closures, cleanup, races), code smell, type honesty, and folder-structure layering. Use when reviewing or auditing frontend code or a frontend diff/PR (React, TypeScript, JavaScript, and other component frameworks), or when asked to check UI code for runtime errors, XSS or injection, hook bugs, code smell, or architecture. Reads source and reports findings. Not for checking how the running app renders, such as layout, theme, or visual regressions seen in screenshots (use visual-ux-sweep), and not for backend services, infrastructure, or non-UI logic.
---

# Frontend Code Review

Review frontend code so it cannot throw at runtime, recovers when something does, and stays legible as it grows. Report general logic bugs you find as well; the passes below add the failure modes specific to the browser: untyped data crossing boundaries, a render loop you do not control, and structure that hides both.

Priority order, highest first: **runtime safety → error handling → hook/effect correctness → type honesty → code smell → layering.** A crash outranks a smell; fix correctness before structure.

## When to use

**Primary target is React / TypeScript / JavaScript** — the idioms below are React-centric. Other component frameworks (Vue, Svelte, Solid) are in scope, but map the React specifics by analogy rather than expecting a literal match. Also reach for this on narrower asks: null-safety audits, leak hunts, and folder-structure or layering questions.

## The central instinct: trust nothing that crosses a boundary

Every production JS error traces to code treating a boundary value as if it were already the shape and type it hopes for. **Boundaries** are network responses, user input, route and query params, storage (`localStorage` / cookies), browser APIs (`window`, `navigator`), third-party SDKs, and props from a parent you do not own. Inside a boundary an honest type holds; at a boundary the declared type is a hope, not a fact.

So the method is: **find the boundaries, then verify every value is guarded, defaulted, or validated before it is accessed, transformed, or rendered.** Most of the review is tracing each boundary value to its first use.

## Review order

1. **Establish context** — framework, TS or JS, state and data layer, and the exact scope (diff or files). Read once before judging.
2. **Map data flow** — mark every boundary; trace each value to where it is read, transformed, and rendered. For a large diff, list the boundaries explicitly before Pass 1 so none is missed.
3. **Pass 1 — runtime safety** — every boundary access, every transformation.
4. **Pass 2 — error handling** — what can throw, and what happens when it does.
5. **Pass 3 — hooks & effects** — dependencies, cleanup, races, effects that should not exist.
6. **Pass 4 — type honesty** — `any` / `as` / `!` standing in for real validation.
7. **Pass 5 — code smell & layering** — structure, duplication, the smells below.
8. **Triage and report** — by severity, with `file:line` and a concrete failure path.

Ground every finding in a real path: state *which input* makes the line throw. "Could be null" is weak; "the `/users` response marks `address` optional, so line 42's `address.city` throws for users without one" is a finding.

## Runtime safety

The heart of the review: no path reaches an access or transformation on a value that might not be the assumed shape.

### Guarding access (`?.` and `??`)

`?.` answers "if null, evaluate to undefined" — correct only when undefined is acceptable *and handled downstream*. Three failures:

- **Deferred crash** — `items?.map(...)` returns `undefined`; the parent's `.length` then throws. `?.` moved the crash, it did not remove it. Pair with a real fallback: `(items ?? []).map(...)`.
- **Masked invariant** — if `user` cannot legitimately be null here, `user?.name` silently renders nothing and hides the real bug. Use the value directly; fix the type or validate at the boundary.
- **Over-chaining** — `a?.b?.c?.d` signals the shape was never modeled. Validate once at the boundary, then use a solid type.

Rule: `?.` + `??` at the boundary is good; deep `?.` in business logic is usually a modeling failure.

### Type transformation (coercion)

Where "looks fine, throws later" lives:

- `||` for defaults eats valid `0`, `""`, `false` → use `??` when those are valid values.
- `Number(x)` and `parseInt(x)` both yield `NaN`, which poisons math and comparisons, but differ: `Number(x)` is strict (`'12px'` → `NaN`), while `parseInt(x[, radix])` is lenient (`'12px'` → `12`) and needs an explicit radix → pick deliberately, then validate with `Number.isFinite`. `NaN === NaN` is `false`, so test with `Number.isNaN`, never `=== NaN`. `Number('')`, `Number('  ')` and `Number(null)` are `0`, not `NaN`, so a cleared field passes `Number.isFinite` as `0` → reject null and blank input explicitly (`s == null || s.trim() === ''`) before converting.
- `JSON.parse` throws on bad input → wrap it with a typed fallback (see Error handling).
- Template literals and `String()` turn `null` / `undefined` into the literal strings `"null"` / `"undefined"` shown to users → guard first.
- `new Date(x)` can be `Invalid Date` → check before formatting.
- `[]` and `{}` are truthy → test `.length` or keys, not the value itself.
- Use `===`, except the deliberate `== null` that catches null and undefined together.

### Common throw sites

Array methods on possibly-non-arrays; destructuring `null`/`undefined` (`const { a } = obj` → `const { a } = obj ?? {}`; a parameter default `= {}` covers only `undefined`, not the `null` JSON returns); index access assumed present; storage reads (`JSON.parse(localStorage.getItem(...))` — both the read and the parse can fail); `e.target` shape assumptions; index-as-`key` in lists that reorder, insert, or delete (not append-only) → React reuses the wrong instance: stale input values, wrong state, not necessarily a crash. A controlled `value={x}` where `x` may be `undefined`/`null` flips the input uncontrolled→controlled (React warns; cursor/state can reset) → default `value={x ?? ''}`.

### Injection & data integrity

These are Blockers:

- **`dangerouslySetInnerHTML` / `innerHTML`** with unsanitized boundary input is the XSS vector → sanitize (e.g. DOMPurify) or avoid; never feed it raw network, input, or URL data.
- **URL / attribute injection** — a user-controlled value flowing into `href`, `src`, or `window.location` can be a `javascript:` or `data:` URL that executes → validate the scheme (allow `http(s)` / `mailto`). `target="_blank"` should carry `rel="noopener"` for older engines (modern browsers imply it).
- **Data loss** — name the concrete cases: an uncontrolled→controlled input reset wiping what the user typed, direct state mutation dropping edits, and navigation away from unsaved state.

## Error handling

`try-catch` is for operations that *throw*, not a blanket wrap.

- **Wrap what throws**: `JSON.parse`, network and `await fetch`, storage (can throw on quota or in private mode), dynamic `import()`, third-party SDK calls, any parse of untrusted input.
- **Never swallow.** An empty `catch {}` turns a crash into silent wrong behavior, which is worse. Every catch must do one thing: recover with a real fallback, surface to the user (error state or toast), or rethrow / log *with context*.
- **Async correctness.** A missing `await` means try-catch catches nothing — `try { doAsync() }` without `await` is a no-op guard. Promise chains need `.catch`. `Promise.all` rejects on the first failure (the sibling promises still run, since `Promise.all` doesn't cancel them, so their side effects still happen; their later rejections are absorbed silently); use `allSettled` when partial success is acceptable.
- **Limits of catching.** Error Boundaries catch render and lifecycle throws but **not** event handlers, async code, or the legacy synchronous `renderToString` — those need their own handling. With streaming SSR (`renderToPipeableStream`), a server throw inside `<Suspense>` emits that boundary's fallback, fires `onError`, and retries on the client; an error boundary catches it only if the client render also throws. A try-catch in a component catches only that component's own synchronous code, never its children's render.

## Hooks & effects

React-first; the principles map to Vue `watch` / `computed`, Svelte runes / `$:`, and Solid `createEffect`. Manual dependency arrays are React-specific, but missed dependencies are not: Vue `watch` tracks only its declared source, never reads inside the callback; `watchEffect`, Svelte `$effect`, and Solid `createEffect` track only synchronous reads, so anything read after an `await` or inside a timer is untracked; Svelte's legacy `$:` statements track only variables referenced directly in the statement. What transfers unchanged is cleanup discipline and "derive, don't effect."

### Dependency arrays

The array says "re-run when these change," so it must list every reactive value (props, state, context, anything derived from them) read inside. Two failure directions:

- **Under-declared → stale closure.** The callback captures the first render's values forever. Symptom: "it shows the old value." `react-hooks/exhaustive-deps` catches most; a disabled-lint comment is a flag to inspect, not to trust.
- **Unstable / over-declared → over-firing or infinite loop.** An object, array, or function literal has a new identity each render, so the effect runs every render; if it then sets state, that is an infinite loop. Fix by memoizing the dependency, moving it inside the effect, depending on a primitive, or using a functional update `setX(x => …)` to drop the dep.

### Effects

- **Cleanup is mandatory** for anything that outlives the render: timers and intervals, subscriptions, event listeners, observers, `AbortController`, sockets. Missing cleanup → leaked timers/listeners/subscriptions, state updates landing after unmount (a wasted render or race; React 18 dropped the old "setState on unmounted" warning), and duplicate subscriptions under StrictMode's dev double-invoke.
- **Races** in fetch effects: fast-changing deps let responses resolve out of order → capture an `ignore` flag flipped in cleanup, or abort the request.
- **The effect callback must not be `async`** — an `async` callback returns a promise, not a cleanup function → define an async function inside and call it.
- **You might not need the effect.** Syncing state from props, transforming data for render, or reacting to a user event are not effects — compute during render (or `useMemo`), or do the work in the handler. An effect whose only job is `setState` from other state is almost always wrong: an extra render plus loop risk. For the genuine "reset state when a prop changes" case, prefer a `key` to remount or the previous-prop-compare set-during-render pattern, not an effect.
- **`ref.current` during render** — don't read it to compute JSX or write it during render; refs are escape-hatch mutable values for effects and handlers, and mutating during render breaks purity and concurrent features.
- **React 18 / 19**: `use(promise)` or a thrown promise needs an enclosing `<Suspense>` plus an error boundary for the reject path; Server Components can't call hooks or hold state.
- **Rules of hooks**: call hooks at the top level, never inside conditions, loops, or nested functions, and never after a conditional early return; custom hooks start with `use`. `use(promise | context)` is not a hook and may be called conditionally.
- **`useMemo` / `useCallback`** earn their place only when the computation is genuinely expensive, or the identity is itself a dependency of another hook or a memoized child. Memoizing everything is a smell, and wrong deps make it silently stale.

## Type honesty

`any`, `as`, and `!` are the three ways TS lies, and each re-opens the JS errors the rest of this review hunts:

- `any` disables checking → prefer `unknown`, then narrow.
- `as SomeType` on a boundary value asserts a runtime shape the compiler never verified → validate instead (schema or type guard), and the type is then earned.
- `!` (non-null assertion) hides exactly the null `?.` would have caught → prove non-null or handle it.

Types vanish at runtime, so validate external data *at the boundary*, not by asserting downstream.

## Code smell

Highest-signal, frontend-specific:

- **God component** — fetching + transforming + presenting + many `useState`. Split into a hook (logic, state, effects) and a presentational component (props in, events out). This split also surfaces the boundaries for Pass 1.
- **Duplication** — repeated logic across components → extract a hook or util.
- **Unstable context value** — `<Ctx.Provider value={{...}}>` with an inline object re-renders every consumer each render → memoize the value (and split contexts by update frequency).
- **Prop drilling** past ~3 levels → context or composition.
- **Flag soup** — `isLoading` / `isError` / `isEmpty` as separate booleans that can contradict → one discriminated union (`status: 'idle' | 'loading' | 'error' | 'success'`).
- **Magic values** → named constants.
- **Pyramid JSX, nested ternaries, inline IIFE** → early returns, guard clauses, extracted components.
- **Direct state mutation** → copy, then set.
- Dead code, stray `console.log`, commented-out blocks.

## Folder structure & layering

Judge layering against the repo's existing or documented convention first; use the template below only when there is none or the user asks about structure. On a diff review, flag only structure the diff introduces or worsens.

Organize so code is findable by feature and by role, and so dependencies flow one direction. Avoid the flat `components/` holding 80 unrelated files — and avoid the opposite, a folder per file.

Feature-first layout:

```
src/
  app/                 routing, providers, layout, entry
  features/<feature>/
    components/         presentational (UI; props in, events out; no fetching)
    hooks/             feature logic, state, effects
    api/               data access for this feature
    model/             domain types, schemas
    index.ts           public surface
  shared/
    ui/                design-system primitives
    hooks/  lib/  api/  reused across features
```

Rules:

- **Co-locate by feature**; promote to `shared` only when two or more features use it.
- **One-way dependencies**: `app → features → shared`. Features import one another only through the public `index.ts`, never internals; `shared` never imports a feature.
- **Separate presentational from container/logic.** This is the layering that keeps the runtime-safety review tractable — boundaries land in `api` and `hooks`, not buried in JSX.
- **One responsibility per file**; a file past ~200–300 lines (or the repo's own threshold), or exporting many unrelated things, wants splitting.
- **Add a layer only when it groups roughly three or more related files or separates a real concern** — over-nesting costs as much as flattening.

## Severity & triage

| Severity | Meaning | Examples |
|---|---|---|
| **Blocker** | Throws at runtime, loses data, loops infinitely, or is a security hole | Unguarded boundary access on a live path; render loop; `dangerouslySetInnerHTML` or a `javascript:` href with unsanitized input |
| **Major** | Latent error on a plausible path, a leak, or wrong behavior | Stale closure; missing cleanup; swallowed catch; `||` eating `0`; `as` on unvalidated data |
| **Minor** | Quality that will bite later | Over-`?.`; flag soup; god component; flat structure |
| **Nit** | Style or preference | Naming, ordering, formatting |

Lead with Blockers and Majors. Do not drown a real crash under nits.

## How to report

- One finding per issue, led by its severity: **`[Severity] file:line`**, then what throws or fails and the input or render that triggers it, each as a full sentence, then the fix.
- Show the fix as a minimal diff or exact replacement, not a paraphrase.
- Separate "will throw" from "could throw" from "smell" — calibrated severity is what makes the review trustworthy. Invent no issues; if unsure a path is reachable, say so and mark confidence.
- If the diff is clean on an axis, say so in a line rather than padding.

## Self-check

- [ ] Every boundary value (network, input, params, storage, browser, SDK, untrusted prop) is guarded, defaulted, or validated before access, transform, or render.
- [ ] `?.` is paired with a real fallback at boundaries, not deferring a crash or masking an invariant; no decorative deep chains.
- [ ] Coercion is safe: `??` not `||` where `0` / `""` / `false` are valid; `NaN` and `Invalid Date` checked; blank string → `0` handled before `Number`; `parseInt` has a radix; `JSON.parse` is wrapped.
- [ ] List keys are stable ids, not indexes, where items reorder, insert, or delete.
- [ ] No injection: `dangerouslySetInnerHTML` / `innerHTML` is sanitized, `href` / `src` / `window.location` schemes are validated; and no path silently loses user input (uncontrolled→controlled reset, direct mutation, unsaved-state navigation).
- [ ] No `any` / `as` / `!` standing in for real validation at a boundary.
- [ ] try-catch covers what throws and no catch is swallowed; `await` is present where rejections must be caught; `all` vs `allSettled` is correct.
- [ ] Hook deps are exhaustive and stable; effects clean up; fetch effects handle races; no effect that should be a handler or a render-time computation; rules of hooks hold; no `async` effect callback; no `ref.current` read or write during render; `use`/suspending code has `<Suspense>` plus an error boundary.
- [ ] No god components, duplication, prop drilling, flag soup, magic values, or direct mutation.
- [ ] Structure the diff touches follows the repo's layering convention (or the template if none), with one-way deps and a presentational/logic split — neither flattened nor over-nested.
- [ ] Findings cite `file:line` with a concrete failure path, calibrated severity, and a precise fix.
