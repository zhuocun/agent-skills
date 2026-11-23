#!/usr/bin/env python3
"""Unit tests for `sync_output_styles.py` and `validate_skills.py` output-style checks.

Runs both stdlib-only (injecting a test-only frontmatter parser when PyYAML is
absent) and against real PyYAML when PyYAML is installed.
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import sync_output_styles
import validate_skills

VALID_SKILL_MD = """\
---
name: communicate
description: >-
  Governs every message to the user in the conversation.
---

# Communicate

This file governs how you write to the user.

**Priority order.** Highest first: grounded truth, concision.

## Standing rules

- **Session persistence.** Stay active across tasks and compactions until turned off.
- **Reload after truncation.** If context holds no complete copy, read `SKILL.md` in full from `communicate`. A complete copy ends with `## Self-check` and its **ASD-STE100** item.
- **Reply language.** Follow a loaded language skill where it applies.

## The ten failure modes

### 1. Burying the answer

- Open with the one-sentence answer.

## ASD-STE100 Simplified Technical English

When writing in English, read [ASD-STE100 Simplified Technical English](references/asd-ste100.md) in full before sending the message, and read it again after a compaction.

## Self-check

Before sending, confirm that each rule holds:

- [ ] **Standing rules** and **Priority order:** **Session persistence**, **Reload after truncation**, **Reply language**, and the priority order.
- [ ] **Failure mode 1:** answer first.
- [ ] **ASD-STE100:** when writing in English, `references/asd-ste100.md` was read in full and its check passes.
"""

VALID_STE_MD = """\
# ASD-STE100 Simplified Technical English

- Use the active voice.
- Hold an instruction sentence to 20 words.
- Hold a description sentence to 25 words.

## Checks

- [ ] **ASD-STE100:** active voice, 20-word instructions, and 25-word descriptions hold.
"""

VALID_BASELINE_HEADER = """\
---
name: Baseline
description: Governs how you write to the user rather than what work you do.
keep-coding-instructions: true
---

# Baseline

"""

EXPECTED_COMPILED_BODY = """\
This file governs how you write to the user.

**Priority order.** Highest first: grounded truth, concision.

## Standing rules

- **Session persistence.** Stay active across tasks and compactions until turned off.
- **Reply language.** Follow a loaded language skill where it applies.

## The ten failure modes

### 1. Burying the answer

- Open with the one-sentence answer.

## ASD-STE100 Simplified Technical English

- Use the active voice.
- Hold an instruction sentence to 20 words.
- Hold a description sentence to 25 words.

## Self-check

Before sending, confirm that each rule holds:

