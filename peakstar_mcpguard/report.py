"""把 MCPGuard 的掃描結果轉成共用報告並渲染（共用底座見 _vendor/）。

本檔把領域結果（analyze.Report，含雙語規則文本）翻成共用 ReportDoc。HTML / JSON /
終端格式由 peakstar_oss_common 提供。文案不使用 em-dash。
"""

from __future__ import annotations

import time
from pathlib import Path

from . import analyze, i18n
from ._vendor.peakstar_oss_common import render as common_render
from ._vendor.peakstar_oss_common.model import Cta, Dimension, Finding, ReportDoc, Stat

TOOL = "mcpguard"


def _version() -> str:
    from . import __version__
    return __version__


def _finding_text(f: analyze.Finding, lang: str) -> str:
    base = f"{f.rule.text(lang)}（{f.server}）：{f.rule.why_text(lang)}" if lang == "zh" \
        else f"{f.rule.text(lang)} ({f.server}): {f.rule.why_text(lang)}"
    if f.rule.ref:
        base += f" [{f.rule.ref}]"
    return base


def _build_doc(report: analyze.Report, lang: str) -> ReportDoc:
    ui = i18n.UI[lang]
    names = i18n.DIM_NAMES[lang]
    descs = i18n.DIM_DESC[lang]

    dimensions = [
        Dimension(key=d.key, name=names[d.key], desc=descs[d.key], score=d.score)
        for d in report.dimensions
    ]
    findings = [
        Finding(severity=f.severity, text=_finding_text(f, lang))
        for f in report.findings
    ]
    meta = [
        (ui["servers_label"], str(report.server_count)),
        (ui["cve_label"], report.cve_date or "n/a"),
        (ui["generated"], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
    ]
    cta = Cta(
        title=ui["cta_title"],
        body=i18n.CTA_BODY[lang][report.light],
        button=i18n.CTA_BUTTON[lang],
        url=i18n.consult_url(TOOL, report.light),
    )
    extra = {
        "critical_count": report.critical_count,
        "high_count": report.high_count,
        "medium_count": report.medium_count,
        "low_count": report.low_count,
        "server_count": report.server_count,
        "cve_date": report.cve_date,
        "warnings": report.warnings,
        "dimension_weights": {d.key: d.weight for d in report.dimensions},
        "findings": [
            {"id": f.rule.id, "severity": f.severity, "category": f.category,
             "server": f.server, "detail": f.detail, "ref": f.rule.ref}
            for f in report.findings
        ],
        "stats": report.stats,
    }

    return ReportDoc(
        tool=TOOL,
        version=_version(),
        lang=lang,
        title=ui["title"],
        subtitle=ui["subtitle"],
        total_score=report.total_score,
        light_word=i18n.LIGHT_WORD[lang][report.light],
        score_caption=ui["total"],
        dimensions=dimensions,
        dimensions_heading=ui["dimensions"],
        findings=findings,
        findings_heading=ui["findings"],
        no_findings_text=ui["no_findings"],
        means_heading=ui["means"],
        means_stat=Stat(value=str(report.critical_count), label=ui["risk_label"]),
        means_rows=[(ui["high_label"], str(report.high_count)),
                    (ui["medium_label"], str(report.medium_count))],
        cta=cta,
        disclaimer=ui["disclaimer"],
        about=ui["about"],
        meta=meta,
        green_min=analyze.GREEN_MIN,
        yellow_min=analyze.YELLOW_MIN,
        extra=extra,
    )


def to_html(report: analyze.Report, lang: str = "zh") -> str:
    return common_render.to_html(_build_doc(report, lang))


def to_json(report: analyze.Report, lang: str = "zh") -> str:
    return common_render.to_json(_build_doc(report, lang))


def terminal_summary(report: analyze.Report, lang: str = "zh") -> str:
    return common_render.terminal_summary(_build_doc(report, lang))


def write_reports(report: analyze.Report, out_dir: Path, formats: list[str], lang: str) -> list[Path]:
    return common_render.write_reports(_build_doc(report, lang), out_dir, formats)
