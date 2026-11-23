#!/usr/bin/env python3
"""Validate the skill files this repository ships.

Every rule enforced here is stated in AGENTS.md ("Skill authoring conventions"
and "What ships from this repo"). Rules that AGENTS.md describes only loosely
(a dense description, a one-paragraph role statement, a priority order,
numbered passes) are deliberately not enforced.

Usage:
    python3 scripts/validate_skills.py [--root PATH]

Exit codes:
    0  every check passed
    1  at least one check failed
    2  the validator could not run (bad root, missing dependency)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - environment problem, not a repo defect
    yaml = None  # type: ignore[assignment]

try:
    from .sync_output_styles import (
        ATX_HEADING,
        compile_baseline_body,
        extract_reload_sentinel,
        first_diff_line,
        iter_lines_outside_code_fences,
    )
except ImportError:
    _scripts_dir = str(Path(__file__).resolve().parent)
    if _scripts_dir not in sys.path:
        sys.path.insert(0, _scripts_dir)
    from sync_output_styles import (
        ATX_HEADING,
        compile_baseline_body,
        extract_reload_sentinel,
        first_diff_line,
        iter_lines_outside_code_fences,
    )

SKILLS_DIR = Path(".agents/skills")
SYMLINK = Path(".claude/skills")
SETTINGS_PATH = Path(".claude/settings.json")
OUTPUT_STYLE_MIRRORS = (
    (Path(".claude/output-styles/baseline.md"), Path(".agents/skills/communicate")),
)
REQUIRED_KEYS = ("name", "description")
MAX_DESCRIPTION_LENGTH = 1024
MAX_NAME_LENGTH = 64
NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
MAX_COMPATIBILITY_LENGTH = 500
MAX_SKILL_MD_LINES = 500
REFERENCE_TOC_THRESHOLD = 100
FENCE = "---"
CODE_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+).+?\1")
CODE_SPAN = re.compile(r"`(references/[^`\s]+)`")
REFERENCES_PATH = re.compile(r"(?<![A-Za-z0-9])references/[^\s`)\]>\"'*_]*")
SKILL_MD_MENTION = re.compile(r"(?<![A-Za-z0-9])SKILL\.md(?![A-Za-z0-9])")
HTTP_URL = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^\s<>)\"']+")
BLOCKQUOTE = re.compile(r"^ {0,3}>")
LINK_TARGET = re.compile(r"\]\(\s*(?:<([^>\n]*)>|([^)\s]+))")
LINK_DEFINITION = re.compile(r"^ {0,3}\[(?!\^)[^\]]+\]:\s*(?:<([^>\n]*)>|(\S+))", re.MULTILINE)
INLINE_LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
URL_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")

CHECKS = (
    ("skill-md-present", "every skill directory contains a SKILL.md"),
    ("skill-md-lines", f"SKILL.md has at most {MAX_SKILL_MD_LINES} lines"),
    ("frontmatter-parses", "SKILL.md opens with a --- block that parses as a YAML mapping"),
    ("required-keys", "frontmatter has non-empty `name` and `description`"),
    ("description-length", f"frontmatter `description` is at most {MAX_DESCRIPTION_LENGTH} characters"),
    ("description-angle-brackets", "frontmatter `description` contains no `<` or `>`"),
    ("name-matches-directory", "frontmatter `name` equals the skill's directory name"),
    ("name-format", f"frontmatter `name` is 1-{MAX_NAME_LENGTH} lowercase ASCII letters, digits and single hyphens, not starting or ending with a hyphen"),
    ("compatibility-length", f"frontmatter `compatibility`, if present, is 1-{MAX_COMPATIBILITY_LENGTH} characters"),
    ("h1-title", "the body opens with an `# ` H1 title"),
    ("self-check-section", "the body's last `## ` heading outside fenced code is `## Self-check`"),
    ("relative-links-resolve", "every relative Markdown link, inline or reference-style, in a skill's .md files resolves to an existing file (anchors are not checked)"),
    ("references-linked", "every file under a skill's references/ is linked, or named by its `references/` path in inline code, directly from its SKILL.md"),
    ("reference-toc", f"a reference .md file over {REFERENCE_TOC_THRESHOLD} lines lists a link to each `## ` heading's anchor before its first `## ` heading outside fenced code"),
    ("claude-skills-symlink", ".claude/skills is a symlink resolving to .agents/skills"),
    ("output-style-mirror", "each output style satisfies its frontmatter and self-containment contract, its body equals the compiled skill output, and the skill's reload sentinel matches its last Self-check item"),
)
REPO_CHECKS = {"claude-skills-symlink", "output-style-mirror"}
FILE_CHECKS = {"relative-links-resolve", "references-linked", "reference-toc"}


@dataclass(frozen=True)
class Failure:
    check: str
    where: str
    detail: str


@dataclass(frozen=True)
class Skipped:
    check: str
    where: str
    reason: str


Result = tuple[list[Failure], list[Skipped]]


def skip_rest(after: str, where: str, reason: str) -> list[Skipped]:
    """Checks that cannot be evaluated once an earlier check failed for this file."""
    names = [name for name, _ in CHECKS if name not in REPO_CHECKS | FILE_CHECKS]
    return [Skipped(name, where, reason) for name in names[names.index(after) + 1 :]]


def split_frontmatter(text: str) -> tuple[str, list[str]]:
    """Return (frontmatter_text, body_lines). Raises ValueError if absent/unterminated."""
    lines = text.split("\n")
    if not lines or lines[0].rstrip() != FENCE:
        raise ValueError("file does not start with a `---` frontmatter delimiter")
    for index in range(1, len(lines)):
        if lines[index].rstrip() == FENCE:
            return "\n".join(lines[1:index]), lines[index + 1 :]
    raise ValueError("frontmatter opened with `---` but is never closed by a second `---`")


def outside_code_fences(lines: list[str]) -> Iterator[str]:
    """Yield the lines that are not inside a fenced code block (``` or ~~~)."""
    for _, line in iter_lines_outside_code_fences(lines):
        yield line


def inline_link_targets(text: str) -> list[str]:
    """Return the targets of inline Markdown links in text, including `<...>` targets with spaces."""
    return [angled or bare for angled, bare in LINK_TARGET.findall(text)]


def _strip_inline_code_in_paragraph(paragraph: str) -> str:
    """Replace CommonMark inline code spans (including multiline spans) with spaces, preserving positions."""
    out: list[str] = []
    i = 0
    n = len(paragraph)
    while i < n:
        if paragraph[i] == "`":
            j = i
            while j < n and paragraph[j] == "`":
                j += 1
            ticks = j - i
            k = j
            closed = False
            while k < n:
                if paragraph[k] == "`":
                    m = k
                    while m < n and paragraph[m] == "`":
                        m += 1
                    if m - k == ticks:
                        out.append("".join("\n" if ch == "\n" else " " for ch in paragraph[i:m]))
                        i = m
                        closed = True
                        break
                    k = m
                else:
                    k += 1
            if not closed:
                out.append(paragraph[i:j])
                i = j
        else:
            out.append(paragraph[i])
            i += 1
    return "".join(out)


def _strip_inline_code_outside_fences(lines: list[str]) -> str:
    """Join lines outside fenced code blocks with inline code spans masked within block boundaries."""
    blocks: list[str] = []
    current: list[str] = []
    prev_index = -2

    def flush() -> None:
        if current:
            blocks.append(_strip_inline_code_in_paragraph("\n".join(current)))
            current.clear()

    for index, line in iter_lines_outside_code_fences(lines):
        if index != prev_index + 1:
            flush()
        prev_index = index

        if not line.strip():
            flush()
        elif ATX_HEADING.match(line):
            flush()
            blocks.append(_strip_inline_code_in_paragraph(line))
        elif LIST_ITEM.match(line) or BLOCKQUOTE.match(line):
            flush()
            current.append(line)
        else:
            current.append(line)

    flush()
    return "\n\n".join(blocks)


def link_targets(lines: list[str]) -> list[str]:
    """Return inline and reference-style link targets outside fenced code and inline code spans."""
    text = _strip_inline_code_outside_fences(lines)
    definitions = [angled or bare for angled, bare in LINK_DEFINITION.findall(text)]
    return inline_link_targets(text) + definitions


def local_path(target: str) -> str | None:
    """Return the path part of a relative link target, or None for anchors, URLs and absolute paths."""
    if target.startswith(("#", "/")) or URL_SCHEME.match(target):
        return None
    path = unquote(target.split("#", 1)[0].split("?", 1)[0])
    return path or None


def heading_anchor(text: str) -> str:
    """The anchor GitHub generates for a heading: lowercase, punctuation removed, spaces as hyphens."""
    text = INLINE_LINK.sub(r"\1", text)
    return re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")


def h2_anchors(lines: list[str]) -> list[tuple[str, str]]:
    """Return (heading text, anchor) for each `## ` heading, with GitHub's -1, -2 suffixes for repeats."""
    seen: dict[str, int] = {}
    anchors: list[tuple[str, str]] = []
    for line in outside_code_fences(lines):
        match = HEADING.match(line)
        if not match:
            continue
        base = heading_anchor(match.group(2))
        count = seen.get(base, 0)
        seen[base] = count + 1
        if len(match.group(1)) == 2:
            anchors.append((match.group(2), f"{base}-{count}" if count else base))
    return anchors


def check_skill_files(directory: Path, root: Path) -> Result:
    """Checks on the links and reference files of one skill directory."""
    failures: list[Failure] = []
    skipped: list[Skipped] = []
    skill_md = directory / "SKILL.md"

    for path in sorted(directory.rglob("*.md")):
        try:
            lines = path.read_text(encoding="utf-8").split("\n")
        except (UnicodeDecodeError, OSError) as exc:
            failures.append(Failure("relative-links-resolve", str(path.relative_to(root)), f"could not read file as UTF-8: {exc}"))
            continue
        for target in link_targets(lines):
            local = local_path(target)
            if local is not None and not (path.parent / local).exists():
                failures.append(Failure("relative-links-resolve", str(path.relative_to(root)), f"link `{target}` points at `{local}`, which does not exist relative to this file; fix the path or create the file"))

    references = sorted(p for p in (directory / "references").rglob("*") if p.is_file()) if (directory / "references").is_dir() else []
    if not skill_md.is_file():
        skipped.append(Skipped("references-linked", str(directory.relative_to(root)), "no SKILL.md to link from"))
    elif references:
        try:
            skill_lines = skill_md.read_text(encoding="utf-8").split("\n")
        except (UnicodeDecodeError, OSError) as exc:
            failures.append(Failure("references-linked", str(skill_md.relative_to(root)), f"could not read file as UTF-8: {exc}"))
        else:
            named = [local_path(target) for target in link_targets(skill_lines)]
            named += [code for line in outside_code_fences(skill_lines) for code in CODE_SPAN.findall(line)]
            linked = {(skill_md.parent / local).resolve() for local in named if local}
            for reference in references:
                if reference.resolve() not in linked:
                    failures.append(Failure("references-linked", str(reference.relative_to(root)), f"is not linked from `{skill_md.relative_to(root)}`; link it, or name its `references/` path in inline code, directly in SKILL.md and say when to read it in full and to read it again after a compaction"))

    for reference in references:
        if reference.suffix != ".md":
            continue
        try:
            lines = reference.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError) as exc:
            failures.append(Failure("reference-toc", str(reference.relative_to(root)), f"could not read file as UTF-8: {exc}"))
            continue
        if len(lines) <= REFERENCE_TOC_THRESHOLD:
            continue
        headings = h2_anchors(lines)
        preamble: list[str] = []
        for line in outside_code_fences(lines):
            if line.startswith("## "):
                break
            preamble.append(line)
        listed = {
            target[1:]
            for line in preamble
            if LIST_ITEM.match(line)
            for target in inline_link_targets(line)
            if target.startswith("#")
        }
        missing = [f"`{text}` (#{anchor})" for text, anchor in headings if anchor not in listed]
        if missing:
            failures.append(Failure("reference-toc", str(reference.relative_to(root)), f"has {len(lines)} lines but its table of contents before the first `## ` heading does not link {', '.join(missing)}; add a list item linking each `## ` heading's anchor"))

    return failures, skipped


