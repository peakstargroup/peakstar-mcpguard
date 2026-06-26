"""靜態檢查函式：每個 check 看一台 Server 是否命中某風險。

回傳 None 表示未命中；回傳 dict（可空）表示命中，dict 為附帶細節（給報告）。
所有檢查皆靜態、離線、唯讀。措辭與判斷保守（規格第 9 節：誤報傷信任）。
"""

from __future__ import annotations

import re

from .parse import Server

_INJECTION_RE = re.compile(
    r"ignore\s+(?:all\s+|the\s+)?(?:previous|above|prior)\s+instructions"
    r"|disregard\s+(?:all\s+)?(?:previous|prior)"
    r"|忽略(?:前述|以上|先前|所有)"
    r"|無視(?:前述|以上)(?:指令|指示)",
    re.IGNORECASE,
)
_BROAD_ENV_KEY_RE = re.compile(r"(admin|root|master|superuser)", re.IGNORECASE)
_DESTRUCTIVE_RE = re.compile(
    r"(delete|remove|drop|destroy|pay|transfer|wire|refund|send|exec|shell|sudo|rm)",
    re.IGNORECASE,
)
_PKG_VER_RE = re.compile(r"((?:@[\w.-]+/)?[\w.-]+)@([\w.\-]+)")


def remote_no_auth(server: Server, ctx: dict):
    if server.transport == "remote" and not server.auth:
        return {"url": server.url}
    return None


def broad_token(server: Server, ctx: dict):
    for k, v in server.env.items():
        if _BROAD_ENV_KEY_RE.search(str(k)) or str(v).strip() == "*":
            return {"env_key": k}
    for v in server.headers.values():
        if str(v).strip() == "*":
            return {"header": "*"}
    return None


def injection_tool_desc(server: Server, ctx: dict):
    for t in server.tools:
        desc = t.get("description", "") if isinstance(t, dict) else str(t)
        if _INJECTION_RE.search(desc or ""):
            return {"tool": t.get("name", "?") if isinstance(t, dict) else "?"}
    return None


def cve_package(server: Server, ctx: dict):
    cve = (ctx.get("cve") or {}).get("packages", {})
    blob = " ".join([server.command] + [str(a) for a in server.args])
    for pkg, ver in _PKG_VER_RE.findall(blob):
        entries = cve.get(pkg)
        if not entries:
            continue
        for e in entries:
            if ver in e.get("versions", []):
                return {"package": pkg, "version": ver, "cve": e.get("id", "")}
    return None


def unpinned_source(server: Server, ctx: dict):
    blob = " ".join([server.command] + [str(a) for a in server.args])
    if "@latest" in blob:
        return {"reason": "@latest"}
    if re.search(r"curl\s+.*\|\s*(?:sudo\s+)?(?:ba)?sh", blob):
        return {"reason": "curl | sh"}
    return None


def auto_approve_destructive(server: Server, ctx: dict):
    for item in server.auto_approve:
        if item == "*" or _DESTRUCTIVE_RE.search(str(item)):
            return {"action": item}
    return None


def auto_approve_any(server: Server, ctx: dict):
    if server.auto_approve and not auto_approve_destructive(server, ctx):
        return {"count": len(server.auto_approve)}
    return None


def no_rate_limit(server: Server, ctx: dict):
    if server.transport in ("remote", "stdio") and not server.rate_limit:
        return {}
    return None


def no_logging(server: Server, ctx: dict):
    if not server.logging:
        return {}
    return None


REGISTRY = {
    "remote_no_auth": remote_no_auth,
    "broad_token": broad_token,
    "injection_tool_desc": injection_tool_desc,
    "cve_package": cve_package,
    "unpinned_source": unpinned_source,
    "auto_approve_destructive": auto_approve_destructive,
    "auto_approve_any": auto_approve_any,
    "no_rate_limit": no_rate_limit,
    "no_logging": no_logging,
}
