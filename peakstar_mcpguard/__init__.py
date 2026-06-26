"""MCPGuard: MCP / Agent 安全掃描器 (security scanner) by Peakstar.

你的 AI Agent 接上公司系統前，先掃一次有沒有資安破口。對本機 MCP / Agent 設定做
靜態安全掃描，產出 5 維資安計分卡與高危清單，對照 2026 年實際 MCP 安全事件。

本機執行、零外送（不上傳你的設定）。零相依（純標準庫）；共用報告外觀見 _vendor/。

狀態：骨架（skeleton, 對應規格里程碑 M0）。設定解析 + 規則引擎 + 5 維評分 + 報告
可端到端離線跑；CVE 快照為內建小樣本，--update-cve feed 與 pro 法遵規則為擴充點。

責任邊界：本工具為診斷輔助、靜態掃描，非完整資安稽核，不構成安全保證。報告只揭露
風險與「為什麼危險」，不提供可直接利用的 exploit / payload。
"""

__version__ = "0.1.0"
