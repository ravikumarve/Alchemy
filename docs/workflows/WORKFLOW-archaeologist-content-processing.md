# WORKFLOW: Archaeologist Agent Content Processing
**Version**: 0.1
**Date**: 2026-04-24
**Author**: Workflow Architect
**Status**: Draft
**Implements**: PRD v0.1 - Archaeologist Agent Implementation

---

## Overview

The Archaeologist agent is the first stage in the ALCHEMY content transmutation pipeline. It ingests raw content files (PDFs, TXT, HTML) from the `raw_ore/` directory, extracts structured text using unstructured.io, identifies evergreen facts through semantic chunking, extracts tabular data, and filters out outdated context. The agent produces a structured data package that is handed off to the Trend-Jacker agent for modernization.

---

## Actors

| Actor | Role in this workflow |
|---|---|
| File System Watcher | Monitors `raw_ore/` directory for new files |
| Archaeologist Agent | Executes text extraction and semantic analysis |
| unstructured.io Service | Extracts text from PDF/TXT/HTML files |
| SemanticChunker | Identifies evergreen content chunks |
| TableExtractor | Extracts structured tabular data |
| SQLite Database | Persists processing state and extracted data |
| Trend-Jacker Agent | Receives processed data for modernization |
| Background Queue | Manages async processing jobs |

---

## Prerequisites

- `raw_ore/` directory exists and is writable
- SQLite database initialized with processing_jobs table
- unstructured.io library installed and configured
- LangGraph orchestration framework initialized
- Background queue service running (for cron/daemon mode)
- File system watcher active (for real-time processing)

---

## Trigger

**Primary Trigger:** New file detected in `raw_ore/` directory by file system watcher
**Secondary Trigger:** Cron job scheduled every 15 minutes scans `raw_ore/` for unprocessed files
**Manual Trigger:** API endpoint `POST /api/process` for on-demand processing

---

## Workflow Tree

### STEP 1: File Discovery and Validation
**Actor**: File System Watcher
**Action**: Detect new files in `raw_ore/` and validate format
**Timeout**: 5s
**Input**: `{ directory: string }`
**Output on SUCCESS**: `{ file_path: string, file_type: string, file_size: int, created_at: timestamp }` -> GO TO STEP 2
**Output on FAILURE**:
  - `FAILURE(directory_not_found)`: Directory does not exist -> [recovery: create directory, log warning, retry in 60s]
  - `FAILURE(invalid_file_type)`: Unsupported format (e.g., .exe, .zip) -> [recovery: move to `rejected/` directory, log error, no retry]
  - `FAILURE(file_corrupted)`: File cannot be read -> [recovery: move to `failed/` directory, log error, no retry]

**Observable states during this step**:
  - Customer sees: Nothing (background process)
  - Operator sees: New file detected in dashboard with "validating" status
  - Database: `processing_jobs.status = "discovered"`, `processing_jobs.file_path = <path>`
  - Logs: `[archaeologist] file discovered: <path>, type: <type>, size: <bytes>`

---

### STEP 2: Job Creation and State Initialization
**Actor**: Archaeologist Agent
**Action**: Create processing job record in database
**Timeout**: 2s
**Input**: `{ file_path: string, file_type: string, file_size: int }`
**Output on SUCCESS**: `{ job_id: uuid, status: "pending", created_at: timestamp }` -> GO TO STEP 3
**Output on FAILURE**:
  - `FAILURE(database_error)`: Cannot connect to SQLite -> [recovery: retry x3 with 2s backoff -> ABORT_CLEANUP]
  - `FAILURE(duplicate_job)`: File already being processed -> [recovery: skip file, log warning, no cleanup needed]

**Observable states during this step**:
  - Customer sees: Nothing (background process)
  - Operator sees: Job created in dashboard with "pending" status
  - Database: `processing_jobs.id = <uuid>`, `processing_jobs.status = "pending"`, `processing_jobs.current_step = "job_creation"`
  - Logs: `[archaeologist] job created: <job_id> for file: <file_path>`

---

