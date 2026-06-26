"""MCPGuard CLI (argparse, stdlib only).

用法：
    py -m peakstar_mcpguard scan [PATH] [選項]      # 不給 PATH 則自動探測
    py -m peakstar_mcpguard list-rules
    mcpguard scan [PATH] [選項]                      # 安裝後
"""

from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path

from . import __version__, analyze, detect, i18n, parse, report as report_mod, rulepack
from ._vendor.peakstar_oss_common import telemetry


def _ensure_utf8_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="mcpguard",
        description="MCPGuard: MCP / Agent 安全掃描器 by Peakstar。Agent 接上系統前，"
                    "先掃有沒有資安破口。靜態掃描、本機執行、零外送。",
    )
    p.add_argument("--version", action="version", version=f"MCPGuard {__version__}")
    sub = p.add_subparsers(dest="command")

    sc = sub.add_parser("scan", help="掃描 MCP / Agent 設定並產出資安報告")
    sc.add_argument("path", nargs="?", default=None, help="設定檔或目錄（省略則自動探測常見位置）")
    sc.add_argument("--config", default=None, help="同 path，指定設定檔或目錄")
    sc.add_argument("--out", default="./mcpguard-report", help="報告輸出目錄")
    sc.add_argument("--format", default="html,json", help="輸出格式，逗號分隔：html,json")
    sc.add_argument("--lang", default="zh", choices=["zh", "en"], help="報告語言")
    sc.add_argument("--severity-min", default="low", choices=["low", "med", "high"],
                    help="報告顯示的最低嚴重度（不影響評分）")
    sc.add_argument("--fail-on", default=None, choices=["high", "critical"],
                    help="命中該等級即以非零退出碼結束（給 CI 用）")
    sc.add_argument("--open", action="store_true", help="完成後自動開啟 HTML 報告")
    sc.add_argument("--no-telemetry", action="store_true", help="強制關閉遙測（預設本就關閉）")

    sub.add_parser("list-rules", help="列出啟用的 basic 規則")
    return p


def _split(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [v.strip() for v in value.split(",") if v.strip()]


def run_scan(args: argparse.Namespace) -> int:
    targets = detect.resolve(args.path or args.config)
    if not targets:
        print("找不到 MCP / Agent 設定檔。請用 mcpguard scan <路徑> 指定，"
              "或確認常見設定位置存在。", file=sys.stderr)
        return 1

    if not args.no_telemetry:
        telemetry.record("scan_started")

    servers: list[parse.Server] = []
    warnings: list[str] = []
    for fp in targets:
        srvs, warns = parse.parse_config(fp)
        servers.extend(srvs)
        warnings.extend(warns)

    rules = rulepack.load_rules("basic")
    ctx = {"cve": rulepack.load_cve(), "ruleset": "basic"}
    rep = analyze.build_report(servers, rules, ctx, severity_min=args.severity_min,
                               warnings=warnings)

    out_dir = Path(args.out).expanduser()
    formats = _split(args.format) or ["html", "json"]
    written = report_mod.write_reports(rep, out_dir, formats, args.lang)

    print(report_mod.terminal_summary(rep, args.lang))
    print()
    for w in warnings:
        print(f"  (未解析) {w}")
    for p in written:
        print(f"  報告已產生：{p}")
    print(f"\n  關於 MCPGuard 與 Peakstar：{report_mod.i18n.consult_url('mcpguard', rep.light)}")

    if not args.no_telemetry:
        telemetry.record("scan_completed")

    if args.open:
        html_path = out_dir / "report.html"
        if html_path.exists():
            webbrowser.open(html_path.resolve().as_uri())

    if args.fail_on == "critical" and rep.critical_count:
        return 1
    if args.fail_on == "high" and (rep.critical_count or rep.high_count):
        return 1
    return 0


def run_list_rules(lang: str = "zh") -> int:
    rules = rulepack.load_rules("basic")
    print(f"啟用規則（basic，{len(rules)} 條）：")
    for r in sorted(rules, key=lambda x: (x.category, x.severity)):
        print(f"  [{r.severity:<8}] {r.category:<13} {r.id}  {r.text(lang)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    _ensure_utf8_output()
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "scan":
        return run_scan(args)
    if args.command == "list-rules":
        return run_list_rules()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
