# 🌐 ALCHEMY API Documentation

## Overview

The ALCHEMY API provides a comprehensive interface for content processing, management, and monitoring. This documentation covers all available endpoints, request/response formats, and usage examples.

## API Base URL

```
http://localhost:8000/api/v1
```

## Authentication

The ALCHEMY API does not require authentication. All endpoints are publicly accessible.

## Rate Limiting

- **Standard**: 100 requests per minute
- **Burst**: 200 requests per minute for authenticated users

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- **200**: Success
- **201**: Created
- **400**: Bad Request - Invalid input data
- **404**: Not Found - Resource does not exist
- **500**: Internal Server Error - Server error

## Endpoints

### 1. Process File

**POST** `/api/v1/process`

Process a file through the ALCHEMY pipeline.

#### Request Body

```json
{
  "file": <binary file>
}
```

**File Format**: PDF, TXT, HTML, or HTM
**Maximum Size**: 100MB

#### Response

```json
{
  "job_id": "string",
  "status": "processing",
  "file_name": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Example

```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### 2. Get Job Status

**GET** `/api/v1/jobs/{job_id}`

Get the status of a specific job.

#### Path Parameters

- `job_id` (string): The unique identifier of the job

#### Response

```json
{
  "job_id": "string",
  "status": "string",
  "file_name": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "processing_time": 123.45,
  "error_message": "string",
  "package_id": "string"
}
```

#### Example

```bash
curl http://localhost:8000/api/v1/jobs/job123
```

### 3. List Jobs

**GET** `/api/v1/jobs`

Get a list of all jobs.

#### Query Parameters

- `status` (string): Filter by job status (optional)
- `limit` (integer): Number of results to return (optional, default: 50)
- `offset` (integer): Number of results to skip (optional, default: 0)

#### Response

```json
{
  "jobs": [
    {
      "job_id": "string",
      "status": "string",
      "file_name": "string",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "processing_time": 123.45,
      "error_message": "string",
      "package_id": "string"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

#### Example

```bash
curl "http://localhost:8000/api/v1/jobs?status=completed&limit=10"
```

### 4. Get Package

**GET** `/api/v1/packages/{package_id}`

Get details of a specific package.

#### Path Parameters

- `package_id` (string): The unique identifier of the package

#### Response

```json
{
  "package_id": "string",
  "version": "string",
  "source_agent": "string",
  "target_agent": "string",
  "timestamp": "2024-01-01T00:00:00Z",
  "metadata": {},
  "content": [],
  "tables": [],
  "quality": {},
  "handoff": {}
}
```

#### Example

```bash
curl http://localhost:8000/api/v1/packages/pkg123
```

### 5. List Packages

**GET** `/api/v1/packages`

Get a list of all packages.

#### Query Parameters

- `source_agent` (string): Filter by source agent (optional)
- `target_agent` (string): Filter by target agent (optional)
- `limit` (integer): Number of results to return (optional, default: 50)
- `offset` (integer): Number of results to skip (optional, default: 0)

#### Response

```json
{
  "packages": [
    {
      "package_id": "string",
      "version": "string",
      "source_agent": "string",
      "target_agent": "string",
      "timestamp": "2024-01-01T00:00:00Z",
      "metadata": {},
      "content": [],
      "tables": [],
      "quality": {},
      "handoff": {}
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

#### Example

```bash
curl "http://localhost:8000/api/v1/packages?source_agent=archaeologist&limit=10"
```

### 6. Health Check

**GET** `/health`

Check if the API is healthy.

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

#### Example

```bash
curl http://localhost:8000/health
```

## Request/Response Formats

### Job Status Values

- `pending`: Job is queued for processing
- `processing`: Job is currently being processed
- `completed`: Job completed successfully
- `failed`: Job failed to complete

### Package Structure

A package contains the following fields:

- `package_id`: Unique identifier
- `version`: Package version
- `source_agent`: Source agent that created the package
- `target_agent`: Target agent that should process the package
- `timestamp`: Creation timestamp
- `metadata`: Additional metadata
- `content`: Array of content chunks
- `tables`: Array of extracted tables
- `quality`: Quality assessment metrics
- `handoff`: Handoff information

### Content Chunk Structure

Each content chunk contains:

- `chunk_id`: Unique identifier
- `content_type`: Type of content (text, table, etc.)
- `quality_level`: Quality assessment
- `text`: Content text
- `evergreen_score`: Evergreen content score
- `confidence_score`: Confidence score
- `length`: Content length in characters

### Table Structure

Each table contains:

- `table_id`: Unique identifier
- `format`: Table format (markdown, html, csv, etc.)
- `row_count`: Number of rows
- `col_count`: Number of columns
- `headers`: Array of column headers
- `data`: Array of row data

## Error Codes

### Common Error Codes

- `INVALID_FILE_FORMAT`: File format is not supported
- `FILE_TOO_LARGE`: File size exceeds limit
- `PROCESSING_ERROR`: Error during processing
- `JOB_NOT_FOUND`: Job does not exist
- `PACKAGE_NOT_FOUND`: Package does not exist
- `INTERNAL_ERROR`: Internal server error

## WebSocket Endpoints

The API supports WebSocket connections for real-time updates:

**WebSocket URL**: `ws://localhost:8000/ws`

#### Events

- `job_update`: Job status update
- `package_created`: New package created
- `error`: Error occurred

#### Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws')

ws.onopen = () => {
  console.log('Connected to WebSocket')
}

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  console.log('Received:', data)
}

ws.onerror = (error) => {
  console.error('WebSocket error:', error)
}
```

## API Testing

### Using Postman

1. Import the Postman collection from `docs/api/postman/AlCHEMY-API.postman_collection.json`
2. Set the base URL to `http://localhost:8000/api/v1`
3. Configure environment variables in `docs/api/postman/AlCHEMY-API.postman_environment.json`

### Using curl

All endpoints can be tested using curl as shown in the examples above.

## API Versioning

The API uses semantic versioning:

- **Major version**: Breaking changes
- **Minor version**: New features
- **Patch version**: Bug fixes

Current version: `1.0.0`

## Rate Limit Headers

The API includes the following rate limit headers in responses:

- `X-RateLimit-Limit`: Maximum number of requests allowed
- `X-RateLimit-Remaining`: Number of requests remaining
- `X-RateLimit-Reset`: Time when rate limit resets (Unix timestamp)

## Monitoring

The API includes monitoring endpoints:

- `/health`: Health check endpoint
- `/metrics`: Prometheus metrics endpoint
- `/logs`: Application logs (admin only)

## API Key Management

API keys are not required for the ALCHEMY API. However, for high-volume usage, consider implementing API key management for rate limiting and access control.

## API Documentation Updates

For API documentation updates, refer to the `CHANGELOG.md` file in the `docs/api` directory.

## Contact

For API-related questions or issues, please contact:

- **Email**: api-support@alchemy.com
- **GitHub**: https://github.com/ravikumarve/Alchemy/issues
- **Discord**: alchemy-devs

## License

This API documentation is licensed under the MIT License.