def check_symlink(root: Path) -> list[Failure]:
    link = root / SYMLINK
    where = str(SYMLINK)
    if not link.is_symlink():
        if not link.exists():
            return [Failure("claude-skills-symlink", where, "does not exist; expected a symlink to .agents/skills")]
        return [Failure("claude-skills-symlink", where, f"exists but is a regular {'directory' if link.is_dir() else 'file'}, not a symlink to .agents/skills")]

    target = link.readlink()
    resolved = (link.parent / target).resolve() if not target.is_absolute() else target.resolve()
    expected = (root / SKILLS_DIR).resolve()

    if not resolved.exists():
        return [Failure("claude-skills-symlink", where, f"is a broken symlink: target `{target}` resolves to `{resolved}`, which does not exist")]
    if resolved != expected:
        return [Failure("claude-skills-symlink", where, f"points at `{resolved}` but must point at `{expected}` (link target is `{target}`)")]
    if not resolved.is_dir():
        return [Failure("claude-skills-symlink", where, f"resolves to `{resolved}`, which is not a directory")]
    return []


def mirrored_body(path: Path) -> str:
    """Return the text below the frontmatter and the opening H1, minus the one blank line after the H1.

    Everything else, trailing blank lines included, is compared exactly. Raises ValueError if the
    frontmatter or the H1 is absent.
    """
    _, body = split_frontmatter(path.read_text(encoding="utf-8"))
    index = next((i for i, line in enumerate(body) if line.strip()), None)
    if index is None or not body[index].startswith("# "):
        raise ValueError("body does not open with an `# ` H1 title")
    rest = body[index + 1 :]
    if rest and not rest[0].strip():
        rest = rest[1:]
    return "\n".join(rest)


