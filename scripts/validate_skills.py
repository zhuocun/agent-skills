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
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - environment problem, not a repo defect
    sys.stderr.write(
        "validate_skills: PyYAML is required. Install it with `pip install pyyaml`.\n"
    )
    raise SystemExit(2) from None

SKILLS_DIR = Path(".agents/skills")
SYMLINK = Path(".claude/skills")
OUTPUT_STYLE_MIRRORS = (
    (Path(".claude/output-styles/baseline.md"), Path(".agents/skills/communicate/SKILL.md")),
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
    ("output-style-mirror", "each mirrored output style's body, below its frontmatter and H1, equals its skill's"),
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
    fence: str | None = None
    for line in lines:
        match = CODE_FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
            else:
                yield line
        elif match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) and not line.strip()[len(match.group(1)):].strip():
            fence = None


def inline_link_targets(text: str) -> list[str]:
    """Return the targets of inline Markdown links in text, including `<...>` targets with spaces."""
    return [angled or bare for angled, bare in LINK_TARGET.findall(text)]


def link_targets(lines: list[str]) -> list[str]:
    """Return inline and reference-style link targets outside fenced code and inline code spans."""
    text = "\n".join(INLINE_CODE.sub("", line) for line in outside_code_fences(lines))
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
        lines = path.read_text(encoding="utf-8").split("\n")
        for target in link_targets(lines):
            local = local_path(target)
            if local is not None and not (path.parent / local).exists():
                failures.append(Failure("relative-links-resolve", str(path.relative_to(root)), f"link `{target}` points at `{local}`, which does not exist relative to this file; fix the path or create the file"))

    references = sorted(p for p in (directory / "references").rglob("*") if p.is_file()) if (directory / "references").is_dir() else []
    if not skill_md.is_file():
        skipped.append(Skipped("references-linked", str(directory.relative_to(root)), "no SKILL.md to link from"))
    elif references:
        skill_lines = skill_md.read_text(encoding="utf-8").split("\n")
        named = [local_path(target) for target in link_targets(skill_lines)]
        named += [code for line in outside_code_fences(skill_lines) for code in CODE_SPAN.findall(line)]
        linked = {(skill_md.parent / local).resolve() for local in named if local}
        for reference in references:
            if reference.resolve() not in linked:
                failures.append(Failure("references-linked", str(reference.relative_to(root)), f"is not linked from `{skill_md.relative_to(root)}`; link it, or name its `references/` path in inline code, directly in SKILL.md and say when to read it in full and to read it again after a compaction"))

    for reference in references:
        if reference.suffix != ".md":
            continue
        lines = reference.read_text(encoding="utf-8").splitlines()
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


def check_output_style_mirrors(root: Path) -> list[Failure]:
    failures: list[Failure] = []
    for style, skill in OUTPUT_STYLE_MIRRORS:
        where = str(style)
        bodies: list[str] = []
        for path in (style, skill):
            if not (root / path).is_file():
                failures.append(Failure("output-style-mirror", str(path), "does not exist; the output style and its skill ship as a mirrored pair"))
                continue
            try:
                bodies.append(mirrored_body(root / path))
            except ValueError as exc:
                failures.append(Failure("output-style-mirror", str(path), str(exc)))
        if len(bodies) == 2 and bodies[0] != bodies[1]:
            style_lines, skill_lines = bodies[0].split("\n"), bodies[1].split("\n")
            index = next(
                (i for i, (a, b) in enumerate(zip(style_lines, skill_lines)) if a != b),
                min(len(style_lines), len(skill_lines)),
            )
            line = (style_lines + ["<end of file>"])[index].strip()[:60]
            first = f"`{line}`" if line else "a blank line"
            failures.append(Failure("output-style-mirror", where, f"body differs from `{skill}`, first at body line {index + 1} ({first}); edit both files together"))
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

    text = skill_md.read_text(encoding="utf-8")
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
        data = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        return unparsable(f"frontmatter is not valid YAML: {' '.join(str(exc).split())}")

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
    parser = argparse.ArgumentParser(description="Validate .agents/skills/*/SKILL.md against AGENTS.md conventions.")
    parser.add_argument("--root", default=".", help="repository root to validate (default: current directory)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    skills_root = root / SKILLS_DIR
    if not skills_root.is_dir():
        sys.stderr.write(f"validate_skills: no skills directory at {skills_root}\n")
        return 2

    directories = sorted(p for p in skills_root.iterdir() if p.is_dir())
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
