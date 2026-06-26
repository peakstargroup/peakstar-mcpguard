"""MCPGuard 測試（stdlib unittest，零相依）。"""

import json
import tempfile
import unittest
from pathlib import Path

from peakstar_mcpguard import analyze, parse, report as report_mod, rulepack

ROOT = Path(__file__).resolve().parents[1]
SAFE = ROOT / "examples" / "safe" / "mcp.json"
DANGEROUS = ROOT / "examples" / "dangerous" / "mcp.json"


def _ctx():
    return {"cve": rulepack.load_cve(), "ruleset": "basic"}


def _scan(path):
    servers, warnings = parse.parse_config(path)
    return analyze.build_report(servers, rulepack.load_rules("basic"), _ctx(), warnings=warnings)


class TestParse(unittest.TestCase):
    def test_safe_parses_two_servers(self):
        servers, warnings = parse.parse_config(SAFE)
        self.assertEqual(len(servers), 2)
        self.assertEqual(warnings, [])
        docs = next(s for s in servers if s.name == "internal-docs")
        self.assertEqual(docs.transport, "remote")
        self.assertTrue(docs.auth)

    def test_unknown_format_warns_not_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.json"
            p.write_text('{"unrelated": true}', encoding="utf-8")
            servers, warnings = parse.parse_config(p)
            self.assertEqual(servers, [])
            self.assertTrue(warnings)


class TestSeparation(unittest.TestCase):
    def test_safe_is_green_no_critical(self):
        rep = _scan(SAFE)
        self.assertEqual(rep.critical_count, 0)
        self.assertEqual(rep.light, "green")

    def test_dangerous_is_red_with_critical(self):
        rep = _scan(DANGEROUS)
        self.assertEqual(rep.light, "red")
        self.assertGreater(rep.critical_count, 0)

    def test_dangerous_flags_expected_rules(self):
        rep = _scan(DANGEROUS)
        ids = {f.rule.id for f in rep.findings}
        for expected in ("AUTH_UNVERIFIED_REMOTE", "SUPPLY_KNOWN_CVE",
                         "ACTION_AUTO_APPROVE_DESTRUCTIVE"):
            self.assertIn(expected, ids)


class TestThresholds(unittest.TestCase):
    def test_strict_thresholds(self):
        self.assertEqual(analyze._light(90), "green")
        self.assertEqual(analyze._light(70), "yellow")
        self.assertEqual(analyze._light(50), "red")

    def test_weights_sum_to_one(self):
        self.assertAlmostEqual(sum(analyze.WEIGHTS.values()), 1.0, places=6)


class TestReportOutputs(unittest.TestCase):
    def test_html_json(self):
        rep = _scan(DANGEROUS)
        with tempfile.TemporaryDirectory() as d:
            written = report_mod.write_reports(rep, Path(d), ["html", "json"], "zh")
            self.assertEqual(len(written), 2)
            html_txt = (Path(d) / "report.html").read_text(encoding="utf-8")
            json_txt = (Path(d) / "report.json").read_text(encoding="utf-8")
            self.assertNotIn("—", html_txt)
            self.assertIn("peakstargroup.com/?ref=mcpguard", html_txt)
            data = json.loads(json_txt)
            self.assertEqual(data["tool"], "mcpguard")
            self.assertEqual(len(data["dimensions"]), 5)
            self.assertIn("consult_url", data)

    def test_english(self):
        rep = _scan(DANGEROUS)
        html_txt = report_mod.to_html(rep, "en")
        self.assertIn("MCP / Agent Security Scan", html_txt)
        self.assertNotIn("—", html_txt)


if __name__ == "__main__":
    unittest.main()
