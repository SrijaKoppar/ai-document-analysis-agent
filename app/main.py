"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import skills package to trigger registration on startup
import app.skills  # noqa: F401

from app.api.routes import router

app = FastAPI(
    title="Document Analysis Agent",
    description="AI-powered document analysis with reusable agent skills",
    version="1.0.0",
)

# CORS — allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)