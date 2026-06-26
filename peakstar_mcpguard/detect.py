"""自動探測常見 MCP / client 設定檔位置，或載入使用者指定的路徑 / 目錄。

只讀本機檔案、不外送。找不到時回空清單由 CLI 提示，不報錯。
"""

from __future__ import annotations

import os
from pathlib import Path

# 常見設定檔（相對於使用者家目錄）。骨架先涵蓋主流位置，未知格式於 parse 標未解析。
_CANDIDATES = [
    "AppData/Roaming/Claude/claude_desktop_config.json",          # Claude Desktop (Windows)
    "Library/Application Support/Claude/claude_desktop_config.json",  # Claude Desktop (macOS)
    ".cursor/mcp.json",                                            # Cursor
    ".config/mcp/mcp.json",
    ".mcp.json",
    "mcp.json",
]


def discover() -> list[Path]:
    home = Path(os.path.expanduser("~"))
    found = []
    for rel in _CANDIDATES:
        p = home / rel
        if p.is_file():
            found.append(p)
    # 也看當前目錄
    for name in (".mcp.json", "mcp.json"):
        p = Path.cwd() / name
        if p.is_file() and p not in found:
            found.append(p)
    return found


def resolve(path: str | None) -> list[Path]:
    """把使用者輸入（檔案 / 目錄 / None=自動探測）解析成設定檔清單。"""
    if path is None:
        return discover()
    p = Path(path).expanduser()
    if p.is_file():
        return [p]
    if p.is_dir():
        return sorted(p.glob("**/*.json"))
    return []
