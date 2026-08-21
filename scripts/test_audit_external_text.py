from __future__ import annotations

import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit_external_text import audit_text  # noqa: E402


class AudienceLeakageAuditTests(unittest.TestCase):
    def test_clean_state_artifact_passes(self) -> None:
        text = "# Example\n\nThis service stores local data in SQLite.\n"
        self.assertEqual([], audit_text(text, "state"))

    def test_reader_relevant_limitation_passes(self) -> None:
        text = "## Compatibility\n\nWindows is not supported. Use Linux or macOS.\n"
        self.assertEqual([], audit_text(text, "state"))

    def test_task_process_leak_is_an_error_in_state_mode(self) -> None:
        text = "# Example\n\n按照你的要求，我们已经删除了旧组件。\n"
        findings = audit_text(text, "state")
        self.assertGreaterEqual(sum(item.severity == "error" for item in findings), 2)

    def test_project_history_belongs_in_change_mode(self) -> None:
        text = "# Release notes\n\nVersion 2 replaced the legacy endpoint with `/v2/items`.\n"
        self.assertEqual([], audit_text(text, "change"))

    def test_request_acknowledgement_belongs_in_direct_mode(self) -> None:
        text = "As you requested, I have updated the deployment guide.\n"
        self.assertEqual([], audit_text(text, "direct"))

    def test_hidden_chat_context_fails_in_pr_text(self) -> None:
        text = "As we discussed earlier in our chat, this changes the parser.\n"
        findings = audit_text(text, "change")
        self.assertEqual(["HIDDEN_CONVERSATION"], [item.rule_id for item in findings])

    def test_migration_section_allows_past_state_inside_state_document(self) -> None:
        text = "# Guide\n\n## Migration\n\nPreviously, the setting was named `old_key`.\n"
        self.assertEqual([], audit_text(text, "state"))

    def test_fenced_example_is_not_artifact_narration(self) -> None:
        text = "# Rules\n\n```text\nAs you requested, we changed the value.\n```\n"
        self.assertEqual([], audit_text(text, "state"))

    def test_process_heading_is_flagged_only_in_state_mode(self) -> None:
        state_findings = audit_text("# What We Changed\n\nCurrent behavior.\n", "state")
        change_findings = audit_text("# What We Changed\n\nCurrent behavior.\n", "change")
        self.assertEqual(["PROCESS_HEADING"], [item.rule_id for item in state_findings])
        self.assertEqual([], change_findings)


if __name__ == "__main__":
    unittest.main()

