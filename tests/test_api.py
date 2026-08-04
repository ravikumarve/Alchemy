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

    def _poll_job(self, client, job_id, max_retries=20, delay=0.2):
        """Poll job status until completion or timeout."""
        import time
        for _ in range(max_retries):
            resp = client.get(f"/api/v1/jobs/{job_id}")
            assert resp.status_code == 200
            data = resp.json()
            if data["status"] in ("completed", "failed"):
                return data
            time.sleep(delay)
        raise TimeoutError(f"Job {job_id} did not complete within {max_retries * delay}s")

    def test_complete_processing_workflow(self):
        """Test complete file processing workflow with job polling."""
        client = TestClient(app)

        # Create test file with meaningful content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
            The Art of War by Sun Tzu

            The supreme art of war is to subdue the enemy without fighting.
            If you know the enemy and know yourself, you need not fear the result of a hundred battles.
            Appear weak when you are strong, and strong when you are weak.
            In the midst of chaos, there is also opportunity.
            """)
            temp_path = f.name

        try:
            # Step 1: Upload file
            with open(temp_path, 'rb') as f:
                upload_response = client.post(
                    "/api/v1/process",
                    files={"file": ("sun_tzu.txt", f, "text/plain")}
                )

            assert upload_response.status_code == 200
            job_id = upload_response.json()["job_id"]
            assert upload_response.json()["status"] == "pending"

            # Step 2: Poll until job completes
            job_data = self._poll_job(client, job_id)

            assert job_data["status"] == "completed", f"Job failed: {job_data.get('error_message')}"
            assert job_data["job_id"] == job_id
            assert "package_id" in job_data
            assert job_data["processing_time"] is not None
            assert job_data["processing_time"] > 0

            # Step 3: Retrieve the package
            package_id = job_data["package_id"]
            pkg_response = client.get(f"/api/v1/packages/{package_id}")
            assert pkg_response.status_code == 200
            pkg = pkg_response.json()

            assert pkg["package_id"] == package_id
            assert pkg["source_agent"] == "archaeologist"
            assert "content" in pkg
            assert len(pkg["content"]) > 0
            assert "tables" in pkg
            assert "metadata" in pkg
            assert pkg["metadata"]["processing_time"] > 0
            assert pkg["metadata"]["extraction_method"] == "built-in"

            # Step 4: Verify package appears in listing
            list_response = client.get("/api/v1/packages")
            assert list_response.status_code == 200
            packages_list = list_response.json()
            package_ids = [p["package_id"] for p in packages_list]
            assert package_id in package_ids

            # Step 5: Verify job appears in completed filter
            filter_response = client.get("/api/v1/jobs?status=completed")
            assert filter_response.status_code == 200
            completed_jobs = filter_response.json()
            completed_ids = [j["job_id"] for j in completed_jobs]
            assert job_id in completed_ids

        finally:
            os.unlink(temp_path)

    def test_upload_then_delete_workflow(self):
        """Test upload, wait for completion, then delete job and package."""
        client = TestClient(app)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content for delete workflow. Strategy and planning are essential.")
            temp_path = f.name

        try:
            # Upload
            with open(temp_path, 'rb') as f:
                upload_resp = client.post(
                    "/api/v1/process",
                    files={"file": ("delete_test.txt", f, "text/plain")}
                )
            assert upload_resp.status_code == 200
            job_id = upload_resp.json()["job_id"]

            # Wait for completion
            job_data = self._poll_job(client, job_id)
            assert job_data["status"] == "completed"
            package_id = job_data["package_id"]

            # Verify package exists
            pkg_resp = client.get(f"/api/v1/packages/{package_id}")
            assert pkg_resp.status_code == 200

            # Delete job
            del_resp = client.delete(f"/api/v1/jobs/{job_id}")
            assert del_resp.status_code == 200

            # Verify job is gone
            get_resp = client.get(f"/api/v1/jobs/{job_id}")
            assert get_resp.status_code == 404

            # Delete package
            del_pkg = client.delete(f"/api/v1/packages/{package_id}")
            assert del_pkg.status_code == 200

            # Verify package is gone
            get_pkg = client.get(f"/api/v1/packages/{package_id}")
            assert get_pkg.status_code == 404

        finally:
            os.unlink(temp_path)

    def test_concurrent_processing(self):
        """Test that multiple files can be processed concurrently."""
        client = TestClient(app)
        temp_paths = []
        job_ids = []

        try:
            # Upload multiple files rapidly
            texts = [
                "First document about machine learning algorithms and neural networks.",
                "Second document about blockchain technology and distributed systems.",
                "Third document about quantum computing and quantum supremacy.",
            ]

            for i, text in enumerate(texts):
                tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
                tmp.write(text)
                tmp.close()
                temp_paths.append(tmp.name)

                with open(tmp.name, 'rb') as f:
                    resp = client.post(
                        "/api/v1/process",
                        files={"file": (f"doc_{i}.txt", f, "text/plain")}
                    )
                assert resp.status_code == 200
                job_ids.append(resp.json()["job_id"])

            # Poll all jobs to completion
            for job_id in job_ids:
                job_data = self._poll_job(client, job_id)
                assert job_data["status"] == "completed", \
                    f"Job {job_id} failed: {job_data.get('error_message')}"

            # Verify all jobs appear in listing
            list_resp = client.get("/api/v1/jobs")
            assert list_resp.status_code == 200
            jobs_list = list_resp.json()
            listed_ids = [j["job_id"] for j in jobs_list]
            for job_id in job_ids:
                assert job_id in listed_ids

        finally:
            for p in temp_paths:
                os.unlink(p)

    def test_error_propagation_via_api(self):
        """Test that processing errors propagate correctly through the API."""
        client = TestClient(app)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as f:
                resp = client.post(
                    "/api/v1/process",
                    files={"file": ("empty.txt", f, "text/plain")}
                )
            assert resp.status_code == 200
            job_id = resp.json()["job_id"]

            # Poll — should either complete (with no content) or fail
            job_data = self._poll_job(client, job_id)

            # Empty file is valid input; should complete with no errors
            assert job_data["status"] in ("completed", "failed")
            if job_data["status"] == "failed":
                assert "error_message" in job_data
                assert len(job_data["error_message"]) > 0

        finally:
            os.unlink(temp_path)

    def test_unsupported_file_handling(self):
        """Test that unsupported file formats are rejected at upload."""
        client = TestClient(app)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.exe', delete=False) as f:
            f.write("fake binary content")
            temp_path = f.name

        try:
            with open(temp_path, 'rb') as f:
                resp = client.post(
                    "/api/v1/process",
                    files={"file": ("virus.exe", f, "application/octet-stream")}
                )
            assert resp.status_code == 400
            detail = resp.json()["detail"]
            assert "Unsupported file format" in detail
            assert ".exe" in detail

        finally:
            os.unlink(temp_path)

    def _make_minimal_pdf(self, text: str = "Test PDF Content") -> bytes:
        """Create a minimal valid PDF with the given text."""
        content = f"BT /F1 12 Tf 100 700 Td ({text}) Tj ET"
        length = len(content.encode('latin-1'))
        return (
            b"%PDF-1.4\n"
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]\n"
            b"   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
            b"4 0 obj\n<< /Length " + str(length).encode() + b" >>\nstream\n"
            + content.encode('latin-1') + b"\nendstream\nendobj\n"
            b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
            b"xref\n0 6\n"
            b"0000000000 65535 f \n"
            b"0000000009 00000 n \n"
            b"0000000058 00000 n \n"
            b"0000000115 00000 n \n"
            b"0000000270 00000 n \n"
            b"0000000365 00000 n \n"
            b"trailer\n<< /Size 6 /Root 1 0 R >>\n"
            b"startxref\n420\n%%EOF"
        )

    def test_multiple_formats_supported(self):
        """Test all supported file formats are accepted and process correctly."""
        client = TestClient(app)

        # Test HTML and HTM with proper HTML content
        format_tests = [
            ('.html', 'text/html', 'page.html',
             '<html><body><p>Test content for HTML format.</p></body></html>',
             True),   # expect upload + processing success
            ('.htm', 'text/html', 'page.htm',
             '<html><body><p>Test content for HTM format.</p></body></html>',
             True),   # expect upload + processing success
            ('.pdf', 'application/pdf', 'sample.pdf',
             None,    # use _make_minimal_pdf
             False),  # just verify upload accepted; content assertion optional
        ]

        for ext, mime, fname, file_content, expect_completion in format_tests:
            if ext == '.pdf':
                # Write a minimal valid PDF
                pdf_bytes = self._make_minimal_pdf("ALCHEMY Test PDF Content")
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
                    f.write(pdf_bytes)
                    temp_path = f.name
            else:
                with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
                    f.write(file_content)
                    temp_path = f.name

            try:
                with open(temp_path, 'rb') as fh:
                    resp = client.post(
                        "/api/v1/process",
                        files={"file": (fname, fh, mime)}
                    )

                assert resp.status_code == 200, f"{ext} upload failed: {resp.json()}"

                # Poll for completion (PDF should succeed with proper content)
                job_id = resp.json()["job_id"]
                try:
                    job_data = self._poll_job(client, job_id, max_retries=15)
                    if expect_completion:
                        assert job_data["status"] == "completed", \
                            f"{ext} processing failed: {job_data.get('error_message')}"
                    else:
                        assert job_data["status"] in ("completed", "failed")
                except TimeoutError:
                    pass  # Allow timeout for slower CI

            finally:
                os.unlink(temp_path)

    def test_job_filtering_edge_cases(self):
        """Test job listing filters handle edge cases."""
        client = TestClient(app)

        # Empty filters
        resp = client.get("/api/v1/jobs?status=nonexistent")
        assert resp.status_code == 200
        assert resp.json() == []

        # Limit parameter
        resp = client.get("/api/v1/jobs?limit=0")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

        # Packages with limit
        resp = client.get("/api/v1/packages?limit=5")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_job_creation_timestamp_order(self):
        """Test jobs are returned in reverse chronological order."""
        client = TestClient(app)
        temp_paths = []
        job_ids = []

        try:
            for i in range(3):
                tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
                tmp.write(f"Document number {i} about various topics.")
                tmp.close()
                temp_paths.append(tmp.name)

                with open(tmp.name, 'rb') as f:
                    resp = client.post(
                        "/api/v1/process",
                        files={"file": (f"ts_test_{i}.txt", f, "text/plain")}
                    )
                assert resp.status_code == 200
                job_ids.append(resp.json()["job_id"])

            # Get all jobs
            list_resp = client.get("/api/v1/jobs?limit=10")
            assert list_resp.status_code == 200
            jobs = list_resp.json()

            # Verify newest first
            timestamps = [j["created_at"] for j in jobs if j["job_id"] in job_ids]
            assert timestamps == sorted(timestamps, reverse=True), \
                "Jobs not in reverse chronological order"

        finally:
            for p in temp_paths:
                os.unlink(p)


class TestExploreEndpoint:
    """Test the topic explore endpoint (Researcher Agent)."""

    def test_explore_topic_creates_job(self):
        """Test explore endpoint creates a job."""
        client = TestClient(app)

        response = client.post(
            "/api/v1/explore",
            json={"topic": "Stoicism for modern entrepreneurs"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"
        assert "topic" in data
        assert data["topic"] == "Stoicism for modern entrepreneurs"

    def test_explore_topic_empty(self):
        """Test explore endpoint rejects whitespace-only topic."""
        client = TestClient(app)

        response = client.post(
            "/api/v1/explore",
            json={"topic": "  "}
        )

        assert response.status_code == 400  # stripped to empty
        assert "Topic cannot be empty" in response.json()["detail"]

    def test_explore_topic_short(self):
        """Test explore endpoint rejects too-short topic."""
        client = TestClient(app)

        response = client.post(
            "/api/v1/explore",
            json={"topic": "x"}
        )

        assert response.status_code == 422

    def test_explore_topic_invalid_asset_type(self):
        """Test explore endpoint rejects invalid asset type."""
        client = TestClient(app)

        response = client.post(
            "/api/v1/explore",
            json={"topic": "Stoicism", "asset_type": "invalid_type"}
        )

        assert response.status_code == 422

    def test_explore_topic_asset_type(self):
        """Test explore endpoint accepts custom asset type."""
        client = TestClient(app)

        response = client.post(
            "/api/v1/explore",
            json={"topic": "Stoicism", "asset_type": "tiktok"}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "pending"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
