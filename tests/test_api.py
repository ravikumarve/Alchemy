"""
API Tests for ALCHEMY

Tests for FastAPI endpoints including file processing,
job management, and package retrieval.
"""

import os
import sys
import tempfile
import json
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import FastAPI app
from src.api.main import app


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self):
        """Test health check endpoint."""
        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_root_endpoint(self):
        """Test root endpoint."""
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "documentation" in data


class TestProcessingEndpoints:
    """Test file processing endpoints."""

    def test_process_file_success(self):
        """Test successful file processing."""
        client = TestClient(app)

        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document for processing.")
            temp_path = f.name

        try:
            # Upload file
            with open(temp_path, 'rb') as f:
                response = client.post(
                    "/api/v1/process",
                    files={"file": ("test.txt", f, "text/plain")}
                )

            assert response.status_code == 200
            data = response.json()
            assert "job_id" in data
            assert data["status"] == "pending"
            assert "created_at" in data

        finally:
            os.unlink(temp_path)

    def test_process_file_unsupported_format(self):
        """Test processing with unsupported file format."""
        client = TestClient(app)

        # Create temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write("Test content")
            temp_path = f.name

        try:
            # Upload file
            with open(temp_path, 'rb') as f:
                response = client.post(
                    "/api/v1/process",
                    files={"file": ("test.xyz", f, "application/octet-stream")}
                )

            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "Unsupported file format" in data["detail"]

        finally:
            os.unlink(temp_path)


class TestJobEndpoints:
    """Test job management endpoints."""

    def test_get_job_status(self):
        """Test getting job status."""
        client = TestClient(app)

        # First create a job
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_path = f.name

        try:
            # Upload file to create job
            with open(temp_path, 'rb') as f:
                create_response = client.post(
                    "/api/v1/process",
                    files={"file": ("test.txt", f, "text/plain")}
                )

            job_id = create_response.json()["job_id"]

            # Get job status
            response = client.get(f"/api/v1/jobs/{job_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["job_id"] == job_id
            assert "status" in data
            assert "created_at" in data

        finally:
            os.unlink(temp_path)

    def test_get_nonexistent_job(self):
        """Test getting status for nonexistent job."""
        client = TestClient(app)

        response = client.get("/api/v1/jobs/nonexistent-job-id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_list_jobs(self):
        """Test listing all jobs."""
        client = TestClient(app)

        response = client.get("/api/v1/jobs")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_jobs_with_filter(self):
        """Test listing jobs with status filter."""
        client = TestClient(app)

        response = client.get("/api/v1/jobs?status=pending")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_delete_job(self):
        """Test deleting a job."""
        client = TestClient(app)

        # First create a job
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_path = f.name

        try:
            # Upload file to create job
            with open(temp_path, 'rb') as f:
                create_response = client.post(
                    "/api/v1/process",
                    files={"file": ("test.txt", f, "text/plain")}
                )

            job_id = create_response.json()["job_id"]

            # Delete job
            response = client.delete(f"/api/v1/jobs/{job_id}")

            assert response.status_code == 200
            data = response.json()
            assert "message" in data

            # Verify job is deleted
            get_response = client.get(f"/api/v1/jobs/{job_id}")
            assert get_response.status_code == 404

        finally:
            os.unlink(temp_path)


class TestPackageEndpoints:
    """Test package management endpoints."""

    def test_list_packages(self):
        """Test listing all packages."""
        client = TestClient(app)

        response = client.get("/api/v1/packages")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_nonexistent_package(self):
        """Test getting nonexistent package."""
        client = TestClient(app)

        response = client.get("/api/v1/packages/nonexistent-package-id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_processing_workflow(self):
        """Test complete file processing workflow."""
        client = TestClient(app)

        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
            This is a fundamental principle of software architecture.
            Modular design allows for better maintainability.
            The latest trends in 2023 show microservices are popular.
            Best practices include separation of concerns.
            """)
            temp_path = f.name

        try:
            # Step 1: Upload file
            with open(temp_path, 'rb') as f:
                upload_response = client.post(
                    "/api/v1/process",
                    files={"file": ("test.txt", f, "text/plain")}
                )

            assert upload_response.status_code == 200
            job_id = upload_response.json()["job_id"]

            # Step 2: Check job status
            status_response = client.get(f"/api/v1/jobs/{job_id}")
            assert status_response.status_code == 200
            job_data = status_response.json()
            assert job_data["job_id"] == job_id

            # Note: In a real test, we would wait for processing to complete
            # and check the final status, but for unit tests we just verify
            # the workflow structure

        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