### STEP 3: Text Extraction with unstructured.io
**Actor**: Archaeologist Agent
**Action**: Extract raw text from file using unstructured.io
**Timeout**: 30s
**Input**: `{ job_id: uuid, file_path: string, file_type: string }`
**Output on SUCCESS**: `{ extracted_text: string, metadata: dict, extraction_time: float }` -> GO TO STEP 4
**Output on FAILURE**:
  - `FAILURE(extraction_timeout)`: unstructured.io took >30s -> [recovery: retry x2 with 5s backoff -> ABORT_CLEANUP]
  - `FAILURE(corrupted_file)`: File is corrupted or password-protected -> [recovery: move to `failed/`, log error, ABORT_CLEANUP]
  - `FAILURE(empty_content)`: No text extracted -> [recovery: move to `rejected/`, log warning, ABORT_CLEANUP]
  - `FAILURE(memory_error)`: File too large for available memory -> [recovery: move to `failed/`, log error, ABORT_CLEANUP]

**Observable states during this step**:
  - Customer sees: Nothing (background process)
  - Operator sees: Job status "extracting" with progress indicator
  - Database: `processing_jobs.status = "extracting"`, `processing_jobs.current_step = "text_extraction"`, `processing_jobs.progress = 33`
  - Logs: `[archaeologist] text extraction started: <job_id>, file: <file_path>`

---

### STEP 4: Semantic Chunking for Evergreen Content
**Actor**: SemanticChunker
**Action**: Analyze text and identify evergreen facts, filter outdated context
**Timeout**: 20s
**Input**: `{ job_id: uuid, extracted_text: string, metadata: dict }`
**Output on SUCCESS**: `{ evergreen_chunks: array, outdated_sections: array, confidence_score: float }` -> GO TO STEP 5
**Output on FAILURE**:
  - `FAILURE(chunking_timeout)`: Semantic analysis took >20s -> [recovery: use fallback chunking (simple sentence splitting), log warning, continue to STEP 5]
  - `FAILURE(low_confidence)`: Confidence score <0.5 -> [recovery: flag for manual review, log warning, continue to STEP 5]
  - `FAILURE(api_error)`: Semantic analysis service unavailable -> [recovery: retry x1 with 3s backoff, use fallback if still fails]

**Observable states during this step**:
  - Customer sees: Nothing (background process)
  - Operator sees: Job status "analyzing" with progress indicator
  - Database: `processing_jobs.status = "analyzing"`, `processing_jobs.current_step = "semantic_chunking"`, `processing_jobs.progress = 66`
  - Logs: `[archaeologist] semantic chunking started: <job_id>, chunks: <count>`

---

### STEP 5: Table Extraction for Structured Data
**Actor**: TableExtractor
**Action**: Extract and parse tabular data from document
**Timeout**: 15s
**Input**: `{ job_id: uuid, extracted_text: string, metadata: dict }`
**Output on SUCCESS**: `{ tables: array, table_count: int, extraction_quality: string }` -> GO TO STEP 6
**Output on FAILURE**:
  - `FAILURE(extraction_timeout)`: Table extraction took >15s -> [recovery: skip table extraction, log warning, continue to STEP 6 with tables=[]]
  - `FAILURE(no_tables_found)`: No tables detected -> [recovery: continue to STEP 6 with tables=[], no cleanup needed]
  - `FAILURE(parsing_error)`: Table structure invalid -> [recovery: skip problematic tables, log warning, continue to STEP 6]

**Observable states during this step**:
  - Customer sees: Nothing (background process)
  - Operator sees: Job status "extracting_tables" with progress indicator
  - Database: `processing_jobs.status = "extracting_tables"`, `processing_jobs.current_step = "table_extraction"`, `processing_jobs.progress = 80`
  - Logs: `[archaeologist] table extraction started: <job_id>, tables found: <count>`

---

### STEP 6: Data Packaging and Trend-Jacker Handoff
**Actor**: Archaeologist Agent
**Action**: Package extracted data and hand off to Trend-Jacker agent
**Timeout**: 5s
**Input**: `{ job_id: uuid, evergreen_chunks: array, tables: array, metadata: dict, confidence_score: float }`
**Output on SUCCESS**: `{ package_id: uuid, handoff_status: "success", next_agent: "trend_jacker" }` -> GO TO STEP 7
**Output on FAILURE**:
  - `FAILURE(package_error)`: Cannot create data package -> [recovery: retry x1, ABORT_CLEANUP if still fails]
  - `FAILURE(handoff_timeout)`: Trend-Jacker not responding -> [recovery: queue for retry in 60s, ABORT_CLEANUP if 3 retries fail]

