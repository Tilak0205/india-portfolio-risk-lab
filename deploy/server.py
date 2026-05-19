"""India Portfolio Risk Lab — FastAPI backend for Jetro deploy."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from yfinance import Ticker, download

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
DATA_DIR = Path(os.environ.get("JET_DATA_DIR", "/app/data"))
if not DATA_DIR.exists():
    DATA_DIR = APP_DIR.parent

PORTFOLIO_PATH = DATA_DIR / "portfolio.json"
CACHE_TTL_SEC = 45
_cache: dict[str, tuple[float, Any]] = {}

app = FastAPI(title="India Portfolio Risk Lab", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _cached(key: str, factory):
    now = time.time()
    if key in _cache and now - _cache[key][0] < CACHE_TTL_SEC:
        return _cache[key][1]
    value = factory()
    _cache[key] = (now, value)
    return value


def load_portfolio() -> dict:
    if not PORTFOLIO_PATH.exists():
        raise HTTPException(404, f"portfolio.json not found at {PORTFOLIO_PATH}")
    return json.loads(PORTFOLIO_PATH.read_text())


def _quote(ticker: str) -> dict:
    t = Ticker(ticker)
    fi = t.fast_info
    last = float(fi.get("last_price") or fi.get("lastPrice") or 0)
    prev = float(fi.get("previous_close") or fi.get("previousClose") or last)
    chg_pct = ((last - prev) / prev * 100) if prev else 0.0
    return {"ticker": ticker, "last": last, "previousClose": prev, "changePct": round(chg_pct, 2)}


def _history_normalized(ticker: str, period: str = "6mo") -> pd.Series:
    df = download(ticker, period=period, progress=False, auto_adjust=True)
    if df is None or df.empty:
        return pd.Series(dtype=float)
    close = df["Close"] if "Close" in df.columns else df.iloc[:, 0]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return close.dropna().astype(float)


@app.get("/api/health")
def health():
    return {"ok": True, "asOf": datetime.now(timezone.utc).isoformat()}


@app.get("/api/holdings")
def holdings():
    def build():
        p = load_portfolio()
        rows = []
        for h in p["holdings"]:
            q = _quote(h["ticker"])
            rows.append(
                {
                    "ticker": h["ticker"],
                    "name": h["name"],
                    "sector": h["sector"],
                    "weight": h["weight"],
                    "weightPct": round(h["weight"] * 100, 1),
                    "lastPrice": q["last"],
                    "changePct": q["changePct"],
                    "dayPnlPct": round(q["changePct"] * h["weight"], 3),
                }
            )
        return {"holdings": rows, "currency": p.get("currency", "INR")}

    return _cached("holdings", build)


@app.get("/api/summary")
def summary():
    def build():
        p = load_portfolio()
        h = holdings()["holdings"]
        port_day = sum(x["dayPnlPct"] for x in h)
        bench = _quote(p["benchmark"])
        return {
            "portfolioName": p["name"],
            "benchmark": p["benchmark"],
            "benchmarkLabel": p.get("benchmarkLabel", "NIFTY 50"),
            "currency": p.get("currency", "INR"),
            "holdingCount": len(h),
            "portfolioDayChangePct": round(port_day, 2),
            "benchmarkDayChangePct": bench["changePct"],
            "vsBenchmarkDayPct": round(port_day - bench["changePct"], 2),
            "asOf": datetime.now(timezone.utc).isoformat(),
        }

    return _cached("summary", build)


@app.get("/api/sector-allocation")
def sector_allocation():
    def build():
        p = load_portfolio()
        sectors: dict[str, float] = {}
        for h in p["holdings"]:
            sectors[h["sector"]] = sectors.get(h["sector"], 0) + h["weight"]
        items = [
            {"sector": k, "weight": v, "weightPct": round(v * 100, 1)}
            for k, v in sorted(sectors.items(), key=lambda x: -x[1])
        ]
        return {"sectors": items}

    return _cached("sector-allocation", build)


@app.get("/api/performance")
def performance(benchmark: str | None = None):
    def build():
        p = load_portfolio()
        bench_ticker = benchmark or p["benchmark"]
        period = "6mo"
        series_map: dict[str, pd.Series] = {}
        weights = {h["ticker"]: h["weight"] for h in p["holdings"]}

        for ticker in weights:
            s = _history_normalized(ticker, period)
            if not s.empty:
                series_map[ticker] = s / float(s.iloc[0])

        if not series_map:
            return {"dates": [], "portfolio": [], "benchmark": [], "benchmarkLabel": bench_ticker}

        aligned = pd.DataFrame(series_map).dropna(how="any")
        port_index = (aligned * pd.Series(weights)).sum(axis=1)
        port_index = port_index / port_index.iloc[0]

        bench = _history_normalized(bench_ticker, period)
        bench = bench.reindex(aligned.index).dropna()
        bench_norm = bench / float(bench.iloc[0]) if len(bench) else bench

        common = port_index.index.intersection(bench_norm.index)
        port_index = port_index.loc[common]
        bench_norm = bench_norm.loc[common]

        dates = [d.strftime("%Y-%m-%d") for d in common]
        return {
            "dates": dates,
            "portfolio": [round(float(x), 4) for x in port_index.tolist()],
            "benchmark": [round(float(x), 4) for x in bench_norm.tolist()],
            "benchmarkTicker": bench_ticker,
            "benchmarkLabel": p.get("benchmarkLabel", "NIFTY 50")
            if bench_ticker == p["benchmark"]
            else bench_ticker,
        }

    return _cached(f"performance-{benchmark or 'default'}", build)


@app.get("/api/risk-metrics")
def risk_metrics():
    def build():
        p = load_portfolio()
        weights = sorted([h["weight"] for h in p["holdings"]], reverse=True)
        top1 = weights[0] if weights else 0
        top3 = sum(weights[:3])
        hhi = sum(w * w for w in weights)
        perf = performance()
        port = pd.Series(perf["portfolio"], dtype=float)
        bench = pd.Series(perf["benchmark"], dtype=float)
        n = min(len(port), len(bench))
        if n > 5:
            port, bench = port.iloc[-n:], bench.iloc[-n:]
            dd_port = float(((port / port.cummax()) - 1).min() * 100)
            dd_bench = float(((bench / bench.cummax()) - 1).min() * 100)
            vol_port = float(port.pct_change().dropna().std() * (252**0.5) * 100)
        else:
            dd_port = dd_bench = vol_port = 0.0

        sectors = sector_allocation()["sectors"]
        max_sector = sectors[0] if sectors else {"sector": "-", "weightPct": 0}

        return {
            "topHoldingWeightPct": round(top1 * 100, 1),
            "top3ConcentrationPct": round(top3 * 100, 1),
            "herfindahlIndex": round(hhi, 4),
            "maxSector": max_sector["sector"],
            "maxSectorWeightPct": max_sector["weightPct"],
            "maxDrawdown6mPct": round(dd_port, 2),
            "benchmarkMaxDrawdown6mPct": round(dd_bench, 2),
            "annualizedVolatilityPct": round(vol_port, 2),
            "interpretation": (
                "Concentration is moderate; IT and Financials are the largest sector buckets. "
                "6M drawdown compares portfolio vs benchmark on a normalized index basis."
            ),
        }

    return _cached("risk-metrics", build)


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
