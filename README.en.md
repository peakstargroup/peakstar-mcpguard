<div align="center">

# MCPGuard

### Scan for security holes before your AI agent touches company systems

**MCP / Agent security scan ｜ Zero dependencies ｜ Static, runs locally, sends nothing out ｜ One board-ready report**

[繁體中文](README.md) ｜ [English](README.en.md)

`Python 3.11+` ｜ `MIT License` ｜ `0 dependencies` ｜ by [Peakstar](https://www.peakstargroup.com)

</div>

> Status: **skeleton (spec milestone M0)**. Config parsing, the rule engine,
> five-dimension scoring and the report run end to end offline. The CVE data is a
> small built-in snapshot; the `--update-cve` feed and the regulated-industry pro
> rule pack are extension points.

---

## Why scan now

Agent adoption is fast; governance is slow. The moment your agent connects to ERP,
accounting, or customer data, the risk begins: prompt injection, tool poisoning,
unauthenticated endpoints, over-broad permissions, runaway cost. 2026 already saw
30+ MCP-related CVEs, including CVE-2025-6514 (CVSS 9.6) affecting hundreds of
thousands of environments.

Most SMEs lack security staff and **cannot see how exposed they are.** MCPGuard
makes that visible.

```bash
mcpguard scan
```

Open `report.html` and you get:

- **A 0 to 100 agent security score** with a red / yellow / green light (stricter thresholds for a security tool)
- **A five-dimension scorecard**: AuthN/Z, prompt injection / tool poisoning, supply chain, action risk / human approval, cost & audit
- **A list of top findings**, each explaining what it is, why it is dangerous, and the matching real incident or CVE

Any critical finding forces the score into the red and to the top of the report.

---

## Usage

```bash
mcpguard scan [PATH] [options]      # omit PATH to auto-detect common config locations
mcpguard list-rules                 # list active rules
```

| Option | Description | Default |
|--------|-------------|---------|
| `--out <dir>` | Report output directory | `./mcpguard-report` |
| `--lang zh\|en` | Report language | `zh` |
| `--severity-min low\|med\|high` | Minimum severity to show | low |
| `--fail-on high\|critical` | Non-zero exit on a hit (for CI) | off |
| `--open` | Open the report when done | off |

Example (offline, with bundled samples):

```bash
mcpguard scan examples/dangerous --open      # dangerous config, comes out red
mcpguard scan examples/safe                  # safe config, comes out green
```

---

## Responsibility boundary (please read)

- This is a **static-scan diagnostic aid, not a full security audit**, and is not a guarantee.
- The report **discloses risk and why it is dangerous; it does not provide directly exploitable techniques or payloads**.
- False positives erode trust and false negatives are worse, so wording is conservative and every finding carries a "why" and evidence.
- CVE data is a built-in snapshot whose date is shown in the report; unknown config formats are marked "unparsed" rather than erroring.

---

## What it does, and what it deliberately does not

**MCPGuard does:** static-scan your MCP / Agent configuration and produce a security scorecard with top findings.

**MCPGuard deliberately does not:** modify configs, auto-remediate, run dynamic / penetration testing, or build least-privilege architecture, OAuth, audit / sandbox, or compliance frameworks for you.

Diagnosis can be automated; treatment cannot. Advanced compliance rule packs and architecture delivery for regulated industries (finance, healthcare, public relations, government) are provided by Peakstar per engagement, not bundled in this open-source repo.

---

## Develop and test

```bash
py -m unittest discover -s tests -t .
```

The shared report look comes from [peakstar-oss-common](https://github.com/peakstargroup/peakstar-oss-common), vendored under `peakstar_mcpguard/_vendor/` so this tool stays dependency-free. Run `py scripts/sync_common.py` after updating the shared base.

---

## License

MIT. See [LICENSE](LICENSE).

## About Peakstar

Peakstar is an AI consulting and engineering delivery firm focused on SME digital transformation in Taiwan and Japan. Business value first, honesty over promises.
[www.peakstargroup.com](https://www.peakstargroup.com)