def parse_frontmatter_yaml(frontmatter_text: str) -> object:
    """Parse YAML frontmatter with PyYAML (the sole production parser)."""
    if yaml is None:
        raise RuntimeError("PyYAML is required to parse YAML frontmatter")
    try:
        return yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        raise ValueError(f"frontmatter is not valid YAML: {' '.join(str(exc).split())}") from None


def _iter_yaml_strings(value: object) -> Iterator[str]:
    """Yield every decoded string value recursively inside a parsed YAML object."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _iter_yaml_strings(k)
            yield from _iter_yaml_strings(v)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_yaml_strings(item)


def _check_style_self_containment(lines: list[str], where: str) -> list[Failure]:
    """Enforce that an output style has no relative links, `references/` paths, or `SKILL.md` mentions."""
    failures: list[Failure] = []
    for target in link_targets(lines):
        local = local_path(target)
        if local is not None:
            failures.append(
                Failure(
                    "output-style-mirror",
                    where,
                    f"contains relative link `{target}` (resolves to `{local}`); output styles must be self-contained",
                )
            )

    for line in outside_code_fences(lines):
        for code in CODE_SPAN.findall(line):
            failures.append(
                Failure(
                    "output-style-mirror",
                    where,
                    f"contains `{code}` outside fenced code; output styles must be self-contained with no `references/` paths",
                )
            )
        without_spans = CODE_SPAN.sub(" ", HTTP_URL.sub(" ", line))
        for ref_path in REFERENCES_PATH.findall(without_spans):
            failures.append(
                Failure(
                    "output-style-mirror",
                    where,
                    f"contains `{ref_path}` outside fenced code; output styles must be self-contained with no `references/` paths",
                )
            )
        if SKILL_MD_MENTION.search(line):
            failures.append(
                Failure(
                    "output-style-mirror",
                    where,
                    "mentions `SKILL.md` outside fenced code; output styles must be self-contained",
                )
            )
    return failures


def _read_text_for_check(path: Path, where: str, failures: list[Failure]) -> str | None:
    """Read UTF-8 text from `path`, appending an `output-style-mirror` failure on decode/OS error."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        failures.append(
            Failure("output-style-mirror", where, f"could not decode file as UTF-8: {exc}")
        )
        return None
    except OSError as exc:
        failures.append(
            Failure("output-style-mirror", where, f"could not read file: {exc}")
        )
        return None


