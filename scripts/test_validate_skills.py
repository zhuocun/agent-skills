"""Regression tests for the selection-policy mirror check."""

import tempfile
import unittest
from pathlib import Path

from validate_skills import POLICY_END, POLICY_START, check_selection_policy


def block(body: str = "Select from installed descriptions.\n") -> str:
    return f"{POLICY_START}\n{body}{POLICY_END}\n"


class SelectionPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.write("AGENTS.md", block())
        self.write("README.md", f"Overview\n```markdown\n{block()}```\n")

    def write(self, name: str, content: str) -> None:
        (self.root / name).write_text(content, encoding="utf-8")

    def assert_rejected(self, name: str, content: str) -> None:
        self.write(name, content)
        failures = check_selection_policy(self.root)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0].check, "skill-selection-policy-mirror")
        self.assertEqual(failures[0].where, name)

    def test_matching_blocks_allow_different_surroundings(self) -> None:
        self.assertEqual(check_selection_policy(self.root), [])

    def test_missing_or_malformed_blocks(self) -> None:
        for content in (
            "No markers\n",
            f"{POLICY_START}\ntext\n",
            f"{POLICY_END}\n{POLICY_START}\n",
            block() + block(),
            block(" \n\t\n"),
        ):
            with self.subTest(content=content):
                self.assert_rejected("README.md", content)

    def test_missing_file(self) -> None:
        (self.root / "AGENTS.md").unlink()
        failures = check_selection_policy(self.root)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0].where, "AGENTS.md")

    def test_changed_word_is_rejected(self) -> None:
        self.assert_rejected("README.md", block("Load every skill.\n"))

    def test_whitespace_drift_is_rejected(self) -> None:
        self.assert_rejected("README.md", block("Select from installed descriptions. \n"))

    def test_line_ending_drift_is_rejected(self) -> None:
        (self.root / "README.md").write_bytes(block().replace("\n", "\r\n").encode())
        self.assertEqual(len(check_selection_policy(self.root)), 1)

    def test_missing_end_marker_is_rejected_in_agents(self) -> None:
        self.assert_rejected("AGENTS.md", f"{POLICY_START}\ntext\n")


if __name__ == "__main__":
    unittest.main()