**Observable states during this step**:
  - Customer sees: Nothing (background process)
  - Operator sees: Job status "packaging" with progress indicator
  - Database: `processing_jobs.status = "packaging"`, `processing_jobs.current_step = "data_packaging"`, `processing_jobs.progress = 90`
  - Logs: `[archaeologist] data packaging started: <job_id>, preparing handoff to trend_jacker`

---

### STEP 7: Job Completion and File Cleanup
**Actor**: Archaeologist Agent
**Action**: Mark job complete, move source file to `processed/`, update database
**Timeout**: 3s
**Input**: `{ job_id: uuid, package_id: uuid, handoff_status: string }`
**Output on SUCCESS**: `{ job_id: uuid, status: "completed", completed_at: timestamp, total_time: float }` -> END
**Output on FAILURE**:
  - `FAILURE(file_move_error)`: Cannot move source file -> [recovery: log error, mark job completed anyway (data is safe)]
  - `FAILURE(database_update_error)`: Cannot update job status -> [recovery: log error, job is effectively complete]

**Observable states during this step**:
  - Customer sees: Nothing (background process)
  - Operator sees: Job status "completed" with green checkmark
  - Database: `processing_jobs.status = "completed"`, `processing_jobs.completed_at = <timestamp>`, `processing_jobs.total_time = <seconds>`
  - Logs: `[archaeologist] job completed: <job_id>, total time: <seconds>s, handed off to trend_jacker`

---

### ABORT_CLEANUP: Archaeologist Processing Failure
**Triggered by**: Extraction timeout, database errors, corrupted files, memory errors
**Actions** (in order):
  1. Move source file from `raw_ore/` to `failed/` directory
  2. Set `processing_jobs.status = "failed"`
  3. Set `processing_jobs.error = "<error_message>"`
  4. Set `processing_jobs.failed_at = <timestamp>`
  5. Set `processing_jobs.current_step = "<failed_step>"`
  6. Log error with full context
  7. Send alert to monitoring system (if configured)
**What customer sees**: Nothing (background process)
**What operator sees**: Job in "failed" state with red error icon, error message displayed, retry button available

---

## State Transitions

```
[discovered] -> (job created) -> [pending]
[pending] -> (extraction started) -> [extracting]
[extracting] -> (extraction complete) -> [analyzing]
[analyzing] -> (chunking complete) -> [extracting_tables]
[extracting_tables] -> (tables extracted) -> [packaging]
[packaging] -> (handoff complete) -> [completed]
[any_state] -> (failure with cleanup) -> [failed]
[failed] -> (manual retry) -> [pending]
```

---

## Handoff Contracts

### Archaeologist -> Trend-Jacker
**Endpoint**: LangGraph state transition
**Payload**:
```json
{
  "job_id": "uuid — unique identifier for this processing job",
  "source_file": "string — original file path",
  "evergreen_chunks": [
    {
      "text": "string — extracted evergreen content",
      "confidence": "float — 0.0 to 1.0 confidence score",
      "metadata": {
        "source_section": "string — section reference",
        "word_count": "int — chunk length"
      }
    }
  ],
  "tables": [
    {
      "headers": ["string — column names"],
      "rows": [["string — cell values"]],
      "metadata": {
        "source_page": "int — page number",
        "table_type": "string — data/statistical/timeline"
      }
    }
  ],
  "document_metadata": {
    "title": "string — document title",
    "author": "string — document author",
    "publication_date": "string — original publication date",
    "content_type": "string — historical/educational/scientific",
    "extraction_timestamp": "string — ISO 8601 timestamp"
  },
  "quality_metrics": {
    "confidence_score": "float — overall quality score",
    "evergreen_ratio": "float — percentage of evergreen content",
    "data_completeness": "float — percentage of data extracted"
  }
}
```
**Success response**:
```json
{
  "status": "accepted",
  "trend_jacker_job_id": "uuid — new job ID for trend-jacking",
  "estimated_completion": "string — ISO 8601 timestamp"
}
```
**Failure response**:
```json
{
  "ok": false,
  "error": "string — error message",
  "code": "ERROR_CODE",
  "retryable": true
}
```
**Timeout**: 10s

