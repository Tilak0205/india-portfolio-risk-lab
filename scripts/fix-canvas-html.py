#!/usr/bin/env python3
"""Rewrite canvas frame HTML (no localhost). Close Jetro Research Board before running."""

from __future__ import annotations

import json
from pathlib import Path

VERCEL = "https://india-portfolio-risk-lab.vercel.app"
CANVAS = Path(__file__).resolve().parents[1] / "canvases" / "india_portfolio_risk_lab.json"


def main() -> None:
    data = json.loads(CANVAS.read_text())
    snapshot = (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"UTF-8\"/>"
        "<style>body{margin:0;padding:20px;font-family:system-ui,sans-serif;background:#0d1117;color:#e6edf3;font-size:13px;line-height:1.45}"
        "h3{margin:0 0 4px;font-size:15px;font-weight:600}.sub{color:#8b949e;font-size:11px;margin-bottom:16px}"
        ".row{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}"
        ".card{flex:1;min-width:110px;background:#161b22;border:1px solid #30363d;border-radius:8px;padding:12px}"
        ".card label{font-size:10px;color:#8b949e;text-transform:uppercase;letter-spacing:.04em;display:block}"
        ".card .v{font-size:17px;font-weight:600;margin-top:6px}.up{color:#3fb950}.down{color:#f85149}"
        "table{width:100%;border-collapse:collapse;font-size:12px;margin-bottom:14px}"
        "th,td{padding:7px 8px;border-bottom:1px solid #30363d;text-align:left}th{color:#8b949e}"
        ".note{color:#8b949e;font-size:11px;border-top:1px solid #30363d;padding-top:12px}"
        ".pill{display:inline-block;font-size:10px;color:#c9a87c;border:1px solid #c9a87c;border-radius:4px;padding:2px 8px;margin-bottom:12px}"
        ".link{color:#58a6ff;text-decoration:none}</style></head><body>"
        "<span class=\"pill\">Berrywise application · Jetro</span>"
        "<h3>Portfolio performance snapshot</h3>"
        "<p class=\"sub\">Sample NSE portfolio vs NIFTY 50 · Illustrative day moves (INR)</p>"
        "<div class=\"row\">"
        "<div class=\"card\"><label>Portfolio (1D)</label><div class=\"v up\">+0.62%</div></div>"
        "<motion class=\"card\"><label>NIFTY 50 (1D)</label><div class=\"v up\">+0.43%</div></div>"
        "<div class=\"card\"><label>Active return</label><div class=\"v up\">+0.19%</div></div></div>"
        "<table><thead><tr><th>Top movers (sample)</th><th>Weight</th><th>Day</th></tr></thead><tbody>"
        "<tr><td>Reliance Industries</td><td>14%</td><td class=\"up\">+0.2%</td></tr>"
        "<tr><td>HDFC Bank</td><td>13%</td><td class=\"down\">-0.0%</td></tr>"
        "<tr><td>Infosys</td><td>12%</td><td class=\"up\">+0.8%</td></tr>"
        "<tr><td>Sun Pharma</td><td>10%</td><td class=\"up\">+2.4%</td></tr></tbody></table>"
        f"<p class=\"note\">Static preview for the Jetro share. For live NSE prices, 6-month charts, sector allocation, and risk metrics, open the "
        f"<a class=\"link\" href=\"{VERCEL}\" target=\"_blank\" rel=\"noopener\">full interactive app</a>.</p>"
        "</body></html>"
    )
    snapshot = snapshot.replace("motion", "div")

    holdings = (
        "<!DOCTYPE html><html><head><style>body{margin:0;padding:16px;font-family:system-ui,sans-serif;background:#0d1117;color:#e6edf3;font-size:12px}"
        "h3{margin:0 0 12px;color:#8b949e}table{width:100%;border-collapse:collapse}"
        "th,td{padding:8px;border-bottom:1px solid #30363d;text-align:left}th{color:#8b949e}"
        ".tag{font-size:10px;color:#8b949e}.foot{color:#8b949e;margin-top:16px;font-size:11px;line-height:1.5}"
        ".link{color:#58a6ff;text-decoration:none}</style></head><body>"
        "<h3>India Core Portfolio</h3><table><tr><th>Name</th><th>Sector</th><th>Weight</th></tr>"
        "<tr><td>Reliance Industries<br><span class='tag'>RELIANCE.NS</span></td><td>Energy</td><td>14%</td></tr>"
        "<tr><td>HDFC Bank</td><td>Financials</td><td>13%</td></tr>"
        "<tr><td>Infosys</td><td>IT</td><td>12%</td></tr>"
        "<tr><td>TCS</td><td>IT</td><td>11%</td></tr>"
        "<tr><td>Sun Pharma</td><td>Pharma</td><td>10%</td></tr>"
        "<tr><td>ITC</td><td>FMCG</td><td>10%</td></tr>"
        "<tr><td>Bharti Airtel</td><td>Telecom</td><td>10%</td></tr>"
        "<tr><td>Kotak Bank</td><td>Financials</td><td>10%</td></tr>"
        "<tr><td>L&amp;T</td><td>Industrials</td><td>10%</td></tr></table>"
        f"<p class=\"foot\">Benchmark: NIFTY 50 (^NSEI). Nine large-cap NSE names. Live demo: "
        f"<a class=\"link\" href=\"{VERCEL}\" target=\"_blank\" rel=\"noopener\">india-portfolio-risk-lab.vercel.app</a></p>"
        "</body></html>"
    )

    for el in data["elements"]:
        if el["id"] == "el-dashboard-frame":
            el["data"]["html"] = snapshot
        elif el["id"] == "el-holdings-table":
            el["data"]["html"] = holdings

    CANVAS.write_text(json.dumps(data, indent=2) + "\n")
    if "127.0.0.1" in CANVAS.read_text():
        raise SystemExit("localhost still in canvas — close Jetro Research Board and rerun")
    print("OK:", CANVAS)


if __name__ == "__main__":
    main()
