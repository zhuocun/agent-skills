#!/usr/bin/env python3
"""Validate the skill files this repository ships.

Every rule enforced here is stated in AGENTS.md ("Skill authoring conventions"
and "What ships from this repo"). Rules that AGENTS.md only describes loosely
are deliberately not enforced; see the module docstring of each check.

Usage:
    python3 scripts/validate_skills.py [--root PATH]

Exit codes:
    0  every check passed
    1  at least one check failed
    2  the validator could not run (bad root, missing dependency)
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - environment problem, not a repo defect
    sys.stderr.write(
        "validate_skills: PyYAML is required. Install it with `pip install pyyaml`.\n"
    )
    raise SystemExit(2) from None

SKILLS_DIR = Path(".agents/skills")
SYMLINK = Path(".claude/skills")
REQUIRED_KEYS = ("name", "description")
FENCE = "---"

CHECKS = (
    ("skill-md-present", "every skill directory contains a SKILL.md"),
    ("frontmatter-parses", "SKILL.md opens with a --- block that parses as a YAML mapping"),
    ("required-keys", "frontmatter has non-empty `name` and `description`"),
    ("name-matches-directory", "frontmatter `name` equals the skill's directory name"),
    ("h1-title", "the body opens with an `# ` H1 title"),
    ("self-check-section", "the body has a `## Self-check` section"),
    ("claude-skills-symlink", ".claude/skills is a symlink resolving to .agents/skills"),
)


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
    names = [name for name, _ in CHECKS if name not in {"claude-skills-symlink"}]
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

    def unparsable(detail: str) -> Result:
        return (
            [Failure("frontmatter-parses", str(rel), detail)],
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
    name = data.get("name")
    if isinstance(name, str) and name.strip():
        if name.strip() != directory.name:
            failures.append(Failure("name-matches-directory", str(rel), f"frontmatter name is `{name.strip()}` but the directory is `{directory.name}`; they must match"))
    else:
        skipped.append(Skipped("name-matches-directory", str(rel), "`name` is missing or not a usable string"))

    first = next((line for line in body if line.strip()), None)
    if first is None:
        failures.append(Failure("h1-title", str(rel), "file has no body after the frontmatter; expected an `# ` H1 title"))
    elif not first.startswith("# "):
        failures.append(Failure("h1-title", str(rel), f"body must open with an `# ` H1 title, but the first line is `{first.strip()[:60]}`"))

    if not any(line.strip() == "## Self-check" for line in body):
        failures.append(Failure("self-check-section", str(rel), "body has no `## Self-check` section; every skill carries one the agent runs before declaring done"))

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

    failures: list[Failure] = check_symlink(root)
    skips: list[Skipped] = []
    for directory in directories:
        directory_failures, directory_skips = check_skill(directory, root)
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
