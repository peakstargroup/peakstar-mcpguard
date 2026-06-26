"""把各家 MCP / client 設定檔正規化成統一的 Server 模型。

支援主流 mcpServers 字典格式（Claude Desktop / Cursor / 通用）。未知格式標為
未解析而非報錯（規格第 9 節：設定格式多樣，未知標未解析）。所有判斷皆靜態、離線。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

_AUTH_HEADER_KEYS = {"authorization", "x-api-key", "api-key", "apikey", "token"}
_AUTO_APPROVE_KEYS = ("alwaysallow", "autoapprove", "auto_approve", "alwaysAllow", "autoApprove")
_RATE_KEYS = ("ratelimit", "rate_limit", "maxrequests", "max_requests", "budget", "timeout")
_LOG_KEYS = ("logging", "audit", "logfile", "log_file", "logpath")


@dataclass
class Server:
    name: str
    transport: str = "unknown"        # stdio | remote | unknown
    url: str = ""
    command: str = ""
    args: list = field(default_factory=list)
    env: dict = field(default_factory=dict)
    headers: dict = field(default_factory=dict)
    auth: bool = False
    auto_approve: list = field(default_factory=list)
    tools: list = field(default_factory=list)   # 選填 [{name, description}]
    rate_limit: bool = False
    logging: bool = False
    raw: dict = field(default_factory=dict)


def _lower_keys(d: dict) -> dict:
    return {str(k).lower(): v for k, v in d.items()}


def _detect_auth(spec: dict, headers: dict, env: dict) -> bool:
    hk = {k.lower() for k in headers}
    if hk & _AUTH_HEADER_KEYS:
        return True
    ek = {k.lower() for k in env}
    if any("token" in k or "key" in k or "secret" in k for k in ek):
        return True
    low = _lower_keys(spec)
    return bool(low.get("auth") or low.get("authentication"))


def _server_from_spec(name: str, spec: dict) -> Server:
    low = _lower_keys(spec)
    url = low.get("url", "") or ""
    command = low.get("command", "") or ""
    args = low.get("args", []) or []
    env = low.get("env", {}) or {}
    headers = low.get("headers", {}) or {}

    transport = "remote" if url else ("stdio" if command else "unknown")

    auto_approve = []
    for k in _AUTO_APPROVE_KEYS:
        v = spec.get(k)
        if isinstance(v, list):
            auto_approve = v
            break
        if v is True:
            auto_approve = ["*"]
            break

    rate_limit = any(k in low for k in _RATE_KEYS)
    logging_on = any(k in low for k in _LOG_KEYS)
    tools = spec.get("tools", []) if isinstance(spec.get("tools"), list) else []

    return Server(
        name=name,
        transport=transport,
        url=url,
        command=command,
        args=list(args),
        env=dict(env),
        headers=dict(headers),
        auth=_detect_auth(spec, headers, env),
        auto_approve=list(auto_approve),
        tools=tools,
        rate_limit=rate_limit,
        logging=logging_on,
        raw=spec,
    )


def parse_config(path: str | Path) -> tuple[list[Server], list[str]]:
    """回傳 (servers, warnings)。無法解析的部分以 warnings 標示，不丟例外。"""
    p = Path(path)
    warnings: list[str] = []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return [], [f"無法解析 {p.name}：{e}"]

    block = None
    for key in ("mcpServers", "servers", "mcp_servers"):
        if isinstance(data.get(key), dict):
            block = data[key]
            break
    if block is None:
        warnings.append(f"{p.name}: 找不到 mcpServers 區塊，未解析")
        return [], warnings

    servers = []
    for name, spec in block.items():
        if isinstance(spec, dict):
            servers.append(_server_from_spec(name, spec))
        else:
            warnings.append(f"{p.name}: server '{name}' 格式非物件，未解析")
    return servers, warnings