def check_output_style_mirrors(root: Path) -> list[Failure]:
    failures: list[Failure] = []
    settings_output_style: str | None = None
    settings_path = root / SETTINGS_PATH
    try:
        settings_exists = settings_path.is_file()
    except OSError as exc:
        failures.append(Failure("output-style-mirror", str(SETTINGS_PATH), f"could not inspect file: {exc}"))
        settings_exists = False
    if settings_exists:
        settings_text = _read_text_for_check(settings_path, str(SETTINGS_PATH), failures)
        if settings_text is not None:
            try:
                settings_data = json.loads(settings_text)
            except json.JSONDecodeError as exc:
                failures.append(
                    Failure("output-style-mirror", str(SETTINGS_PATH), f"is not valid JSON: {exc}")
                )
            else:
                if not isinstance(settings_data, dict):
                    failures.append(
                        Failure(
                            "output-style-mirror",
                            str(SETTINGS_PATH),
                            f"must be a JSON object, but parsed as {type(settings_data).__name__}",
                        )
                    )
                elif "outputStyle" in settings_data:
                    raw_style = settings_data["outputStyle"]
                    if not isinstance(raw_style, str) or not raw_style.strip() or raw_style != raw_style.strip():
                        failures.append(
                            Failure(
                                "output-style-mirror",
                                str(SETTINGS_PATH),
                                f"`outputStyle` must be a non-empty string with no leading or trailing whitespace, but is {raw_style!r} ({type(raw_style).__name__})",
                            )
                        )
                    else:
                        settings_output_style = raw_style

    for style, skill in OUTPUT_STYLE_MIRRORS:
        where = str(style)
        skill_dir = skill.parent if skill.name == "SKILL.md" else skill
        skill_md = skill_dir / "SKILL.md"
        style_path = root / style
        skill_md_path = root / skill_md

        style_mirrored: str | None = None
        try:
            style_exists = style_path.is_file()
        except OSError as exc:
            failures.append(Failure("output-style-mirror", where, f"could not inspect file: {exc}"))
            style_exists = False
        if not style_exists:
            if not any(f.where == where and "could not inspect" in f.detail for f in failures):
                failures.append(
                    Failure(
                        "output-style-mirror",
                        where,
                        "does not exist; the output style and its skill ship as a compiled pair",
                    )
                )
        else:
            style_text = _read_text_for_check(style_path, where, failures)
            if style_text is not None:
                try:
                    fm_text, style_body = split_frontmatter(style_text)
                except ValueError as exc:
                    failures.append(Failure("output-style-mirror", where, str(exc)))
                    failures.extend(_check_style_self_containment(style_text.split("\n"), where))
                else:
                    name_value: str | None = None
                    parsed_fm_data: object = None
                    try:
                        data = parse_frontmatter_yaml(fm_text)
                    except ValueError as exc:
                        failures.append(Failure("output-style-mirror", where, str(exc)))
                    else:
                        parsed_fm_data = data
                        if not isinstance(data, dict):
                            kind = "empty" if data is None else f"a {type(data).__name__}"
                            failures.append(
                                Failure(
                                    "output-style-mirror",
                                    where,
                                    f"frontmatter must be a YAML mapping of keys to values, but parsed as {kind}",
                                )
                            )
                        else:
                            raw_name = data.get("name")
                            if not isinstance(raw_name, str) or not raw_name.strip():
                                failures.append(
                                    Failure(
                                        "output-style-mirror",
                                        where,
                                        "frontmatter `name` must be a non-empty string",
                                    )
                                )
                            else:
                                if raw_name != raw_name.strip():
                                    failures.append(
                                        Failure(
                                            "output-style-mirror",
                                            where,
                                            f"frontmatter `name` must not have leading or trailing whitespace: {raw_name!r}",
                                        )
                                    )
                                name_value = raw_name
                                if settings_output_style is not None and raw_name != settings_output_style:
                                    failures.append(
                                        Failure(
                                            "output-style-mirror",
                                            where,
                                            f"frontmatter `name` is {raw_name!r}, which does not match `{SETTINGS_PATH}` `outputStyle` ({settings_output_style!r})",
                                        )
                                    )

                            raw_desc = data.get("description")
                            if not isinstance(raw_desc, str) or not raw_desc.strip():
                                failures.append(
                                    Failure(
                                        "output-style-mirror",
                                        where,
                                        "frontmatter `description` must be a non-empty string",
                                    )
                                )

                            if "keep-coding-instructions" not in data:
                                failures.append(
                                    Failure(
                                        "output-style-mirror",
                                        where,
                                        "frontmatter is missing required `keep-coding-instructions: true`",
                                    )
                                )
                            elif data["keep-coding-instructions"] is not True:
                                val = data["keep-coding-instructions"]
                                failures.append(
                                    Failure(
                                        "output-style-mirror",
                                        where,
                                        f"frontmatter `keep-coding-instructions` must be boolean `true`, but is {val!r} ({type(val).__name__})",
                                    )
                                )

                    first_index = next((i for i, line in enumerate(style_body) if line.strip()), None)
                    if first_index is None:
                        failures.append(
                            Failure(
                                "output-style-mirror",
                                where,
                                "file has no body after frontmatter; expected an `# ` H1 title",
                            )
                        )
                    else:
                        first_line = style_body[first_index]
                        if name_value is not None:
                            expected_h1 = f"# {name_value}"
                            if first_line.rstrip(" \t") != expected_h1:
                                failures.append(
                                    Failure(
                                        "output-style-mirror",
                                        where,
                                        f"body must open with `{expected_h1}`, but the first line is `{first_line.strip()[:60]}`",
                                    )
                                )
                        elif not first_line.startswith("# "):
                            failures.append(
                                Failure(
                                    "output-style-mirror",
                                    where,
                                    f"body must open with an `# ` H1 title, but the first line is `{first_line.strip()[:60]}`",
                                )
                            )
                        if first_line.startswith("# "):
                            rest = style_body[first_index + 1 :]
                            if rest and not rest[0].strip():
                                rest = rest[1:]
                            style_mirrored = "\n".join(rest)

                    fm_failures = _check_style_self_containment(fm_text.split("\n"), where)
                    if parsed_fm_data is not None:
                        seen_details = {f.detail for f in fm_failures}
                        decoded_lines = [
                            line
                            for s in _iter_yaml_strings(parsed_fm_data)
                            for line in s.split("\n")
                        ]
                        for failure in _check_style_self_containment(decoded_lines, where):
                            if failure.detail not in seen_details:
                                fm_failures.append(failure)
                                seen_details.add(failure.detail)
                    failures.extend(fm_failures)
                    failures.extend(_check_style_self_containment(style_body, where))

        compiled_body: str | None = None
        try:
            skill_exists = skill_md_path.is_file()
        except OSError as exc:
            failures.append(Failure("output-style-mirror", str(skill_md), f"could not inspect file: {exc}"))
            skill_exists = False
        if not skill_exists:
            if not any(f.where == str(skill_md) and "could not inspect" in f.detail for f in failures):
                failures.append(
                    Failure(
                        "output-style-mirror",
                        str(skill_md),
                        "does not exist; the output style and its skill ship as a compiled pair",
                    )
                )
        else:
            try:
                compiled_body = compile_baseline_body(root / skill_dir)
            except (FileNotFoundError, ValueError, UnicodeDecodeError, OSError) as exc:
                failures.append(Failure("output-style-mirror", str(skill_dir), str(exc)))

            skill_text = _read_text_for_check(skill_md_path, str(skill_md), failures)
            if skill_text is not None:
                try:
                    reload_sentinel, last_check_label = extract_reload_sentinel(skill_text)
                except ValueError as exc:
                    failures.append(Failure("output-style-mirror", str(skill_md), str(exc)))
                else:
                    if reload_sentinel != last_check_label:
                        failures.append(
                            Failure(
                                "output-style-mirror",
                                str(skill_md),
                                f"reload sentinel `**{reload_sentinel}**` in `## Standing rules` does not match the final `## Self-check` item `**{last_check_label}**`",
                            )
                        )

        if style_mirrored is not None and compiled_body is not None and style_mirrored != compiled_body:
            line_no, preview = first_diff_line(style_mirrored, compiled_body)
            failures.append(
                Failure(
                    "output-style-mirror",
                    where,
                    f"body differs from compiled `{skill_dir}` output, first at body line {line_no} ({preview}); run `python3 scripts/sync_output_styles.py` to regenerate",
                )
            )

    return failures


def check_skill(directory: Path, root: Path) -> Result:
    failures: list[Failure] = []
    skill_md = directory / "SKILL.md"
    rel = skill_md.relative_to(root)

    if not skill_md.is_file():
        where = str(directory.relative_to(root))
        return (
            [Failure("skill-md-present", where, "skill directory has no SKILL.md")],
            skip_rest("skill-md-present", where, "no SKILL.md to inspect"),
        )

    try:
        text = skill_md.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        return (
            [Failure("frontmatter-parses", str(rel), f"could not read file as UTF-8: {exc}")],
            skip_rest("frontmatter-parses", str(rel), "SKILL.md could not be read"),
        )
    line_count = len(text.splitlines())
    if line_count > MAX_SKILL_MD_LINES:
        failures.append(Failure("skill-md-lines", str(rel), f"has {line_count} lines; the limit is {MAX_SKILL_MD_LINES}. Move material needed only in some cases into references/ files linked from SKILL.md"))

    def unparsable(detail: str) -> Result:
        return (
            failures + [Failure("frontmatter-parses", str(rel), detail)],
            skip_rest("frontmatter-parses", str(rel), "frontmatter could not be parsed"),
        )

    try:
        frontmatter_text, body = split_frontmatter(text)
    except ValueError as exc:
        return unparsable(str(exc))

    try:
        data = parse_frontmatter_yaml(frontmatter_text)
    except ValueError as exc:
        return unparsable(str(exc))

    if not isinstance(data, dict):
        kind = "empty" if data is None else f"a {type(data).__name__}"
        return unparsable(f"frontmatter must be a YAML mapping of keys to values, but parsed as {kind}")

    missing = [key for key in REQUIRED_KEYS if key not in data]
    for key in missing:
        failures.append(Failure("required-keys", str(rel), f"frontmatter is missing the required `{key}` key"))

    for key in REQUIRED_KEYS:
        if key in data:
            value = data[key]
            if not isinstance(value, str):
                kind = "empty" if value is None else f"a {type(value).__name__}"
                failures.append(Failure("required-keys", str(rel), f"frontmatter `{key}` must be a string, but is {kind}"))
            elif not value.strip():
                failures.append(Failure("required-keys", str(rel), f"frontmatter `{key}` is present but empty"))

    skipped: list[Skipped] = []
    description = data.get("description")
    if isinstance(description, str) and description.strip():
        if len(description) > MAX_DESCRIPTION_LENGTH:
            failures.append(Failure("description-length", str(rel), f"skill `{directory.name}` has a {len(description)}-character description; the limit is {MAX_DESCRIPTION_LENGTH}"))
        brackets = sorted({char for char in description if char in "<>"})
        if brackets:
            failures.append(Failure("description-angle-brackets", str(rel), f"description contains {' and '.join(f'`{char}`' for char in brackets)}; some hosts display them as HTML entities, so reword without angle brackets"))
    else:
        for check in ("description-length", "description-angle-brackets"):
            skipped.append(Skipped(check, str(rel), "`description` is missing or not a usable string"))

    name = data.get("name")
    if isinstance(name, str) and name.strip():
        if name.strip() != directory.name:
            failures.append(Failure("name-matches-directory", str(rel), f"frontmatter name is `{name.strip()}` but the directory is `{directory.name}`; they must match"))
        if len(name) > MAX_NAME_LENGTH or not NAME_PATTERN.fullmatch(name):
            failures.append(Failure("name-format", str(rel), f"frontmatter name `{name}` must be 1-{MAX_NAME_LENGTH} lowercase ASCII letters, digits and single hyphens, not starting or ending with a hyphen"))
    else:
        for check in ("name-matches-directory", "name-format"):
            skipped.append(Skipped(check, str(rel), "`name` is missing or not a usable string"))

    if "compatibility" in data:
        compatibility = data["compatibility"]
        if not isinstance(compatibility, str):
            kind = "empty" if compatibility is None else f"a {type(compatibility).__name__}"
            failures.append(Failure("compatibility-length", str(rel), f"frontmatter `compatibility` must be a string of 1-{MAX_COMPATIBILITY_LENGTH} characters, but is {kind}"))
        elif not 1 <= len(compatibility) <= MAX_COMPATIBILITY_LENGTH:
            failures.append(Failure("compatibility-length", str(rel), f"frontmatter `compatibility` has {len(compatibility)} characters; it must have 1-{MAX_COMPATIBILITY_LENGTH}"))

    first = next((line for line in body if line.strip()), None)
    if first is None:
        failures.append(Failure("h1-title", str(rel), "file has no body after the frontmatter; expected an `# ` H1 title"))
    elif not first.startswith("# "):
        failures.append(Failure("h1-title", str(rel), f"body must open with an `# ` H1 title, but the first line is `{first.strip()[:60]}`"))

    h2_headings = [line.strip() for line in outside_code_fences(body) if line.startswith("## ")]
    if "## Self-check" not in h2_headings:
        failures.append(Failure("self-check-section", str(rel), "body has no `## Self-check` section; every skill carries one the agent runs before declaring done"))
    elif h2_headings[-1] != "## Self-check":
        failures.append(Failure("self-check-section", str(rel), f"`## Self-check` must be the last `## ` heading, but `{h2_headings[-1][:60]}` follows it; move it to the end"))

    return failures, skipped