---

## Cleanup Inventory

| Resource | Created at step | Destroyed by | Destroy method |
|---|---|---|---|
| Database job record | Step 2 | ABORT_CLEANUP | UPDATE status='failed' |
| Source file in raw_ore/ | Step 1 | ABORT_CLEANUP | MOVE to failed/ |
| Temporary extraction files | Step 3 | ABORT_CLEANUP | DELETE temp files |
| In-memory chunks | Step 4 | ABORT_CLEANUP | Clear from memory |
| Data package | Step 6 | ABORT_CLEANUP | DELETE if handoff failed |

---

## Reality Checker Findings

| # | Finding | Severity | Spec section affected | Resolution |
|---|---|---|---|---|
| RC-1 | Pending verification against actual implementation | TBD | All sections | To be populated after implementation |

---

## Test Cases

| Test | Trigger | Expected behavior |
|---|---|---|
| TC-01: Happy path | Valid PDF file, all services healthy | Job completes successfully, data handed off to Trend-Jacker |
| TC-02: Corrupted file | File cannot be read or is password-protected | File moved to failed/, job marked failed, error logged |
| TC-03: Extraction timeout | unstructured.io takes >30s | Retry x2 with 5s backoff, then ABORT_CLEANUP |
| TC-04: Empty content | File contains no extractable text | File moved to rejected/, job marked failed |
| TC-05: Low confidence | Semantic chunking confidence <0.5 | Flag for manual review, continue processing with warning |
| TC-06: No tables found | Document contains no tables | Continue processing with empty tables array |
| TC-07: Handoff timeout | Trend-Jacker not responding | Queue for retry in 60s, ABORT_CLEANUP after 3 failures |
| TC-08: Memory error | File too large for available memory | Move to failed/, log error, ABORT_CLEANUP |
| TC-09: Database error | SQLite connection fails | Retry x3 with 2s backoff, then ABORT_CLEANUP |
| TC-10: Partial failure | Table extraction fails after chunking succeeds | Continue with empty tables, log warning |

---

## Assumptions

| # | Assumption | Where verified | Risk if wrong |
|---|---|---|---|
| A1 | unstructured.io can handle PDF, TXT, and HTML formats | Not verified | Extraction fails for some file types |
| A2 | SemanticChunker can identify evergreen content with >70% accuracy | Not verified | Low quality content passed to Trend-Jacker |
| A3 | SQLite database is sufficient for local-first operation | Not verified | Performance issues at scale |
| A4 | File system watcher can detect new files within 5 seconds | Not verified | Processing delays |
| A5 | Trend-Jacker agent is always available for handoff | Not verified | Handoff failures require queuing |

---

## Open Questions

- What is the maximum file size that can be processed given CPU-only constraints?
- How should we handle files with mixed content (some evergreen, some outdated)?
- What is the acceptable confidence threshold for automatic vs manual review?
- How should we prioritize files when multiple are detected simultaneously?
- Should we implement batch processing or stick to single-file processing for MVP?

---

## Spec vs Reality Audit Log

| Date | Finding | Action taken |
|---|---|---|
| 2026-04-24 | Initial spec created | — |

---

## Performance Requirements

- **Total processing time**: <60 seconds per file (end-to-end)
- **Text extraction**: <30 seconds
- **Semantic chunking**: <20 seconds
- **Table extraction**: <15 seconds
- **Handoff to Trend-Jacker**: <10 seconds
- **Memory usage**: <500MB per file
- **CPU usage**: <80% on single core

---

## Monitoring and Observability

**Key Metrics to Track**:
- Processing success rate (target: >95%)
- Average processing time (target: <60s)
- Files processed per hour
- Error rate by failure type
- Queue depth (if using background processing)
- Memory and CPU utilization

**Alerting Thresholds**:
- Success rate drops below 90%
- Average processing time exceeds 90s
- Error rate exceeds 10%
- Queue depth exceeds 100 files
- Memory usage exceeds 1GB

---

## Next Steps

1. Review spec with Backend Architect for implementation feasibility
2. Validate assumptions with proof-of-concept implementation
3. Define database schema for processing_jobs table
4. Set up monitoring and alerting infrastructure
5. Implement Archaeologist agent following this spec
6. Execute Reality Checker pass against implementation
