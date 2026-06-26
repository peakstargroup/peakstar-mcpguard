"""繁中 / English strings for MCPGuard report. 預設繁中。

規則本文（標題 / 為什麼 / 風險）為雙語、放在 rulepacks 內；此處只放 UI 框架字串。
"""

DIM_NAMES = {
    "zh": {
        "auth": "驗證與存取",
        "injection": "提示注入 / 工具投毒抗性",
        "supply_chain": "供應鏈與來源",
        "action_risk": "動作風險 / 人為核可",
        "cost_audit": "成本與稽核",
    },
    "en": {
        "auth": "AuthN / AuthZ",
        "injection": "Prompt injection / tool poisoning",
        "supply_chain": "Supply chain",
        "action_risk": "Action risk / human approval",
        "cost_audit": "Cost & audit",
    },
}

DIM_DESC = {
    "zh": {
        "auth": "端點是否驗證、權限是否最小化",
        "injection": "工具描述 / skill 是否含可被操弄的指令樣式",
        "supply_chain": "skill / server 來源、版本、是否命中已知 CVE",
        "action_risk": "破壞性 / 對外動作是否需人工核可",
        "cost_audit": "有無速率 / 成本上限、有無稽核軌跡",
    },
    "en": {
        "auth": "Whether endpoints authenticate and permissions are least-privilege",
        "injection": "Whether tool descriptions / skills carry manipulable instruction patterns",
        "supply_chain": "Source and version of skills / servers, and known-CVE hits",
        "action_risk": "Whether destructive / outbound actions require human approval",
        "cost_audit": "Rate / cost limits and audit trail",
    },
}

LIGHT_WORD = {
    "zh": {"green": "綠燈", "yellow": "黃燈", "red": "紅燈"},
    "en": {"green": "Green", "yellow": "Yellow", "red": "Red"},
}

UI = {
    "zh": {
        "title": "MCP / Agent 資安掃描報告",
        "subtitle": "你的 AI Agent 接上公司系統前，先掃一次有沒有資安破口",
        "target_label": "掃描標的",
        "servers_label": "伺服器數",
        "cve_label": "CVE 快照",
        "generated": "產生時間",
        "total": "Agent 資安總分",
        "dimensions": "五大資安維度",
        "findings": "高危發現",
        "no_findings": "未發現重大資安破口。但靜態掃描非完整稽核，建議定期重掃。",
        "means": "這代表什麼",
        "risk_label": "偵測到的重大風險項（critical）",
        "high_label": "高危項",
        "medium_label": "中危項",
        "cta_title": "下一步：安全地把 Agent 接上你的系統",
        "disclaimer": "本報告為靜態掃描的診斷輔助，非完整資安稽核，不構成安全保證，且不提供可直接利用的攻擊手法。所有分析皆於本機執行，未上傳任何設定。",
        "about": "Peakstar（品得網絡數位）：AI 顧問與工程交付，專注台灣與日本中小企業數位轉型。",
    },
    "en": {
        "title": "MCP / Agent Security Scan",
        "subtitle": "Scan for security holes before your AI agent touches company systems",
        "target_label": "Scanned",
        "servers_label": "Servers",
        "cve_label": "CVE snapshot",
        "generated": "Generated",
        "total": "Agent Security Score",
        "dimensions": "Five Dimensions",
        "findings": "Top Findings",
        "no_findings": "No critical security holes found. Static scanning is not a full audit; rescan regularly.",
        "means": "What this means",
        "risk_label": "Critical findings detected",
        "high_label": "High",
        "medium_label": "Medium",
        "cta_title": "Next step: connect your agent to your systems safely",
        "disclaimer": "This report is a static-scan diagnostic aid, not a full security audit, is not a guarantee, and does not provide directly exploitable techniques. All analysis runs locally; no configuration is uploaded.",
        "about": "Peakstar: AI consulting and engineering delivery, focused on SME digital transformation in Taiwan and Japan.",
    },
}

CTA_BODY = {
    "zh": {
        "red": "你的 Agent 資安為紅燈，偵測到重大破口。在受監管產業，這些破口可能造成法遵違規與資料外洩。安全地把 Agent 接上系統，需要最小權限、稽核軌跡與在地法遵架構，正是 Peakstar 的治理與整合服務。",
        "yellow": "你的 Agent 資安為黃燈，有明顯可收斂的風險。在擴大 Agent 權限前先補強，能大幅降低外洩與失控風險。需要時歡迎參考 Peakstar 的做法。",
        "green": "你的 Agent 資安為綠燈，基礎良好。下一步是把治理制度化（最小權限、稽核、持續掃描），守住這個分數。",
    },
    "en": {
        "red": "Your agent security is Red, with critical holes detected. In regulated industries these can mean compliance violations and data leaks. Connecting agents safely needs least-privilege, audit trails and local compliance architecture, which is Peakstar's governance and integration work.",
        "yellow": "Your agent security is Yellow, with clearly fixable risks. Hardening before you widen agent permissions sharply lowers leak and runaway risk.",
        "green": "Your agent security is Green, a solid base. The next step is institutionalizing governance (least-privilege, audit, continuous scanning) to hold that score.",
    },
}

CTA_BUTTON = {"zh": "了解 Peakstar 的做法", "en": "How Peakstar approaches this"}


def consult_url(tool: str, light: str) -> str:
    # 單一、低調的來源標記。開源預設版不埋 campaign / 燈號層級追蹤。
    return "https://www.peakstargroup.com/?ref=mcpguard"
