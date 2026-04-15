"""
API routes for the Document Analysis Agent.
"""
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import shutil
import os

from app.core.agent import Agent
from app.services.llm import llm
from app.skills.registry import registry
from app.config import UPLOAD_DIR, SUPPORTED_EXTENSIONS

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Document Analysis Agent is running"}


@router.get("/skills")
async def list_skills():
    """List all registered skills — useful for demo visibility."""
    skills = registry.list_skills()
    skill_list = []
    for name, skill in skills.items():
        skill_list.append({
            "name": name,
            "description": skill.description,
            "input_schema": skill.input_schema,
            "output_schema": skill.output_schema,
        })
    return {"total_skills": len(skill_list), "skills": skill_list}


@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    query: str = Form("Summarize this document"),
):
    """
    Main analysis endpoint.
    Upload a PDF, Excel, or CSV file and get structured analysis.
    """
    try:
        # Validate file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Unsupported file type: {ext}",
                    "supported": list(SUPPORTED_EXTENSIONS),
                },
            )

        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run agent
        agent = Agent(llm)
        result = agent.run(file_path, query)

        return result

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )