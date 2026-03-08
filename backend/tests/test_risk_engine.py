"""
Tests for the Risk Engine destructive-action rule.
Ensures destructive keywords trigger CRITICAL risk before AI scoring runs.
"""
import unittest
import sys

sys.path.insert(0, ".")
from app.risk_engine import calculate_risk


class TestDestructiveRiskRule(unittest.TestCase):
    def test_destructive_keywords_return_critical(self):
        """
        Input: "Delete all customer records from the production database immediately"
        Expected:
          - Risk Level: CRITICAL
          - Decision: REQUIRE_HUMAN_APPROVAL
          - Auto Execute: False
        Ensures UI displays CRITICAL risk instead of LOW.
        """
        input_text = "Delete all customer records from the production database immediately"
        result = calculate_risk(input_text)

        self.assertEqual(result["risk_level"], "CRITICAL")
        self.assertEqual(result["decision"], "REQUIRE_HUMAN_APPROVAL")
        self.assertFalse(result["auto_execute"])
        self.assertEqual(result["risk_score"], 95)
        self.assertEqual(result["risk"], "critical")
        self.assertTrue(result["requires_human_approval"])

    def test_destructive_rule_overrides_ai_scoring(self):
        """Destructive keywords must trigger immediate return; normal AI scoring must not run."""
        result = calculate_risk("wipe user data from the system")
        self.assertEqual(result["risk_level"], "CRITICAL")
        self.assertEqual(result["decision"], "REQUIRE_HUMAN_APPROVAL")
        self.assertFalse(result["auto_execute"])

    def test_normal_task_no_destructive_keywords(self):
        """Tasks without destructive keywords proceed to normal risk scoring."""
        result = calculate_risk("Summarize the quarterly sales report")
        self.assertIn("decision", result)
        self.assertIn("auto_execute", result)
        self.assertIn("risk_level", result)


if __name__ == "__main__":
    unittest.main()
