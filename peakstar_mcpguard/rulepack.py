"""載入規則包與 CVE 快照。

basic 規則包以 JSON 定義（規格原寫 YAML，本實作改 JSON 以維持零相依純標準庫）。
每條規則：id, category, severity, check（對應 checks.py 的檢查函式名）, 雙語
title / why / risk, ref（對照真實事件或 CVE）。pro 規則庫（受監管產業法遵）不入庫。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent


@dataclass
class Rule:
    id: str
    category: str          # auth | injection | supply_chain | action_risk | cost_audit
    severity: str          # critical | high | medium | low
    check: str
    title: dict            # {"zh":..., "en":...}
    why: dict
    risk: dict
    ref: str = ""

    def text(self, lang: str) -> str:
        return self.title.get(lang, self.title.get("zh", self.id))

    def why_text(self, lang: str) -> str:
        return self.why.get(lang, self.why.get("zh", ""))


def _rule_from_json(d: dict) -> Rule:
    return Rule(
        id=d["id"],
        category=d["category"],
        severity=d["severity"],
        check=d["check"],
        title={"zh": d.get("title_zh", d["id"]), "en": d.get("title_en", d["id"])},
        why={"zh": d.get("why_zh", ""), "en": d.get("why_en", "")},
        risk={"zh": d.get("risk_zh", ""), "en": d.get("risk_en", "")},
        ref=d.get("ref", ""),
    )


def load_rules(ruleset: str = "basic") -> list[Rule]:
    folder = _HERE / "rulepacks" / ruleset
    rules: list[Rule] = []
    if not folder.is_dir():
        return rules
    for fp in sorted(folder.glob("*.json")):
        data = json.loads(fp.read_text(encoding="utf-8"))
        for d in data.get("rules", []):
            rules.append(_rule_from_json(d))
    return rules


def load_cve() -> dict:
    fp = _HERE / "cve" / "snapshot.json"
    if not fp.is_file():
        return {"date": "", "packages": {}}
    return json.loads(fp.read_text(encoding="utf-8"))
