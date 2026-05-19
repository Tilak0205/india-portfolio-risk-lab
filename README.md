# India Portfolio Risk Lab

Sample NSE equity portfolio dashboard vs **NIFTY 50** — built for a Berrywise / Jetro application demo.

**Live demo:** https://india-portfolio-risk-lab.vercel.app

## Stack

- **API:** Python FastAPI, [yfinance](https://github.com/ranaroussi/yfinance) for NSE prices
- **UI:** Vanilla JavaScript + Chart.js
- **Deploy:** [Vercel](https://vercel.com) (FastAPI)

## Run locally

```bash
cd deploy
docker build -t india-portfolio-risk-lab .
docker run --rm -p 8000:8000 -v "$(pwd)/..:/app/data" india-portfolio-risk-lab
```

Open http://127.0.0.1:8000

## Deploy (Vercel)

Production deploys **automatically** when you push to `main` (GitHub → Vercel integration).

Manual deploy:

```bash
vercel deploy --prod
```

Uses native [FastAPI on Vercel](https://vercel.com/docs/frameworks/backend/fastapi) (`index.py` → `deploy/server.py`).

## Jetro

Canvas and share links live in the parent Jetro workspace (`berrywise-jetro`).