- [ ] **Standing rules** and **Priority order:** **Session persistence**, **Reply language**, and the priority order.
- [ ] **Failure mode 1:** answer first.
- [ ] **ASD-STE100:** active voice, 20-word instructions, and 25-word descriptions hold.
"""


def _test_only_parse_frontmatter(text: str) -> object:
    """Minimal test-only frontmatter parser injected ONLY when PyYAML is not installed."""
    lines = text.split("\n")
    non_empty = [line for line in lines if line.strip() and not line.lstrip().startswith("#")]
    if not non_empty:
        return None
    if non_empty[0].startswith("- "):
        return [line[2:].strip() for line in non_empty if line.startswith("- ")]
    if ":" not in non_empty[0]:
        return non_empty[0].strip()

    data: dict[str, object] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        match = re.match(r"^([A-Za-z0-9_.-]+)\s*:(.*)$", line)
        if not match:
            raise ValueError(f"frontmatter is not valid YAML: invalid line {line!r}")
        key, rest = match.group(1), match.group(2).strip()
        if rest in {">", ">-", "|", "|-"}:
            block: list[str] = []
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i].startswith(" ")):
                block.append(lines[i].strip())
                i += 1
            data[key] = " ".join(part for part in block if part)
            continue
        if rest.startswith('"'):
            m = re.match(r'^("(?:\\.|[^"\\])*")(?:\s+#.*)?$', rest)
            if not m:
                raise ValueError(f"frontmatter is not valid YAML: {rest!r}")
            data[key] = json.loads(m.group(1))
        elif rest.startswith("'"):
            m = re.match(r"^'((?:''|[^'])*)'(?:\s+#.*)?$", rest)
            if not m:
                raise ValueError(f"frontmatter is not valid YAML: {rest!r}")
            data[key] = m.group(1).replace("''", "'")
        else:
            scalar = re.sub(r"\s+#.*$", "", rest).strip()
            if ": " in scalar or scalar.endswith(":"):
                raise ValueError(f"frontmatter is not valid YAML: unquoted colon in {scalar!r}")
            if scalar == "" or scalar == "null":
                data[key] = None
            elif scalar == "true":
                data[key] = True
            elif scalar == "false":
                data[key] = False
            elif re.fullmatch(r"[+-]?\d+", scalar):
                data[key] = int(scalar)
            else:
                data[key] = scalar
        i += 1
    return data


@contextlib.contextmanager
def _with_validator_yaml():
    """Use real PyYAML when installed; inject the test-only parser only in stdlib-only runs."""
    if validate_skills.yaml is not None:
        yield
    else:
        with mock.patch.object(
            validate_skills, "parse_frontmatter_yaml", _test_only_parse_frontmatter
        ):
            yield


def check_mirrors(root: Path) -> list[validate_skills.Failure]:
    with _with_validator_yaml():
        return validate_skills.check_output_style_mirrors(root)


def build_fixture_repo(
    root: Path,
    *,
    skill_md: str = VALID_SKILL_MD,
    ste_md: str = VALID_STE_MD,
    baseline_md: str | None = None,
    baseline_bytes: bytes | None = None,
    settings_json: object = None,
    include_settings: bool = True,
) -> Path:
    """Create a minimal repository fixture under `root` and return `root`."""
    comm_dir = root / ".agents/skills/communicate"
    ref_dir = comm_dir / "references"
    style_dir = root / ".claude/output-styles"
    ref_dir.mkdir(parents=True, exist_ok=True)
    style_dir.mkdir(parents=True, exist_ok=True)

    (comm_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    (ref_dir / "asd-ste100.md").write_text(ste_md, encoding="utf-8")

    style_path = style_dir / "baseline.md"
    if baseline_bytes is not None:
        style_path.write_bytes(baseline_bytes)
    else:
        content = (
            baseline_md
            if baseline_md is not None
            else VALID_BASELINE_HEADER + EXPECTED_COMPILED_BODY
        )
        style_path.write_text(content, encoding="utf-8")

    if include_settings:
        data = settings_json if settings_json is not None else {"outputStyle": "Baseline"}
        (root / ".claude/settings.json").write_text(
            json.dumps(data, indent=2) + "\n", encoding="utf-8"
        )
    return root


def run_sync_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
        code = sync_output_styles.main(argv)
    return code, stdout_buf.getvalue(), stderr_buf.getvalue()


class TestSyncOutputStyles(unittest.TestCase):
    def test_compile_baseline_body_happy_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp))
            compiled = sync_output_styles.compile_baseline_body(
                root / ".agents/skills/communicate"
            )
            self.assertEqual(compiled, EXPECTED_COMPILED_BODY)

    def test_compile_preserves_trailing_blank_line_parity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp), skill_md=VALID_SKILL_MD + "\n")
            compiled = sync_output_styles.compile_baseline_body(
                root / ".agents/skills/communicate"
            )
            self.assertEqual(compiled, EXPECTED_COMPILED_BODY + "\n")

    def test_check_passes_when_up_to_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp))
            code, out, err = run_sync_cli(["--root", str(root), "--check"])
            self.assertEqual(code, 0, err)
            self.assertIn("OK", out)
            self.assertIn("words", out)
            self.assertIn("chars", out)
            self.assertEqual(check_mirrors(root), [])

    def test_sync_round_trip_writes_in_place_and_preserves_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            custom_header = (
                "---\n"
                "name: Baseline\n"
                "description: >-\n"
                "  Custom description preserved verbatim.\n"
                "keep-coding-instructions: true\n"
                "---\n\n"
                "# Baseline\n\n"
            )
            root = build_fixture_repo(
                Path(tmp), baseline_md=custom_header + "Stale body content.\n"
            )
            code, out, err = run_sync_cli(["--root", str(root)])
            self.assertEqual(code, 0, err)
            self.assertIn("wrote", out)

            written = (root / ".claude/output-styles/baseline.md").read_text(
                encoding="utf-8"
            )
            self.assertEqual(written, custom_header + EXPECTED_COMPILED_BODY)

            check_code, _, check_err = run_sync_cli(["--root", str(root), "--check"])
            self.assertEqual(check_code, 0, check_err)
            self.assertEqual(check_mirrors(root), [])

    def test_sync_preserves_crlf_and_header_bytes_verbatim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            crlf_header = (
                b"---\r\n"
                b"name: Baseline\r\n"
                b"description: Preserved CRLF header.\r\n"
                b"keep-coding-instructions: true\r\n"
                b"---\r\n"
                b"\r\n"
                b"# Baseline\r\n"
                b"   \r\n"
            )
            root = build_fixture_repo(
                Path(tmp), baseline_bytes=crlf_header + b"Old CRLF body.\r\n"
            )
            code, _, err = run_sync_cli(["--root", str(root)])
            self.assertEqual(code, 0, err)

            style_path = root / ".claude/output-styles/baseline.md"
            written_bytes = style_path.read_bytes()
            expected_bytes = crlf_header + EXPECTED_COMPILED_BODY.replace("\n", "\r\n").encode("utf-8")
            self.assertEqual(written_bytes, expected_bytes)

            check_code, _, check_err = run_sync_cli(["--root", str(root), "--check"])
            self.assertEqual(check_code, 0, check_err)
            self.assertEqual(check_mirrors(root), [])

    def test_sync_preserves_symlinked_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as ext:
            root = build_fixture_repo(Path(tmp))
            target = Path(ext) / "real-baseline.md"
            target.write_text(
                VALID_BASELINE_HEADER + "Old symlinked content.\n", encoding="utf-8"
            )
            style_path = root / ".claude/output-styles/baseline.md"
            style_path.unlink()
            style_path.symlink_to(target)

            code, _, err = run_sync_cli(["--root", str(root)])
            self.assertEqual(code, 0, err)
            self.assertTrue(style_path.is_symlink())
            self.assertEqual(style_path.readlink(), target)
            self.assertEqual(
                target.read_text(encoding="utf-8"),
                VALID_BASELINE_HEADER + EXPECTED_COMPILED_BODY,
            )
            check_code, _, check_err = run_sync_cli(["--root", str(root), "--check"])
            self.assertEqual(check_code, 0, check_err)

    def test_drift_detection_reports_exact_first_differing_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            expected_line_no = (
                EXPECTED_COMPILED_BODY.split("\n").index("- Use the active voice.") + 1
            )
            drifted_body = EXPECTED_COMPILED_BODY.replace(
                "- Use the active voice.", "- Use the passive voice."
            )
            root = build_fixture_repo(
                Path(tmp), baseline_md=VALID_BASELINE_HEADER + drifted_body
            )

            code, _, err = run_sync_cli(["--root", str(root), "--check"])
            self.assertEqual(code, 1)
            self.assertIn(f"body line {expected_line_no} ", err)
            self.assertIn("python3 scripts/sync_output_styles.py", err)

            failures = check_mirrors(root)
            self.assertEqual(len(failures), 1)
            self.assertEqual(failures[0].check, "output-style-mirror")
            self.assertIn(f"body line {expected_line_no} ", failures[0].detail)
            self.assertIn("python3 scripts/sync_output_styles.py", failures[0].detail)

    def test_trailing_blank_line_drift_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(
                Path(tmp),
                baseline_md=VALID_BASELINE_HEADER + EXPECTED_COMPILED_BODY + "\n",
            )
            code, _, err = run_sync_cli(["--root", str(root), "--check"])
            self.assertEqual(code, 1)
            self.assertIn("a blank line", err)
            failures = check_mirrors(root)
            self.assertTrue(
                any("differs from compiled" in f.detail for f in failures), failures
            )

    def test_check_rejects_wrong_h1(self) -> None:
        header = (
            "---\nname: Baseline\ndescription: Test.\n"
            "keep-coding-instructions: true\n---\n\n# Wrong\n\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(
                Path(tmp), baseline_md=header + EXPECTED_COMPILED_BODY
            )
            code, _, err = run_sync_cli(["--root", str(root), "--check"])
            self.assertEqual(code, 1)
            self.assertIn("# Baseline", err)

    def test_cli_exit_2_on_missing_root_or_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, _, err = run_sync_cli(["--root", str(Path(tmp) / "does-not-exist")])
            self.assertEqual(code, 2)
            self.assertIn("does not exist", err)

            root = build_fixture_repo(Path(tmp))
            (root / ".agents/skills/communicate/references/asd-ste100.md").unlink()
            code, _, err = run_sync_cli(["--root", str(root), "--check"])
            self.assertEqual(code, 2)
            self.assertIn("missing required input file", err)

    def test_file_errors_report_diagnostics_without_tracebacks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp))
            style_path = root / ".claude/output-styles/baseline.md"

            # Denied destination write returns exit 1 with affected path.
            real_open = Path.open

            def deny_style_write(self: Path, mode: str = "r", *args: object, **kwargs: object):
                if self.resolve() == style_path.resolve() and "w" in mode:
                    raise PermissionError("read-only destination")
                return real_open(self, mode, *args, **kwargs)

            with mock.patch.object(Path, "open", deny_style_write):
                code, _, err = run_sync_cli(["--root", str(root)])
            self.assertEqual(code, 1)
            self.assertIn(str(style_path), err)
            self.assertIn("could not write", err)

            # Invalid UTF-8 baseline.md returns exit 1 from sync and Failure from validator.
            style_path.write_bytes(b"\xff\xfe\x00invalid-utf8")
            code, _, err = run_sync_cli(["--root", str(root), "--check"])
            self.assertEqual(code, 1)
            self.assertIn("UTF-8", err)

            failures = check_mirrors(root)
            self.assertTrue(
                any(f.check == "output-style-mirror" and "UTF-8" in f.detail for f in failures),
                failures,
            )

    def test_fenced_code_headings_do_not_confuse_compiler(self) -> None:
        fenced_ste = (
            "# ASD-STE100 Simplified Technical English\n\n"
            "- Use the active voice.\n"
            "```markdown\n"
            "## Checks\n"
            "- [ ] **ASD-STE100:** fake check inside code fence.\n"
            "```\n\n"
            "## Checks\n\n"
            "- [ ] **ASD-STE100:** real check outside code fence.\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp), ste_md=fenced_ste)
            compiled = sync_output_styles.compile_baseline_body(
                root / ".agents/skills/communicate"
            )
            self.assertIn("- [ ] **ASD-STE100:** real check outside code fence.", compiled)
            self.assertIn("- [ ] **ASD-STE100:** fake check inside code fence.", compiled)


class TestFrontmatterAndSelfContainment(unittest.TestCase):
    def test_settings_absent_still_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp), include_settings=False)
            self.assertEqual(check_mirrors(root), [])

    def test_missing_keep_coding_instructions_fails(self) -> None:
        header = "---\nname: Baseline\ndescription: Test.\n---\n\n# Baseline\n\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(
                Path(tmp), baseline_md=header + EXPECTED_COMPILED_BODY
            )
            failures = check_mirrors(root)
            self.assertTrue(
                any("keep-coding-instructions" in f.detail for f in failures), failures
            )

    def test_keep_coding_instructions_false_and_string_true_fail(self) -> None:
        for bad_val in ("false", '"true"', "'true'", "1"):
            with self.subTest(value=bad_val):
                header = (
                    f"---\nname: Baseline\ndescription: Test.\n"
                    f"keep-coding-instructions: {bad_val}\n---\n\n# Baseline\n\n"
                )
                with tempfile.TemporaryDirectory() as tmp:
                    root = build_fixture_repo(
                        Path(tmp), baseline_md=header + EXPECTED_COMPILED_BODY
                    )
                    failures = check_mirrors(root)
                    self.assertTrue(
                        any("boolean `true`" in f.detail for f in failures), failures
                    )

    def test_name_mismatch_padded_name_and_non_string_output_style_fail(self) -> None:
        # Mismatched name
        header = (
            "---\nname: OtherStyle\ndescription: Test.\n"
            "keep-coding-instructions: true\n---\n\n# OtherStyle\n\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(
                Path(tmp),
                baseline_md=header + EXPECTED_COMPILED_BODY,
                settings_json={"outputStyle": "Baseline"},
            )
            failures = check_mirrors(root)
            self.assertTrue(any("outputStyle" in f.detail for f in failures), failures)

        # Quoted name with surrounding spaces must not match "Baseline"
        padded_header = (
            '---\nname: " Baseline "\ndescription: Test.\n'
            "keep-coding-instructions: true\n---\n\n# Baseline\n\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(
                Path(tmp),
                baseline_md=padded_header + EXPECTED_COMPILED_BODY,
                settings_json={"outputStyle": "Baseline"},
            )
            failures = check_mirrors(root)
            self.assertTrue(any("whitespace" in f.detail for f in failures), failures)
            self.assertTrue(any("outputStyle" in f.detail for f in failures), failures)

        # Non-string outputStyle in .claude/settings.json must fail
        for bad_setting in (False, 123, "", None, ["Baseline"]):
            with self.subTest(outputStyle=bad_setting):
                with tempfile.TemporaryDirectory() as tmp:
                    root = build_fixture_repo(
                        Path(tmp), settings_json={"outputStyle": bad_setting}
                    )
                    failures = check_mirrors(root)
                    self.assertTrue(
                        any("outputStyle" in f.detail for f in failures), failures
                    )

    def test_wrong_h1_fails(self) -> None:
        header = (
            "---\nname: Baseline\ndescription: Test.\n"
            "keep-coding-instructions: true\n---\n\n# Communicate\n\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(
                Path(tmp), baseline_md=header + EXPECTED_COMPILED_BODY
            )
            failures = check_mirrors(root)
            self.assertTrue(any("# Baseline" in f.detail for f in failures), failures)

    def test_yaml_parsing_edge_cases(self) -> None:
        # Invalid unquoted colon in mapping value must fail
        invalid_yaml_header = (
            "---\nname: Baseline\ndescription: Test: example\n"
            "keep-coding-instructions: true\n---\n\n# Baseline\n\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(
                Path(tmp), baseline_md=invalid_yaml_header + EXPECTED_COMPILED_BODY
            )
            failures = check_mirrors(root)
            self.assertTrue(any("not valid YAML" in f.detail for f in failures), failures)

        # Valid quoted value followed by an inline comment must pass
        quoted_comment_header = (
            '---\nname: "Baseline" # active style\n'
            'description: "Governs user replies." # summary\n'
            "keep-coding-instructions: true\n---\n\n# Baseline\n\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(
                Path(tmp), baseline_md=quoted_comment_header + EXPECTED_COMPILED_BODY
            )
            self.assertEqual(check_mirrors(root), [])

        # Production validator has no divergent fallback parser when PyYAML is absent
        with mock.patch.object(validate_skills, "yaml", None):
            with self.assertRaises(RuntimeError):
                validate_skills.parse_frontmatter_yaml("name: Baseline")

    def test_non_mapping_and_missing_description_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(
                Path(tmp),
                baseline_md="---\n- not-a-map\n---\n\n# Baseline\n\n" + EXPECTED_COMPILED_BODY,
            )
            failures = check_mirrors(root)
            self.assertTrue(any("YAML mapping" in f.detail for f in failures), failures)

        header = '---\nname: Baseline\ndescription: ""\nkeep-coding-instructions: true\n---\n\n# Baseline\n\n'
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(
                Path(tmp), baseline_md=header + EXPECTED_COMPILED_BODY
            )
            failures = check_mirrors(root)
            self.assertTrue(any("`description`" in f.detail for f in failures), failures)

    def test_self_containment_catches_body_emphasis_and_frontmatter_leaks(self) -> None:
        body_cases = [
            ("relative link", "- See [guide](./local.md).\n", "relative link"),
            ("references code span", "- Read `references/foo.md`.\n", "references/foo.md"),
            ("bare references path", "- Read references/bar.md before acting.\n", "references/bar.md"),
            ("underscore emphasis references", "- Read _references/bar.md_ before acting.\n", "references/bar.md"),
            ("SKILL.md mention", "- Reload SKILL.md after compaction.\n", "SKILL.md"),
            ("backticked SKILL.md", "- Reload `SKILL.md` after compaction.\n", "SKILL.md"),
            ("underscore emphasis SKILL.md", "- Reload _SKILL.md_ after compaction.\n", "SKILL.md"),
        ]
        for label, extra_line, expected_substr in body_cases:
            with self.subTest(case=label):
                ste_with_leak = VALID_STE_MD.replace(
                    "- Use the active voice.\n",
                    f"- Use the active voice.\n{extra_line}",
                )
                with tempfile.TemporaryDirectory() as tmp:
                    root = build_fixture_repo(Path(tmp), ste_md=ste_with_leak)
                    code, _, err = run_sync_cli(["--root", str(root)])
                    self.assertEqual(code, 0, err)
                    failures = check_mirrors(root)
                    self.assertTrue(
                        any(expected_substr in f.detail for f in failures), failures
                    )

        # Frontmatter leaks in description must also be caught
        for label, desc, expected_substr in (
            ("frontmatter SKILL.md", "Compiled from SKILL.md.", "SKILL.md"),
            ("frontmatter references/", "Inlines references/foo.md.", "references/foo.md"),
        ):
            with self.subTest(case=label):
                header = (
                    f"---\nname: Baseline\ndescription: {desc}\n"
                    "keep-coding-instructions: true\n---\n\n# Baseline\n\n"
                )
                with tempfile.TemporaryDirectory() as tmp:
                    root = build_fixture_repo(
                        Path(tmp), baseline_md=header + EXPECTED_COMPILED_BODY
                    )
                    failures = check_mirrors(root)
                    self.assertTrue(
                        any(expected_substr in f.detail for f in failures), failures
                    )

    def test_self_containment_ignores_fenced_code_multiline_inline_code_and_external_urls(
        self,
    ) -> None:
        valid_examples = (
            "- External docs at [spec](https://example.com/references/ste) and [top](#self-check).\n"
            "- Multiline inline code example: `first line\n"
            "  [not a link](./local.md)` stays allowed.\n"
            "```markdown\n"
            "See [guide](references/foo.md), `references/bar.md`, references/baz.md, and SKILL.md.\n"
            "```\n"
            "~~~\n"
            "Also ignore [other](./x.md) and SKILL.md inside tilde fences.\n"
            "~~~\n"
        )
        ste_with_valid = VALID_STE_MD.replace(
            "- Use the active voice.\n",
            f"- Use the active voice.\n{valid_examples}",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp), ste_md=ste_with_valid)
            code, _, err = run_sync_cli(["--root", str(root)])
            self.assertEqual(code, 0, err)
            self.assertEqual(check_mirrors(root), [])


class TestFailClosedAnchorsAndSentinel(unittest.TestCase):
    def test_missing_or_duplicate_reload_bullet_raises(self) -> None:
        missing = VALID_SKILL_MD.replace(
            "- **Reload after truncation.** If context holds no complete copy, read `SKILL.md` in full from `communicate`. A complete copy ends with `## Self-check` and its **ASD-STE100** item.\n",
            "",
        )
        duplicate = VALID_SKILL_MD.replace(
            "- **Reply language.**",
            "- **Reload after truncation.** Duplicate **ASD-STE100** item.\n- **Reply language.**",
        )
        for label, bad_skill in (("missing", missing), ("duplicate", duplicate)):
            with self.subTest(case=label):
                with tempfile.TemporaryDirectory() as tmp:
                    root = build_fixture_repo(Path(tmp), skill_md=bad_skill)
                    with self.assertRaisesRegex(ValueError, "Reload after truncation"):
                        sync_output_styles.compile_baseline_body(
                            root / ".agents/skills/communicate"
                        )

    def test_missing_or_duplicate_self_check_reload_token_raises(self) -> None:
        missing = VALID_SKILL_MD.replace("**Reload after truncation**, ", "")
        duplicate = VALID_SKILL_MD.replace(
            "**Reload after truncation**, ",
            "**Reload after truncation**, **Reload after truncation**, ",
        )
        for label, bad_skill in (("missing", missing), ("duplicate", duplicate)):
            with self.subTest(case=label):
                with tempfile.TemporaryDirectory() as tmp:
                    root = build_fixture_repo(Path(tmp), skill_md=bad_skill)
                    with self.assertRaisesRegex(ValueError, "Reload after truncation"):
                        sync_output_styles.compile_baseline_body(
                            root / ".agents/skills/communicate"
                        )

    def test_intervening_indented_section_or_reordered_standing_rules_raises(self) -> None:
        intervening = VALID_SKILL_MD.replace(
            "## Self-check",
            "## Extra section\n\nText.\n\n## Self-check",
        )
        indented_intervening = VALID_SKILL_MD.replace(
            "## Self-check",
            "  ## Extra section\n\nText.\n\n## Self-check",
        )
        nested_h3 = VALID_SKILL_MD.replace(
            "## Self-check",
            "### Nested heading\n\nText.\n\n## Self-check",
        )
        for label, bad_skill, pattern in (
            ("unindented extra h2", intervening, "immediately precede"),
            ("indented extra h2", indented_intervening, "immediately precede"),
            ("nested h3 inside STE", nested_h3, "unexpected heading"),
        ):
            with self.subTest(case=label):
                with tempfile.TemporaryDirectory() as tmp:
                    root = build_fixture_repo(Path(tmp), skill_md=bad_skill)
                    with self.assertRaisesRegex(ValueError, pattern):
                        sync_output_styles.compile_baseline_body(
                            root / ".agents/skills/communicate"
                        )

        # Standing rules appearing after Self-check must fail
        standing_after_self_check = (
            "---\nname: communicate\ndescription: Test.\n---\n\n# Communicate\n\nIntro.\n\n"
            "## ASD-STE100 Simplified Technical English\n\nPointer.\n\n"
            "## Self-check\n\n"
            "- [ ] **Standing rules:** **Reload after truncation**, ok.\n"
            "- [ ] **ASD-STE100:** check.\n\n"
            "## Standing rules\n\n"
            "- **Reload after truncation.** Ends with **ASD-STE100** item.\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp), skill_md=standing_after_self_check)
            with self.assertRaisesRegex(ValueError, "must precede"):
                sync_output_styles.compile_baseline_body(
                    root / ".agents/skills/communicate"
                )

    def test_ste_check_not_last_checklist_item_raises(self) -> None:
        not_last = VALID_SKILL_MD + "- [ ] **Trailing item:** after STE.\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp), skill_md=not_last)
            with self.assertRaisesRegex(ValueError, "must be the last"):
                sync_output_styles.compile_baseline_body(
                    root / ".agents/skills/communicate"
                )

    def test_ste_reference_missing_checks_or_duplicate_check_raises(self) -> None:
        no_checks = "# ASD-STE100 Simplified Technical English\n\n- Rule.\n"
        dup_checks = VALID_STE_MD + "- [ ] **ASD-STE100:** duplicate check.\n"
        bad_h1 = VALID_STE_MD.replace(
            "# ASD-STE100 Simplified Technical English", "# Wrong Title"
        )
        for label, bad_ste, pattern in (
            ("missing checks", no_checks, "## Checks"),
            ("duplicate ste check", dup_checks, "ASD-STE100"),
            ("wrong h1", bad_h1, "ASD-STE100 Simplified Technical English"),
        ):
            with self.subTest(case=label):
                with tempfile.TemporaryDirectory() as tmp:
                    root = build_fixture_repo(Path(tmp), ste_md=bad_ste)
                    with self.assertRaisesRegex(ValueError, pattern):
                        sync_output_styles.compile_baseline_body(
                            root / ".agents/skills/communicate"
                        )

    def test_reload_sentinel_mismatch_and_ambiguity_caught(self) -> None:
        mismatched = VALID_SKILL_MD.replace(
            "its **ASD-STE100** item.",
            "its **Failure mode 10** item.",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp), skill_md=mismatched)
            code, _, err = run_sync_cli(["--root", str(root)])
            self.assertEqual(code, 0, err)

            sentinel, last_item = sync_output_styles.extract_reload_sentinel(mismatched)
            self.assertEqual(sentinel, "Failure mode 10")
            self.assertEqual(last_item, "ASD-STE100")

            failures = check_mirrors(root)
            self.assertEqual(len(failures), 1)
            self.assertIn("Failure mode 10", failures[0].detail)
            self.assertIn("ASD-STE100", failures[0].detail)

        # Ambiguous reload bullet naming two bold items must fail even if the second matches
        for label, replacement in (
            ("two bold items", "its **Failure mode 10** and **ASD-STE100** items."),
            ("two named items", "its **Failure mode 10** item and **ASD-STE100** item."),
        ):
            with self.subTest(case=label):
                ambiguous = VALID_SKILL_MD.replace("its **ASD-STE100** item.", replacement)
                with self.assertRaisesRegex(ValueError, "multiple bold sentinel"):
                    sync_output_styles.extract_reload_sentinel(ambiguous)
                with tempfile.TemporaryDirectory() as tmp:
                    root = build_fixture_repo(Path(tmp), skill_md=ambiguous)
                    code, _, err = run_sync_cli(["--root", str(root)])
                    self.assertEqual(code, 0, err)
                    failures = check_mirrors(root)
                    self.assertTrue(
                        any("multiple bold sentinel" in f.detail for f in failures),
                        failures,
                    )

    def test_reload_sentinel_missing_bold_label_caught_by_validator(self) -> None:
        no_bold = VALID_SKILL_MD.replace(
            "its **ASD-STE100** item.",
            "the last numbered failure mode.",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp), skill_md=no_bold)
            code, _, err = run_sync_cli(["--root", str(root)])
            self.assertEqual(code, 0, err)

            failures = check_mirrors(root)
            self.assertTrue(any("sentinel" in f.detail for f in failures), failures)

    def test_code_only_sentinel_rejected(self) -> None:
        code_only = VALID_SKILL_MD.replace(
            "its **ASD-STE100** item.",
            "its `**ASD-STE100**` item.",
        )
        with self.assertRaisesRegex(ValueError, "must name a bold sentinel label"):
            sync_output_styles.extract_reload_sentinel(code_only)

    def test_block_boundaries_and_position_preserving_code_spans(self) -> None:
        lines = [
            "# Heading with `unclosed",
            "See [real](./missing.md) and `closing`.",
            "- item one with `unclosed",
            "- item two with [list-link](./missing2.md) and `closing`",
            "Literal [guide]`literal`(./not-a-link.md) stays separate.",
        ]
        targets = validate_skills.link_targets(lines)
        self.assertIn("./missing.md", targets)
        self.assertIn("./missing2.md", targets)
        self.assertNotIn("./not-a-link.md", targets)

    def test_malformed_backtick_fence_info_string_does_not_open_fence(self) -> None:
        lines = [
            "```bad`info",
            "## Checks",
            "See [visible](./missing.md).",
        ]
        outside = [line for _, line in sync_output_styles.iter_lines_outside_code_fences(lines)]
        self.assertEqual(outside, lines)
        self.assertIn("./missing.md", validate_skills.link_targets(lines))

    def test_self_containment_catches_emphasis_after_link_and_yaml_escapes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp))
            code, _, err = run_sync_cli(["--root", str(root)])
            self.assertEqual(code, 0, err)
            style_path = root / ".claude/output-styles/baseline.md"
            text = style_path.read_text(encoding="utf-8")
            old_desc = "description: Governs how you write to the user rather than what work you do."
            self.assertIn(old_desc, text)
            text = text.replace(
                old_desc,
                'description: "Read SKILL\\x2emd."',
            )
            text += "\n[site](https://example.com)__references/foo.md__\n"
            style_path.write_text(text, encoding="utf-8")

            failures = check_mirrors(root)
            self.assertTrue(any("references/foo.md" in f.detail for f in failures), failures)
            if validate_skills.yaml is not None:
                self.assertTrue(any("SKILL.md" in f.detail for f in failures), failures)

    def test_check_fails_when_blank_line_after_h1_missing_and_respects_settings_h1(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp))
            code, _, err = run_sync_cli(["--root", str(root)])
            self.assertEqual(code, 0, err)
            style_path = root / ".claude/output-styles/baseline.md"
            style_path.write_text(
                style_path.read_text(encoding="utf-8").replace("# Baseline\n\n", "# Baseline\n", 1),
                encoding="utf-8",
            )
            code, _, err = run_sync_cli(["--root", str(root), "--check"])
            self.assertEqual(code, 1)
            self.assertIn("blank line", err)

        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(
                Path(tmp),
                settings_json={"outputStyle": "CustomStyle"},
                baseline_md="---\nname: CustomStyle\ndescription: Custom.\nkeep-coding-instructions: true\n---\n\n# CustomStyle\n\nplaceholder\n",
            )
            code, _, err = run_sync_cli(["--root", str(root)])
            self.assertEqual(code, 0, err)
            code, _, err = run_sync_cli(["--root", str(root), "--check"])
            self.assertEqual(code, 0, err)
            self.assertEqual(check_mirrors(root), [])

    def test_corrupt_reference_utf8_reports_failure_instead_of_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture_repo(Path(tmp))
            code, _, err = run_sync_cli(["--root", str(root)])
            self.assertEqual(code, 0, err)
            (root / ".agents/skills/communicate/references/asd-ste100.md").write_bytes(b"\xff\xfe\x00")
            failures, _ = validate_skills.check_skill_files(
                root / ".agents/skills/communicate", root
            )
            self.assertTrue(any("UTF-8" in f.detail for f in failures), failures)
            mirror_failures = check_mirrors(root)
            self.assertTrue(any("UTF-8" in f.detail for f in mirror_failures), mirror_failures)


if __name__ == "__main__":
    unittest.main()
