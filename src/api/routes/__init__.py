"""
API Routes Module

Organized route handlers for the ALCHEMY API.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, File, UploadFile
from typing import Optional, List
from datetime import datetime
import uuid
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create routers
processing_router = APIRouter(prefix="/api/v1/processing", tags=["Processing"])
jobs_router = APIRouter(prefix="/api/v1/jobs", tags=["Jobs"])
packages_router = APIRouter(prefix="/api/v1/packages", tags=["Packages"])
health_router = APIRouter(prefix="/health", tags=["Health"])

# Import models (will be imported from main in production)
# from src.api.main import JobStatus, ProcessFileResponse, PackageResponse, HealthResponse

# Global state (in production, use database)
processing_jobs = {}
packages = {}


# Processing routes
@processing_router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="File to process (PDF, TXT, HTML)")
):
    """
    Upload and process a file.

    This endpoint accepts a file upload and processes it through the
    complete Archaeologist agent workflow.
    """
    # Validate file format
    file_ext = os.path.splitext(file.filename)[1].lower()
    supported_extensions = ['.pdf', '.txt', '.html', '.htm']

    if file_ext not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Supported formats: {', '.join(supported_extensions)}"
        )

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Create job directory
    job_dir = f"raw_ore/{job_id}"
    os.makedirs(job_dir, exist_ok=True)

    # Save uploaded file
    file_path = f"{job_dir}/{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    # Create job record
    processing_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "file_path": file_path,
        "file_name": file.filename,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "processing_time": None,
        "error_message": None,
        "package_id": None
    }

    # Add background task for processing
    background_tasks.add_task(process_file_background, job_id, file_path)

    logger.info(f"Created processing job {job_id} for file {file.filename}")

    return {
        "job_id": job_id,
        "status": "pending",
        "message": f"File processing started. Use job_id {job_id} to track progress.",
        "created_at": processing_jobs[job_id]["created_at"]
    }


# Background processing function
async def process_file_background(job_id: str, file_path: str):
    """
    Background task to process a file.

    Args:
        job_id: Unique job identifier
        file_path: Path to the file to process
    """
    try:
        # Update job status
        processing_jobs[job_id]["status"] = "processing"
        processing_jobs[job_id]["updated_at"] = datetime.utcnow().isoformat()

        logger.info(f"Starting background processing for job {job_id}")

        # Import Archaeologist agent
        from src.agents.archaeologist import ArchaeologistAgent

        # Initialize agent
        agent = ArchaeologistAgent()

        # Process file
        result = agent.process_file(file_path)

        # Update job status based on result
        if result["success"]:
            processing_jobs[job_id]["status"] = "completed"
            processing_jobs[job_id]["processing_time"] = result["processing_time"]

            # Store package
            package_id = result["package"]["package_id"]
            packages[package_id] = result["package"]
            processing_jobs[job_id]["package_id"] = package_id

            logger.info(f"Job {job_id} completed successfully in {result['processing_time']:.2f}s")
        else:
            processing_jobs[job_id]["status"] = "failed"
            processing_jobs[job_id]["error_message"] = str(result["errors"])
            processing_jobs[job_id]["processing_time"] = result["processing_time"]

            logger.error(f"Job {job_id} failed: {result['errors']}")

        processing_jobs[job_id]["updated_at"] = datetime.utcnow().isoformat()

    except Exception as e:
        # Update job status with error
        processing_jobs[job_id]["status"] = "failed"
        processing_jobs[job_id]["error_message"] = str(e)
        processing_jobs[job_id]["updated_at"] = datetime.utcnow().isoformat()

        logger.error(f"Job {job_id} encountered error: {str(e)}")


# Jobs routes
@jobs_router.get("/{job_id}")
async def get_job(job_id: str):
    """
    Get the status of a processing job.
    """
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return processing_jobs[job_id]


@jobs_router.get("/")
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 50
):
    """
    List all processing jobs.
    """
    jobs = list(processing_jobs.values())

    # Filter by status if provided
    if status:
        jobs = [job for job in jobs if job["status"] == status]

    # Sort by created_at (newest first)
    jobs.sort(key=lambda x: x["created_at"], reverse=True)

    # Limit results
    jobs = jobs[:limit]

    return jobs


@jobs_router.delete("/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a processing job.
    """
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    # Delete job
    del processing_jobs[job_id]

    logger.info(f"Deleted job {job_id}")

    return {"message": f"Job {job_id} deleted successfully"}


# Packages routes
@packages_router.get("/{package_id}")
async def get_package(package_id: str):
    """
    Get a processed package by ID.
    """
    if package_id not in packages:
        raise HTTPException(status_code=404, detail=f"Package {package_id} not found")

    return packages[package_id]


@packages_router.get("/")
async def list_packages(limit: int = 50):
    """
    List all processed packages.
    """
    package_list = list(packages.values())

    # Sort by timestamp (newest first)
    package_list.sort(key=lambda x: x["timestamp"], reverse=True)

    # Limit results
    package_list = package_list[:limit]

    return package_list


@packages_router.delete("/{package_id}")
async def delete_package(package_id: str):
    """
    Delete a processed package.
    """
    if package_id not in packages:
        raise HTTPException(status_code=404, detail=f"Package {package_id} not found")

    # Delete package
    del packages[package_id]

    logger.info(f"Deleted package {package_id}")

    return {"message": f"Package {package_id} deleted successfully"}


# Health routes
@health_router.get("/")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": 0.0  # TODO: Implement actual uptime tracking
    }