def main() -> int:
    if yaml is None:
        sys.stderr.write(
            "validate_skills: PyYAML is required. Install it with `pip install pyyaml`.\n"
        )
        return 2

    parser = argparse.ArgumentParser(description="Validate .agents/skills/*/SKILL.md against AGENTS.md conventions.")
    parser.add_argument("--root", default=".", help="repository root to validate (default: current directory)")
    args = parser.parse_args()

    try:
        root = Path(args.root).resolve()
        skills_root = root / SKILLS_DIR
        if not skills_root.is_dir():
            sys.stderr.write(f"validate_skills: no skills directory at {skills_root}\n")
            return 2
        directories = sorted(p for p in skills_root.iterdir() if p.is_dir())
    except OSError as exc:
        sys.stderr.write(f"validate_skills: could not inspect repository paths under `{args.root}`: {exc}\n")
        return 2
    if not directories:
        sys.stderr.write(f"validate_skills: {skills_root} contains no skill directories\n")
        return 2

    failures: list[Failure] = check_symlink(root) + check_output_style_mirrors(root)
    skips: list[Skipped] = []
    for directory in directories:
        for check in (check_skill, check_skill_files):
            directory_failures, directory_skips = check(directory, root)
            failures.extend(directory_failures)
            skips.extend(directory_skips)

    print(f"validate_skills: {len(directories)} skill(s) under {SKILLS_DIR}\n")

    by_check: dict[str, list[Failure]] = {}
    for failure in failures:
        by_check.setdefault(failure.check, []).append(failure)

    by_skip: dict[str, list[Skipped]] = {}
    for skip in skips:
        by_skip.setdefault(skip.check, []).append(skip)

    for check, description in CHECKS:
        hits = by_check.get(check, [])
        misses = by_skip.get(check, [])
        if hits:
            print(f"FAIL  {check}: {description}")
        elif misses:
            print(f"n/a   {check}: {description}")
        else:
            print(f"PASS  {check}: {description}")
        for failure in hits:
            print(f"        {failure.where}: {failure.detail}")
        for skip in misses:
            print(f"        not evaluated for {skip.where}: {skip.reason}")

    print()
    if failures:
        broken = len({f.check for f in failures})
        print(f"validate_skills: FAILED — {len(failures)} problem(s) across {broken} check(s).")
        return 1
    print("validate_skills: OK — all checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
