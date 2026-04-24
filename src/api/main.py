"""
FastAPI Main Application for ALCHEMY

REST API for the Temporal Content Transmuter system.
Provides endpoints for file processing, job management, and package retrieval.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="ALCHEMY - Temporal Content Transmuter",
    description="Autonomous multi-agent pipeline converting legacy content into modern digital assets",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state (in production, use database)
processing_jobs = {}
packages = {}


# Pydantic models for request/response
class JobStatus(BaseModel):
    """Job status response model"""
    job_id: str
    status: str
    file_path: Optional[str] = None
    created_at: str
    updated_at: str
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    package_id: Optional[str] = None


class ProcessFileResponse(BaseModel):
    """Process file response model"""
    job_id: str
    status: str
    message: str
    created_at: str


class PackageResponse(BaseModel):
    """Package response model"""
    package_id: str
    version: str
    source_agent: str
    target_agent: str
    timestamp: str
    metadata: Dict[str, Any]
    content: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]
    quality: Dict[str, Any]
    handoff: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    version: str
    timestamp: str
    uptime: float


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting ALCHEMY API server")
    logger.info(f"FastAPI version: {app.version}")
    logger.info("Documentation available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down ALCHEMY API server")


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns the current status of the API server.
    """
    return HealthResponse(
        status="healthy",
        version=app.version,
        timestamp=datetime.utcnow().isoformat(),
        uptime=0.0  # TODO: Implement actual uptime tracking
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "ALCHEMY - Temporal Content Transmuter",
        "version": app.version,
        "status": "running",
        "documentation": "/docs",
        "health": "/health"
    }


# Process file endpoint
@app.post("/api/v1/process", response_model=ProcessFileResponse, tags=["Processing"])
async def process_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="File to process (PDF, TXT, HTML)")
):
    """
    Process a file through the Archaeologist workflow.

    This endpoint accepts a file upload and processes it through the
    complete Archaeologist agent workflow. Processing happens in the
    background, and a job ID is returned for tracking.

    Supported file formats: PDF, TXT, HTML
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

    return ProcessFileResponse(
        job_id=job_id,
        status="pending",
        message=f"File processing started. Use job_id {job_id} to track progress.",
        created_at=processing_jobs[job_id]["created_at"]
    )


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

        # Import Archaeologist agent (import here to avoid circular imports)
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


# Get job status endpoint
@app.get("/api/v1/jobs/{job_id}", response_model=JobStatus, tags=["Jobs"])
async def get_job_status(job_id: str):
    """
    Get the status of a processing job.

    Args:
        job_id: Unique job identifier

    Returns:
        Job status information
    """
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job = processing_jobs[job_id]

    return JobStatus(
        job_id=job["job_id"],
        status=job["status"],
        file_path=job.get("file_path"),
        created_at=job["created_at"],
        updated_at=job["updated_at"],
        processing_time=job.get("processing_time"),
        error_message=job.get("error_message"),
        package_id=job.get("package_id")
    )


# List all jobs endpoint
@app.get("/api/v1/jobs", response_model=List[JobStatus], tags=["Jobs"])
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 50
):
    """
    List all processing jobs.

    Args:
        status: Filter by status (optional)
        limit: Maximum number of jobs to return (default: 50)

    Returns:
        List of job statuses
    """
    jobs = list(processing_jobs.values())

    # Filter by status if provided
    if status:
        jobs = [job for job in jobs if job["status"] == status]

    # Sort by created_at (newest first)
    jobs.sort(key=lambda x: x["created_at"], reverse=True)

    # Limit results
    jobs = jobs[:limit]

    return [
        JobStatus(
            job_id=job["job_id"],
            status=job["status"],
            file_path=job.get("file_path"),
            created_at=job["created_at"],
            updated_at=job["updated_at"],
            processing_time=job.get("processing_time"),
            error_message=job.get("error_message"),
            package_id=job.get("package_id")
        )
        for job in jobs
    ]


# Get package endpoint
@app.get("/api/v1/packages/{package_id}", response_model=PackageResponse, tags=["Packages"])
async def get_package(package_id: str):
    """
    Get a processed package by ID.

    Args:
        package_id: Unique package identifier

    Returns:
        Package data with content, tables, and metadata
    """
    if package_id not in packages:
        raise HTTPException(status_code=404, detail=f"Package {package_id} not found")

    package = packages[package_id]

    return PackageResponse(
        package_id=package["package_id"],
        version=package["version"],
        source_agent=package["source_agent"],
        target_agent=package["target_agent"],
        timestamp=package["timestamp"],
        metadata=package["metadata"],
        content=package["content"],
        tables=package["tables"],
        quality=package["quality"],
        handoff=package["handoff"]
    )


# List all packages endpoint
@app.get("/api/v1/packages", response_model=List[PackageResponse], tags=["Packages"])
async def list_packages(limit: int = 50):
    """
    List all processed packages.

    Args:
        limit: Maximum number of packages to return (default: 50)

    Returns:
        List of packages
    """
    package_list = list(packages.values())

    # Sort by timestamp (newest first)
    package_list.sort(key=lambda x: x["timestamp"], reverse=True)

    # Limit results
    package_list = package_list[:limit]

    return [
        PackageResponse(
            package_id=package["package_id"],
            version=package["version"],
            source_agent=package["source_agent"],
            target_agent=package["target_agent"],
            timestamp=package["timestamp"],
            metadata=package["metadata"],
            content=package["content"],
            tables=package["tables"],
            quality=package["quality"],
            handoff=package["handoff"]
        )
        for package in package_list
    ]


# Delete job endpoint
@app.delete("/api/v1/jobs/{job_id}", tags=["Jobs"])
async def delete_job(job_id: str):
    """
    Delete a processing job.

    Args:
        job_id: Unique job identifier

    Returns:
        Deletion confirmation
    """
    if job_id not in processing_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    # Delete job
    del processing_jobs[job_id]

    logger.info(f"Deleted job {job_id}")

    return {"message": f"Job {job_id} deleted successfully"}


# Delete package endpoint
@app.delete("/api/v1/packages/{package_id}", tags=["Packages"])
async def delete_package(package_id: str):
    """
    Delete a processed package.

    Args:
        package_id: Unique package identifier

    Returns:
        Deletion confirmation
    """
    if package_id not in packages:
        raise HTTPException(status_code=404, detail=f"Package {package_id} not found")

    # Delete package
    del packages[package_id]

    logger.info(f"Deleted package {package_id}")

    return {"message": f"Package {package_id} deleted successfully"}


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
