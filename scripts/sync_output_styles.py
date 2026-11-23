#!/usr/bin/env python3
"""Compile `.claude/output-styles/baseline.md` from `.agents/skills/communicate/`.

Reads `.agents/skills/communicate/SKILL.md` and
`.agents/skills/communicate/references/asd-ste100.md`, applies four deterministic,
fail-closed structural transforms, and either writes `.claude/output-styles/baseline.md`
in place (preserving its existing header bytes, line endings, and symlinks) or checks
whether it is up to date.

Dependencies: Python 3.11+ standard library only (`tiktoken` is optional for
advisory token counts).

Usage:
    python3 scripts/sync_output_styles.py [--root PATH] [--check]

Exit codes:
    0  synced successfully, or up to date under `--check`
    1  stale under `--check`, invalid skill/reference/output-style content, or read/write failure
    2  bad root or missing input files
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterator
from pathlib import Path

STYLE_REL_PATH = Path(".claude/output-styles/baseline.md")
SETTINGS_REL_PATH = Path(".claude/settings.json")
COMMUNICATE_REL_DIR = Path(".agents/skills/communicate")
STE_REF_REL_PATH = Path("references/asd-ste100.md")

FENCE = "---"
CODE_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")

SKILL_H1 = "# Communicate"
BASELINE_H1 = "# Baseline"
STE_REF_H1 = "# ASD-STE100 Simplified Technical English"
STANDING_RULES_HEADING = "## Standing rules"
STE_HEADING = "## ASD-STE100 Simplified Technical English"
SELF_CHECK_HEADING = "## Self-check"
CHECKS_HEADING = "## Checks"

RELOAD_BULLET_PREFIX = "- **Reload after truncation.** "
RELOAD_SELF_CHECK_TOKEN = "**Reload after truncation**, "
STE_CHECK_PREFIX = "- [ ] **ASD-STE100:** "
CHECKLIST_PREFIX = "- [ ] "

BOLD_SPAN = re.compile(r"\*\*([^*]+?)\*\*")
CHECKLIST_BOLD_LEAD = re.compile(r"^- \[ \] \*\*([^*]+?)\*\*")


def _strip_eol(line: str) -> str:
    if line.endswith("\r\n"):
        return line[:-2]
    if line.endswith("\n"):
        return line[:-1]
    return line


def split_frontmatter(text: str) -> tuple[str, list[str]]:
    """Return (frontmatter_text, body_lines). Raises ValueError if absent/unterminated."""
    lines = text.split("\n")
    if not lines or lines[0].rstrip() != FENCE:
        raise ValueError("file does not start with a `---` frontmatter delimiter")
    for index in range(1, len(lines)):
        if lines[index].rstrip() == FENCE:
            return "\n".join(lines[1:index]), lines[index + 1 :]
    raise ValueError("frontmatter opened with `---` but is never closed by a second `---`")


def split_style_header_and_body(
    raw_text: str,
    expected_h1: str = BASELINE_H1,
) -> tuple[str, str]:
    """Split a raw (non-newline-translated) output-style file into `(header_prefix, normalized_body)`.

    `header_prefix` preserves the frontmatter, any blank lines before the H1,
    the opening H1 line, and the single blank line after it (including spaces
    and original CRLF/LF line endings) verbatim byte for byte.
    `normalized_body` uses `\n` line endings for comparison against `compile_baseline_body`.
    """
    raw_lines = raw_text.splitlines(keepends=True)
    if not raw_lines or _strip_eol(raw_lines[0]).rstrip() != FENCE:
        raise ValueError("file does not start with a `---` frontmatter delimiter")

    fm_end = next(
        (i for i in range(1, len(raw_lines)) if _strip_eol(raw_lines[i]).rstrip() == FENCE),
        None,
    )
    if fm_end is None:
        raise ValueError("frontmatter opened with `---` but is never closed by a second `---`")

    body_start = fm_end + 1
    h1_index = next(
        (i for i in range(body_start, len(raw_lines)) if _strip_eol(raw_lines[i]).strip()),
        None,
    )
    if h1_index is None or not _strip_eol(raw_lines[h1_index]).startswith("# "):
        raise ValueError("body does not open with an `# ` H1 title")

    h1_line = _strip_eol(raw_lines[h1_index]).rstrip(" \t")
    if expected_h1 is not None and h1_line != expected_h1:
        raise ValueError(f"expected opening H1 `{expected_h1}`, found `{h1_line}`")

    eol = "\r\n" if raw_lines[0].endswith("\r\n") else "\n"
    if h1_index + 1 < len(raw_lines) and not _strip_eol(raw_lines[h1_index + 1]).strip():
        blank_line = raw_lines[h1_index + 1]
        if not blank_line.endswith(("\r\n", "\n")):
            blank_line += eol
        header_prefix = "".join(raw_lines[: h1_index + 1]) + blank_line
        raw_body = "".join(raw_lines[h1_index + 2 :])
    else:
        h1_raw = raw_lines[h1_index]
        if not h1_raw.endswith(("\r\n", "\n")):
            h1_raw += eol
        header_prefix = "".join(raw_lines[:h1_index]) + h1_raw + eol
        raw_body = "".join(raw_lines[h1_index + 1 :])

    return header_prefix, raw_body.replace("\r\n", "\n")


def extract_body_lines(text: str, expected_h1: str | None = None) -> list[str]:
    """Return lines below frontmatter, the opening H1, and one blank line."""
    _, body = split_frontmatter(text)
    index = next((i for i, line in enumerate(body) if line.strip()), None)
    if index is None or not body[index].startswith("# "):
        raise ValueError("body does not open with an `# ` H1 title")
    if expected_h1 is not None and body[index].rstrip(" \t") != expected_h1:
        raise ValueError(f"expected opening H1 `{expected_h1}`, found `{body[index].strip()}`")
    rest = body[index + 1 :]
    if rest and not rest[0].strip():
        rest = rest[1:]
    return rest


def _strip_inline_code_single_line(text: str) -> str:
    """Replace CommonMark inline code spans on one line with spaces, preserving positions."""
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == "`":
            j = i
            while j < n and text[j] == "`":
                j += 1
            ticks = j - i
            k = j
            closed = False
            while k < n:
                if text[k] == "`":
                    m = k
                    while m < n and text[m] == "`":
                        m += 1
                    if m - k == ticks:
                        out.append(" " * (m - i))
                        i = m
                        closed = True
                        break
                    k = m
                else:
                    k += 1
            if not closed:
                out.append(text[i:j])
                i = j
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def _is_valid_fence_opener(line: str, match: re.Match[str]) -> bool:
    """CommonMark: a backtick fence info string may not contain backticks."""
    fence = match.group(1)
    if fence[0] == "`" and "`" in line[match.end() :]:
        return False
    return True


def _resolve_expected_baseline_h1(root: Path) -> str:
    """Resolve the expected H1 for `baseline.md` from `.claude/settings.json` when valid."""
    settings_path = root / SETTINGS_REL_PATH
    try:
        if not settings_path.is_file():
            return BASELINE_H1
        data = json.loads(settings_path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return BASELINE_H1
    if isinstance(data, dict) and "outputStyle" in data:
        raw_style = data["outputStyle"]
        if isinstance(raw_style, str) and raw_style.strip() and raw_style == raw_style.strip():
            return f"# {raw_style}"
    return BASELINE_H1


def iter_lines_outside_code_fences(lines: list[str]) -> Iterator[tuple[int, str]]:
    """Yield `(index, line)` pairs for lines outside fenced code blocks (` ``` ` or `~~~`)."""
    fence: str | None = None
    for index, line in enumerate(lines):
        match = CODE_FENCE.match(line)
        if fence is None:
            if match and _is_valid_fence_opener(line, match):
                fence = match.group(1)
            else:
                yield index, line
        elif (
            match
            and match.group(1)[0] == fence[0]
            and len(match.group(1)) >= len(fence)
            and not line.strip()[len(match.group(1)) :].strip()
        ):
            fence = None


def _parse_atx_heading(line: str) -> tuple[int, str] | None:
    """Return `(level, normalized_heading)` for a CommonMark ATX heading (0-3 leading spaces)."""
    match = ATX_HEADING.match(line)
    if not match:
        return None
    hashes = match.group(1)
    title = (match.group(2) or "").strip()
    normalized = f"{hashes} {title}" if title else hashes
    return len(hashes), normalized


def _find_section_boundaries(lines: list[str]) -> list[tuple[int, str]]:
    """Return `(line_index, normalized_heading)` for each level 1-2 ATX heading outside fenced code."""
    boundaries: list[tuple[int, str]] = []
    for index, line in iter_lines_outside_code_fences(lines):
        parsed = _parse_atx_heading(line)
        if parsed is not None and parsed[0] <= 2:
            boundaries.append((index, parsed[1]))
    return boundaries


def _section_range(
    lines: list[str],
    sections: list[tuple[int, str]],
    heading: str,
    source_label: str,
) -> tuple[int, int, int]:
    """Return `(section_pos, start_line_index, end_line_index)` for a unique section heading."""
    matches = [(pos, idx) for pos, (idx, text) in enumerate(sections) if text == heading]
    if not matches:
        raise ValueError(f"{source_label}: missing required `{heading}` heading")
    if len(matches) > 1:
        raise ValueError(f"{source_label}: expected exactly one `{heading}` heading, found {len(matches)}")
    pos, start_idx = matches[0]
    end_idx = sections[pos + 1][0] if pos + 1 < len(sections) else len(lines)
    return pos, start_idx, end_idx


def _read_utf8_text(path: Path, label: str) -> str:
    """Read a UTF-8 file normalized to `\n`, converting decode/OS errors to `ValueError`."""
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        raise
    except OSError as exc:
        raise ValueError(f"{label}: could not read file ({exc})") from None
    try:
        return raw.decode("utf-8").replace("\r\n", "\n")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label}: could not decode as UTF-8 ({exc})") from None


def _parse_ste_reference(ste_text: str, source_label: str) -> tuple[list[str], str]:
    """Extract `(ste_rules, ste_check)` from `references/asd-ste100.md`."""
    lines = ste_text.split("\n")
    h1_index = next((i for i, line in enumerate(lines) if line.strip()), None)
    if h1_index is None or lines[h1_index].rstrip(" \t") != STE_REF_H1:
        found = lines[h1_index].strip() if h1_index is not None else "<empty file>"
        raise ValueError(f"{source_label}: must open with `{STE_REF_H1}`, found `{found}`")

    sections = _find_section_boundaries(lines)
    _, checks_start, checks_end = _section_range(lines, sections, CHECKS_HEADING, source_label)
    if checks_start <= h1_index:
        raise ValueError(f"{source_label}: `{CHECKS_HEADING}` must appear after `{STE_REF_H1}`")

    rules_start = h1_index + 1
    if rules_start < checks_start and not lines[rules_start].strip():
        rules_start += 1
    ste_rules = list(lines[rules_start:checks_start])
    while ste_rules and not ste_rules[-1].strip():
        ste_rules.pop()
    if not any(line.strip() for line in ste_rules):
        raise ValueError(f"{source_label}: no rule lines found between `{STE_REF_H1}` and `{CHECKS_HEADING}`")

    check_lines = [
        line
        for index, line in iter_lines_outside_code_fences(lines)
        if checks_start < index < checks_end and line.startswith(STE_CHECK_PREFIX)
    ]
    if len(check_lines) != 1:
        raise ValueError(
            f"{source_label}: expected exactly one `{STE_CHECK_PREFIX}` line under `{CHECKS_HEADING}`, found {len(check_lines)}"
        )

    return ste_rules, check_lines[0]


def _normalize_label(raw: str) -> str:
    return raw.strip().rstrip(":").strip()


def extract_reload_sentinel(skill_text: str) -> tuple[str, str]:
    """Return `(reload_sentinel_label, last_self_check_label)` from `communicate/SKILL.md`.

    Parses the single unambiguous bold sentinel label named in the
    `- **Reload after truncation.** ` bullet inside `## Standing rules` and compares
    it with the bold lead-in of the final `- [ ] ` line inside `## Self-check`.
    Raises `ValueError` if any required anchor is missing or ambiguous.
    """
    lines = extract_body_lines(skill_text.replace("\r\n", "\n"), expected_h1=SKILL_H1)
    sections = _find_section_boundaries(lines)

    _, standing_start, standing_end = _section_range(lines, sections, STANDING_RULES_HEADING, "SKILL.md")
    reload_lines = [
        line
        for index, line in iter_lines_outside_code_fences(lines)
        if standing_start < index < standing_end and line.startswith(RELOAD_BULLET_PREFIX)
    ]
    if len(reload_lines) != 1:
        raise ValueError(
            f"SKILL.md: expected exactly one `{RELOAD_BULLET_PREFIX}` bullet inside `{STANDING_RULES_HEADING}`, found {len(reload_lines)}"
        )

    reload_rest = _strip_inline_code_single_line(reload_lines[0][len(RELOAD_BULLET_PREFIX) :])
    bold_matches = [_normalize_label(m) for m in BOLD_SPAN.findall(reload_rest)]
    if not bold_matches:
        raise ValueError(
            f"SKILL.md: `{RELOAD_BULLET_PREFIX}` bullet must name a bold sentinel label (such as `**ASD-STE100**`)"
        )
    if len(bold_matches) > 1:
        candidates = ", ".join(f"`**{label}**`" for label in bold_matches)
        raise ValueError(
            f"SKILL.md: `{RELOAD_BULLET_PREFIX}` bullet names multiple bold sentinel candidates ({candidates}); name exactly one"
        )
    reload_sentinel = bold_matches[0]
    if not reload_sentinel:
        raise ValueError(f"SKILL.md: `{RELOAD_BULLET_PREFIX}` bullet contains an empty sentinel label")

    _, sc_start, sc_end = _section_range(lines, sections, SELF_CHECK_HEADING, "SKILL.md")
    checklist_lines = [
        line
        for index, line in iter_lines_outside_code_fences(lines)
        if sc_start < index < sc_end and line.startswith(CHECKLIST_PREFIX)
    ]
    if not checklist_lines:
        raise ValueError(f"SKILL.md: no `{CHECKLIST_PREFIX}` items found inside `{SELF_CHECK_HEADING}`")

    last_match = CHECKLIST_BOLD_LEAD.match(checklist_lines[-1])
    if not last_match:
        raise ValueError(
            f"SKILL.md: final `{CHECKLIST_PREFIX}` line in `{SELF_CHECK_HEADING}` must start with a bold label"
        )
    last_label = _normalize_label(last_match.group(1))
    if not last_label:
        raise ValueError(
            f"SKILL.md: final `{CHECKLIST_PREFIX}` line in `{SELF_CHECK_HEADING}` has an empty bold label"
        )

    return reload_sentinel, last_label


def _compile_baseline_with_skill_body(communicate_dir: Path) -> tuple[str, str]:
    """Compile baseline body and also return the single-read `SKILL.md` body text for metrics."""
    skill_path = communicate_dir / "SKILL.md"
    ste_path = communicate_dir / STE_REF_REL_PATH
    if not skill_path.is_file():
        raise FileNotFoundError(f"missing skill file: {skill_path}")
    if not ste_path.is_file():
        raise FileNotFoundError(f"missing reference file: {ste_path}")

    ste_text = _read_utf8_text(ste_path, str(STE_REF_REL_PATH))
    skill_text = _read_utf8_text(skill_path, "SKILL.md")

    _, skill_body_lines = split_frontmatter(skill_text)
    skill_body_text = "\n".join(skill_body_lines)

    ste_rules, ste_check = _parse_ste_reference(ste_text, str(STE_REF_REL_PATH))
    lines = extract_body_lines(skill_text, expected_h1=SKILL_H1)

    # Verify required section presence and ordering before replacing any content.
    sections = _find_section_boundaries(lines)
    standing_pos, standing_start, standing_end = _section_range(
        lines, sections, STANDING_RULES_HEADING, "SKILL.md"
    )
    ste_pos, ste_start, _ = _section_range(lines, sections, STE_HEADING, "SKILL.md")
    sc_pos, sc_start, _ = _section_range(lines, sections, SELF_CHECK_HEADING, "SKILL.md")

    if not (standing_pos < ste_pos):
        raise ValueError(
            f"SKILL.md: `{STANDING_RULES_HEADING}` must precede `{STE_HEADING}` and `{SELF_CHECK_HEADING}`"
        )
    if ste_pos > sc_pos:
        raise ValueError(f"SKILL.md: `{STE_HEADING}` must precede `{SELF_CHECK_HEADING}`")
    if ste_pos + 1 != sc_pos:
        intervening = sections[ste_pos + 1][1]
        raise ValueError(
            f"SKILL.md: `{STE_HEADING}` must immediately precede `{SELF_CHECK_HEADING}`, but `{intervening}` appears between them"
        )
    if sc_pos != len(sections) - 1:
        trailing = sections[sc_pos + 1][1]
        raise ValueError(
            f"SKILL.md: `{SELF_CHECK_HEADING}` must be the final section, but `{trailing}` follows it"
        )

    nested_headings = [
        parsed[1]
        for index, line in iter_lines_outside_code_fences(lines)
        if ste_start < index < sc_start
        for parsed in (_parse_atx_heading(line),)
        if parsed is not None
    ]
    if nested_headings:
        raise ValueError(
            f"SKILL.md: unexpected heading `{nested_headings[0]}` inside `{STE_HEADING}` would be discarded during compilation"
        )

    # Transform 1: Strip skill-only reload bullet inside `## Standing rules`.
    reload_indices = [
        index
        for index, line in iter_lines_outside_code_fences(lines)
        if standing_start < index < standing_end and line.startswith(RELOAD_BULLET_PREFIX)
    ]
    if len(reload_indices) != 1:
        raise ValueError(
            f"SKILL.md: expected exactly one `{RELOAD_BULLET_PREFIX}` line inside `{STANDING_RULES_HEADING}`, found {len(reload_indices)}"
        )
    del lines[reload_indices[0]]

    # Transform 2: Strip matching Self-check token inside `## Self-check`.
    sections = _find_section_boundaries(lines)
    _, sc_start, sc_end = _section_range(lines, sections, SELF_CHECK_HEADING, "SKILL.md")
    token_hits = [
        (index, line.count(RELOAD_SELF_CHECK_TOKEN))
        for index, line in iter_lines_outside_code_fences(lines)
        if sc_start < index < sc_end and RELOAD_SELF_CHECK_TOKEN in line
    ]
    total_tokens = sum(count for _, count in token_hits)
    if total_tokens != 1:
        raise ValueError(
            f"SKILL.md: expected `{RELOAD_SELF_CHECK_TOKEN}` exactly once inside `{SELF_CHECK_HEADING}`, found {total_tokens}"
        )
    token_line_index = token_hits[0][0]
    lines[token_line_index] = lines[token_line_index].replace(RELOAD_SELF_CHECK_TOKEN, "", 1)

    # Transform 3: Inline `ASD-STE100` rules between its heading and `## Self-check`.
    sections = _find_section_boundaries(lines)
    _, ste_start, _ = _section_range(lines, sections, STE_HEADING, "SKILL.md")
    _, sc_start, _ = _section_range(lines, sections, SELF_CHECK_HEADING, "SKILL.md")
    lines[ste_start + 1 : sc_start] = [""] + ste_rules + [""]

    # Transform 4: Inline `ASD-STE100` check as the last checklist item under `## Self-check`.
    sections = _find_section_boundaries(lines)
    _, sc_start, sc_end = _section_range(lines, sections, SELF_CHECK_HEADING, "SKILL.md")
    sc_outside = [
        (index, line)
        for index, line in iter_lines_outside_code_fences(lines)
        if sc_start < index < sc_end
    ]
    checklist_indices = [index for index, line in sc_outside if line.startswith(CHECKLIST_PREFIX)]
    ste_check_indices = [index for index, line in sc_outside if line.startswith(STE_CHECK_PREFIX)]
    if len(ste_check_indices) != 1:
        raise ValueError(
            f"SKILL.md: expected exactly one `{STE_CHECK_PREFIX}` line inside `{SELF_CHECK_HEADING}`, found {len(ste_check_indices)}"
        )
    if not checklist_indices or ste_check_indices[0] != checklist_indices[-1]:
        raise ValueError(
            f"SKILL.md: `{STE_CHECK_PREFIX}` must be the last `{CHECKLIST_PREFIX}` line in `{SELF_CHECK_HEADING}`"
        )
    lines[ste_check_indices[0]] = ste_check

    return "\n".join(lines), skill_body_text


def compile_baseline_body(communicate_dir: Path) -> str:
    """Compile the mirrored body for `.claude/output-styles/baseline.md` from `communicate_dir`.

    Applies four deterministic, fail-closed transforms to `SKILL.md`'s body:
      1. Strip the single `- **Reload after truncation.** ` bullet inside `## Standing rules`.
      2. Strip the single `**Reload after truncation**, ` token inside `## Self-check`.
      3. Inline `references/asd-ste100.md`'s rules between `## ASD-STE100 Simplified Technical English`
         and `## Self-check`.
      4. Replace the final `- [ ] **ASD-STE100:** ` line in `## Self-check` with the check bullet
         from `references/asd-ste100.md`'s `## Checks` section.
    """
    compiled_body, _ = _compile_baseline_with_skill_body(communicate_dir)
    return compiled_body


def first_diff_line(actual: str, expected: str) -> tuple[int, str]:
    """Return `(1_based_line_number, preview)` for the first differing line between two bodies."""
    actual_lines, expected_lines = actual.split("\n"), expected.split("\n")
    index = next(
        (i for i, (a, b) in enumerate(zip(actual_lines, expected_lines)) if a != b),
        min(len(actual_lines), len(expected_lines)),
    )
    snippet = (actual_lines + ["<end of file>"])[index].strip()[:60]
    preview = f"`{snippet}`" if snippet else "a blank line"
    return index + 1, preview


def _count_o200k_tokens(text: str) -> int | None:
    """Return advisory `o200k_base` token count if `tiktoken` is installed and usable."""
    try:
        import tiktoken  # type: ignore[import-not-found]
    except ImportError:
        return None
    try:
        return len(tiktoken.get_encoding("o200k_base").encode(text))
    except Exception:
        return None


def _format_metrics(label: str, text: str) -> str:
    words = len(text.split())
    chars = len(text)
    tokens = _count_o200k_tokens(text)
    if tokens is not None:
        return f"{label}: {words} words, {chars} chars, {tokens} o200k_base tokens"
    return f"{label}: {words} words, {chars} chars"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compile or check .claude/output-styles/baseline.md from .agents/skills/communicate/."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="repository root (default: current directory)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify .claude/output-styles/baseline.md is up to date without writing",
    )
    args = parser.parse_args(argv)

    try:
        root = Path(args.root).resolve()
        root_is_dir = root.is_dir()
    except OSError as exc:
        sys.stderr.write(f"sync_output_styles: could not inspect root directory `{args.root}`: {exc}\n")
        return 2
    if not root_is_dir:
        sys.stderr.write(f"sync_output_styles: root directory does not exist: {root}\n")
        return 2

    communicate_dir = root / COMMUNICATE_REL_DIR
    skill_path = communicate_dir / "SKILL.md"
    ste_path = communicate_dir / STE_REF_REL_PATH
    style_path = root / STYLE_REL_PATH

    try:
        missing = [p for p in (skill_path, ste_path, style_path) if not p.is_file()]
    except OSError as exc:
        sys.stderr.write(f"sync_output_styles: could not inspect input paths under {root}: {exc}\n")
        return 1
    if missing:
        for path in missing:
            sys.stderr.write(f"sync_output_styles: missing required input file: {path}\n")
        return 2

    try:
        compiled_body, skill_body_text = _compile_baseline_with_skill_body(communicate_dir)
    except FileNotFoundError as exc:
        sys.stderr.write(f"sync_output_styles: {exc}\n")
        return 2
    except ValueError as exc:
        sys.stderr.write(f"sync_output_styles: compilation failed: {exc}\n")
        return 1

    try:
        raw_style_bytes = style_path.read_bytes()
        raw_style_text = raw_style_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        sys.stderr.write(f"sync_output_styles: could not decode {style_path} as UTF-8: {exc}\n")
        return 1
    except OSError as exc:
        sys.stderr.write(f"sync_output_styles: could not read {style_path}: {exc}\n")
        return 1

    expected_h1 = _resolve_expected_baseline_h1(root)
    try:
        header_prefix, existing_body = split_style_header_and_body(
            raw_style_text, expected_h1=expected_h1
        )
    except ValueError as exc:
        sys.stderr.write(f"sync_output_styles: invalid {STYLE_REL_PATH}: {exc}\n")
        return 1

    eol = "\r\n" if "\r\n" in header_prefix else "\n"
    payload = (header_prefix + compiled_body.replace("\n", eol)).encode("utf-8")

    if args.check:
        if existing_body != compiled_body:
            line_no, preview = first_diff_line(existing_body, compiled_body)
            sys.stderr.write(
                f"sync_output_styles: {STYLE_REL_PATH} is out of date, first differing at body line {line_no} ({preview}); "
                "run `python3 scripts/sync_output_styles.py` to regenerate.\n"
            )
            return 1
        if raw_style_bytes != payload:
            sys.stderr.write(
                f"sync_output_styles: {STYLE_REL_PATH} is missing the required blank line after `{expected_h1}` or has mismatched line endings; "
                "run `python3 scripts/sync_output_styles.py` to regenerate.\n"
            )
            return 1
        print(f"sync_output_styles: OK — {STYLE_REL_PATH} is up to date.")
        print(f"  {_format_metrics('communicate/SKILL.md body', skill_body_text)}")
        print(f"  {_format_metrics('baseline.md compiled body', compiled_body)}")
        return 0

    # Write in place (never os.replace / unlink) so symlinked baseline.md stays linked
    # and header bytes / line endings stay intact.
    try:
        with style_path.open("wb") as handle:
            handle.write(payload)
    except OSError as exc:
        sys.stderr.write(f"sync_output_styles: could not write {style_path}: {exc}\n")
        return 1

    print(f"sync_output_styles: wrote {STYLE_REL_PATH} in place.")
    print(f"  {_format_metrics('communicate/SKILL.md body', skill_body_text)}")
    print(f"  {_format_metrics('baseline.md compiled body', compiled_body)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
