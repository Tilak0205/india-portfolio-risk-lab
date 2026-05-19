# India Portfolio Risk Lab

Sample NSE equity portfolio dashboard vs **NIFTY 50** — built for a Berrywise / Jetro application demo.

## Stack

- **API:** Python FastAPI, [yfinance](https://github.com/ranaroussi/yfinance) for NSE prices
- **UI:** Vanilla JavaScript + Chart.js
- **Deploy:** Docker (`Dockerfile.cloud` for Render/Railway)

## Run locally

```bash
cd deploy
docker build -t india-portfolio-risk-lab .
docker run --rm -p 8000:8000 -v "$(pwd)/..:/app/data" india-portfolio-risk-lab
```

Open http://127.0.0.1:8000

## Deploy to Render

Connect this repo on [Render](https://render.com) as a **Docker** web service:

- **Root directory:** `.` (repo root)
- **Dockerfile:** `Dockerfile.cloud`

Or use the included `render.yaml` blueprint.

## Jetro

Canvas and share links live in the parent Jetro workspace (`berrywise-jetro`).
