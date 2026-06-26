"""評分引擎：規則命中 -> findings -> 5 維資安計分卡 -> 總分 / 燈號。

安全工具採較嚴門檻（規格第 3 節覆寫共用門檻）：綠 >= 85、黃 60..84、紅 < 60。
任一 critical 命中直接把總分壓進紅燈區，並於報告置頂。措辭保守，附「為什麼」。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import checks
from .parse import Server
from .rulepack import Rule

WEIGHTS = {
    "auth": 0.30,
    "injection": 0.25,
    "supply_chain": 0.20,
    "action_risk": 0.15,
    "cost_audit": 0.10,
}

GREEN_MIN = 85
YELLOW_MIN = 60

PENALTY = {"critical": 100, "high": 35, "medium": 20, "low": 10}
_SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
_SEV_MIN_RANK = {"low": 3, "med": 1, "medium": 1, "high": 1}


@dataclass
class Dimension:
    key: str
    score: float
    weight: float


@dataclass
class Finding:
    rule: Rule
    server: str
    severity: str
    category: str
    detail: dict = field(default_factory=dict)


@dataclass
class Report:
    server_count: int
    total_score: float
    light: str
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    dimensions: list[Dimension]
    findings: list[Finding]
    cve_date: str
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


def _light(score: float) -> str:
    if score >= GREEN_MIN:
        return "green"
    if score >= YELLOW_MIN:
        return "yellow"
    return "red"


def build_report(servers: list[Server], rules: list[Rule], ctx: dict,
                 severity_min: str = "low", warnings: list[str] | None = None) -> Report:
    all_findings: list[Finding] = []
    for server in servers:
        for rule in rules:
            fn = checks.REGISTRY.get(rule.check)
            if fn is None:
                continue
            detail = fn(server, ctx)
            if detail is not None:
                all_findings.append(Finding(rule=rule, server=server.name,
                                            severity=rule.severity,
                                            category=rule.category, detail=detail))

    per_cat = {cat: 0 for cat in WEIGHTS}
    for f in all_findings:
        per_cat[f.category] = per_cat.get(f.category, 0) + PENALTY.get(f.severity, 0)

    dims_raw = {cat: max(0.0, 100.0 - per_cat[cat]) for cat in WEIGHTS}
    total = round(sum(dims_raw[c] * w for c, w in WEIGHTS.items()), 1)

    counts = {s: sum(1 for f in all_findings if f.severity == s)
              for s in ("critical", "high", "medium", "low")}
    if counts["critical"]:
        total = min(total, 50.0)   # critical 強制紅燈

    dims = [Dimension(c, round(dims_raw[c], 1), WEIGHTS[c]) for c in WEIGHTS]

    min_rank = _SEV_MIN_RANK.get(severity_min, 3)
    shown = [f for f in all_findings if _SEV_ORDER[f.severity] <= min_rank]
    shown.sort(key=lambda f: _SEV_ORDER[f.severity])

    return Report(
        server_count=len(servers),
        total_score=total,
        light=_light(total),
        critical_count=counts["critical"],
        high_count=counts["high"],
        medium_count=counts["medium"],
        low_count=counts["low"],
        dimensions=dims,
        findings=shown,
        cve_date=(ctx.get("cve") or {}).get("date", ""),
        warnings=warnings or [],
        stats={"servers": len(servers), "findings_total": len(all_findings),
               "ruleset": ctx.get("ruleset", "basic")},
    )
