"""Vercel entrypoint — re-exports the FastAPI app from deploy/."""
from deploy.server import app  # noqa: F401
