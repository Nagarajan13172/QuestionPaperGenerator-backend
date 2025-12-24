"""
ASGI handler for Vercel deployment
"""
from app.main import app

# Vercel requires this specific variable name
handler = app
