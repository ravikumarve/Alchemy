"""
Archaeologist Agent - Main Orchestration Module

Implements the complete 7-step workflow for extracting evergreen content
from legacy documents using LangGraph for orchestration.

Workflow Steps:
1. File Validation (5s) - Verify file format and integrity
2. Content Extraction (2s) - Extract raw text using unstructured.io
3. Semantic Analysis (30s) - Identify evergreen vs outdated content
4. Data Structuring (20s) - Organize into chunks and tables
5. Quality Filtering (15s) - Filter low-quality or irrelevant content
6. Metadata Enrichment (5s) - Add source, timestamp, confidence scores
7. Package Generation (3s) - Create JSON package for Trend-Jacker

Total Time Budget: 80 seconds (with safety margin)
"""

import os
import time
from typing import Dict, Any, Optional, TypedDict
from datetime import datetime
import logging
import uuid

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available, using fallback execution")

# Local imports
from src.agents.archaeologist_state import (
    ArchaeologistState,
    ProcessingStatus,
    ExtractionQuality,
    create_initial_state,
    update_step_timing,
    calculate_evergreen_score,
    assess_quality,
    OUTDATED_KEYWORDS,
    EVERGREEN_KEYWORDS
)
from src.pipeline.text_extractor import TextExtractor
from src.pipeline.semantic_chunker import SemanticChunker
from src.pipeline.table_extractor import TableExtractor
from src.pipeline.data_packager import DataPackager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArchaeologistAgent:
    """
    Main Archaeologist agent that orchestrates the 7-step content extraction workflow.

    Uses LangGraph for state management and workflow orchestration.
    Implements retry logic, fallback mechanisms, and timeout handling.
    """

    def __init__(self):
        """Initialize ArchaeologistAgent with all pipeline components."""
        # Initialize pipeline components
        self.text_extractor = TextExtractor()
        self.semantic_chunker = SemanticChunker()
        self.table_extractor = TableExtractor()
        self.data_packager = DataPackager()

        # Time budgets for each step (in seconds)
        self.step_time_budgets = {
            'validate_file': 5.0,
            'extract_content': 2.0,
            'analyze_semantics': 30.0,
            'structure_data': 20.0,
            'filter_quality': 15.0,
            'enrich_metadata': 5.0,
            'generate_package': 3.0
        }

        # Build LangGraph workflow if available
        if LANGGRAPH_AVAILABLE:
            self.workflow = self._build_workflow()
            self.memory = MemorySaver()
        else:
            self.workflow = None
            self.memory = None

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a file through the complete Archaeologist workflow.

        Args:
            file_path: Path to the file to process

        Returns:
            Dictionary containing:
            - success: Whether processing was successful
            - package: Final package for Trend-Jacker (if successful)
            - state: Final ArchaeologistState
            - processing_time: Total processing time
            - errors: List of errors (if any)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        # Generate job ID
        job_id = str(uuid.uuid4())

        # Create initial state
        state = create_initial_state(file_path, job_id)

        logger.info(f"Starting Archaeologist workflow for {file_path} (job_id: {job_id})")

        start_time = time.time()

        try:
            # Execute workflow
            if LANGGRAPH_AVAILABLE and self.workflow:
                # Use LangGraph execution
                final_state = self._execute_with_langgraph(state)
            else:
                # Use fallback execution
                final_state = self._execute_fallback(state)

            processing_time = time.time() - start_time

            # Prepare result
            result = {
                'success': final_state.get('status') == ProcessingStatus.COMPLETED,
                'package': final_state.get('output_package'),
                'state': final_state,
                'processing_time': processing_time,
                'errors': final_state.get('extraction_errors', [])
            }

            if result['success']:
                logger.info(
                    f"Archaeologist workflow completed successfully in {processing_time:.2f}s"
                )
            else:
                logger.warning(
                    f"Archaeologist workflow completed with errors in {processing_time:.2f}s"
                )

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Archaeologist workflow failed after {processing_time:.2f}s: {str(e)}")

            return {
                'success': False,
                'package': None,
                'state': state,
                'processing_time': processing_time,
                'errors': [str(e)]
            }

    def _build_workflow(self) -> StateGraph:
        """
        Build LangGraph workflow for Archaeologist agent.

        Returns:
            Configured StateGraph workflow
        """
        # Create workflow graph
        workflow = StateGraph(ArchaeologistState)

        # Add nodes for each step
        workflow.add_node("validate_file", self._step_validate_file)
        workflow.add_node("extract_content", self._step_extract_content)
        workflow.add_node("analyze_semantics", self._step_analyze_semantics)
        workflow.add_node("structure_data", self._step_structure_data)
        workflow.add_node("filter_quality", self._step_filter_quality)
        workflow.add_node("enrich_metadata", self._step_enrich_metadata)
        workflow.add_node("generate_package", self._step_generate_package)

        # Define workflow edges
        workflow.set_entry_point("validate_file")
        workflow.add_edge("validate_file", "extract_content")
        workflow.add_edge("extract_content", "analyze_semantics")
        workflow.add_edge("analyze_semantics", "structure_data")
        workflow.add_edge("structure_data", "filter_quality")
        workflow.add_edge("filter_quality", "enrich_metadata")
        workflow.add_edge("enrich_metadata", "generate_package")
        workflow.add_edge("generate_package", END)

        return workflow.compile(checkpointer=self.memory)

    def _execute_with_langgraph(self, state: ArchaeologistState) -> ArchaeologistState:
        """
        Execute workflow using LangGraph.

        Args:
            state: Initial ArchaeologistState

        Returns:
            Final ArchaeologistState
        """
        # Execute workflow
        config = {"configurable": {"thread_id": state["job_id"]}}
        result = self.workflow.invoke(state, config)

        return result

    def _execute_fallback(self, state: ArchaeologistState) -> ArchaeologistState:
        """
        Execute workflow using fallback sequential execution.

        Args:
            state: Initial ArchaeologistState

        Returns:
            Final ArchaeologistState
        """
        # Execute steps sequentially
        steps = [
            ("validate_file", self._step_validate_file),
            ("extract_content", self._step_extract_content),
            ("analyze_semantics", self._step_analyze_semantics),
            ("structure_data", self._step_structure_data),
            ("filter_quality", self._step_filter_quality),
            ("enrich_metadata", self._step_enrich_metadata),
            ("generate_package", self._step_generate_package)
        ]

        for step_name, step_func in steps:
            try:
                state = step_func(state)
                if state.get('status') == ProcessingStatus.FAILED:
                    logger.error(f"Workflow failed at step: {step_name}")
                    break
            except Exception as e:
                logger.error(f"Step {step_name} failed: {str(e)}")
                state['status'] = ProcessingStatus.FAILED
                state['error_message'] = str(e)
                break

        return state

    # Step 1: File Validation
    def _step_validate_file(self, state: ArchaeologistState) -> ArchaeologistState:
        """
        Step 1: Validate file format and integrity.

        Time Budget: 5 seconds
        """
        step_name = "validate_file"
        state['current_step'] = 1
        state['status'] = ProcessingStatus.VALIDATING
        state['step_start_time'] = datetime.utcnow().isoformat()

        logger.info(f"Step 1: Validating file {state['file_path']}")

        try:
            # Check if file exists
            if not os.path.exists(state['file_path']):
                raise FileNotFoundError(f"File not found: {state['file_path']}")

            # Check file size
            file_size = os.path.getsize(state['file_path'])
            if file_size == 0:
                raise ValueError("File is empty")

            # Check file extension
            file_ext = os.path.splitext(state['file_path'])[1].lower()
            supported_extensions = ['.pdf', '.txt', '.html', '.htm']
            if file_ext not in supported_extensions:
                raise ValueError(
                    f"Unsupported file format: {file_ext}. "
                    f"Supported formats: {', '.join(supported_extensions)}"
                )

            # Update state
            state['file_metadata'] = {
                'file_type': file_ext[1:],  # Remove dot
                'file_size': file_size,
                'validation_passed': True
            }

            # Update timing
            state = update_step_timing(state, step_name)

            logger.info(f"Step 1 completed: File validated successfully")

            return state

        except Exception as e:
            logger.error(f"Step 1 failed: {str(e)}")
            state['status'] = ProcessingStatus.FAILED
            state['error_message'] = str(e)
            state['extraction_errors'].append(f"Validation failed: {str(e)}")
            return state

    # Step 2: Content Extraction
    def _step_extract_content(self, state: ArchaeologistState) -> ArchaeologistState:
        """
        Step 2: Extract raw text from file.

        Time Budget: 2 seconds
        """
        step_name = "extract_content"
        state['current_step'] = 2
        state['status'] = ProcessingStatus.EXTRACTING
        state['step_start_time'] = datetime.utcnow().isoformat()

        logger.info("Step 2: Extracting content from file")

        try:
            # Extract text using TextExtractor
            extraction_result = self.text_extractor.extract(state['file_path'])

            # Update state
            state['raw_text'] = extraction_result['raw_text']
            state['file_metadata'].update(extraction_result['metadata'])
            state['extraction_errors'].extend(extraction_result.get('errors', []))

            # Update timing
            state = update_step_timing(state, step_name)

            logger.info(f"Step 2 completed: Extracted {len(state['raw_text'])} characters")

            return state

        except Exception as e:
            logger.error(f"Step 2 failed: {str(e)}")
            state['status'] = ProcessingStatus.FAILED
            state['error_message'] = str(e)
            state['extraction_errors'].append(f"Extraction failed: {str(e)}")
            return state

    # Step 3: Semantic Analysis
    def _step_analyze_semantics(self, state: ArchaeologistState) -> ArchaeologistState:
        """
        Step 3: Analyze semantics to identify evergreen vs outdated content.

        Time Budget: 30 seconds
        """
        step_name = "analyze_semantics"
        state['current_step'] = 3
        state['status'] = ProcessingStatus.ANALYZING
        state['step_start_time'] = datetime.utcnow().isoformat()

        logger.info("Step 3: Analyzing content semantics")

        try:
            # Analyze semantics using SemanticChunker
            analysis_result = self.semantic_chunker.analyze(
                state['raw_text'],
                state['file_metadata']
            )

            # Update state
            state['content_chunks'] = analysis_result['content_chunks']
            state['evergreen_score'] = analysis_result['evergreen_score']
            state['outdated_indicators'] = analysis_result['outdated_indicators']
            state['confidence_scores'] = analysis_result['confidence_scores']

            # Update timing
            state = update_step_timing(state, step_name)

            logger.info(
                f"Step 3 completed: Analyzed {len(state['content_chunks'])} chunks, "
                f"evergreen_score={state['evergreen_score']:.2f}"
            )

            return state

        except Exception as e:
            logger.error(f"Step 3 failed: {str(e)}")
            state['status'] = ProcessingStatus.FAILED
            state['error_message'] = str(e)
            state['extraction_errors'].append(f"Semantic analysis failed: {str(e)}")
            return state

    # Step 4: Data Structuring
    def _step_structure_data(self, state: ArchaeologistState) -> ArchaeologistState:
        """
        Step 4: Structure data into chunks and extract tables.

        Time Budget: 20 seconds
        """
        step_name = "structure_data"
        state['current_step'] = 4
        state['status'] = ProcessingStatus.STRUCTURING
        state['step_start_time'] = datetime.utcnow().isoformat()

        logger.info("Step 4: Structuring data and extracting tables")

        try:
            # Extract tables using TableExtractor
            table_result = self.table_extractor.extract(
                state['raw_text'],
                state['file_metadata']
            )

            # Update state
            state['extracted_tables'] = table_result['extracted_tables']

            # Update timing
            state = update_step_timing(state, step_name)

            logger.info(
                f"Step 4 completed: Structured {len(state['content_chunks'])} chunks, "
                f"extracted {len(state['extracted_tables'])} tables"
            )

            return state

        except Exception as e:
            logger.error(f"Step 4 failed: {str(e)}")
            state['status'] = ProcessingStatus.FAILED
            state['error_message'] = str(e)
            state['extraction_errors'].append(f"Data structuring failed: {str(e)}")
            return state

    # Step 5: Quality Filtering
    def _step_filter_quality(self, state: ArchaeologistState) -> ArchaeologistState:
        """
        Step 5: Filter content based on quality assessment.

        Time Budget: 15 seconds
        """
        step_name = "filter_quality"
        state['current_step'] = 5
        state['status'] = ProcessingStatus.FILTERING
        state['step_start_time'] = datetime.utcnow().isoformat()

        logger.info("Step 5: Filtering content by quality")

        try:
            # Filter chunks by quality
            filtered_chunks = self.semantic_chunker.filter_chunks(
                state['content_chunks'],
                min_quality='medium'
            )

            # Assess overall quality
            state['quality_assessment'] = assess_quality(
                state['evergreen_score'],
                state['confidence_scores'],
                len(state['raw_text'])
            )

            # Update state
            state['filtered_content'] = filtered_chunks

            # Update timing
            state = update_step_timing(state, step_name)

            logger.info(
                f"Step 5 completed: Filtered {len(state['content_chunks'])} -> "
                f"{len(state['filtered_content'])} chunks, "
                f"quality={state['quality_assessment']}"
            )

            return state

        except Exception as e:
            logger.error(f"Step 5 failed: {str(e)}")
            state['status'] = ProcessingStatus.FAILED
            state['error_message'] = str(e)
            state['extraction_errors'].append(f"Quality filtering failed: {str(e)}")
            return state

    # Step 6: Metadata Enrichment
    def _step_enrich_metadata(self, state: ArchaeologistState) -> ArchaeologistState:
        """
        Step 6: Enrich content with additional metadata.

        Time Budget: 5 seconds
        """
        step_name = "enrich_metadata"
        state['current_step'] = 6
        state['status'] = ProcessingStatus.ENRICHING
        state['step_start_time'] = datetime.utcnow().isoformat()

        logger.info("Step 6: Enriching metadata")

        try:
            # Add enrichment metadata to filtered chunks
            for chunk in state['filtered_content']:
                chunk['metadata']['enriched'] = True
                chunk['metadata']['enrichment_timestamp'] = datetime.utcnow().isoformat()
                chunk['metadata']['source_agent'] = 'archaeologist'

            # Update timing
            state = update_step_timing(state, step_name)

            logger.info(f"Step 6 completed: Enriched {len(state['filtered_content'])} chunks")

            return state

        except Exception as e:
            logger.error(f"Step 6 failed: {str(e)}")
            state['status'] = ProcessingStatus.FAILED
            state['error_message'] = str(e)
            state['extraction_errors'].append(f"Metadata enrichment failed: {str(e)}")
            return state

    # Step 7: Package Generation
    def _step_generate_package(self, state: ArchaeologistState) -> ArchaeologistState:
        """
        Step 7: Generate final package for Trend-Jacker handoff.

        Time Budget: 3 seconds
        """
        step_name = "generate_package"
        state['current_step'] = 7
        state['status'] = ProcessingStatus.PACKAGING
        state['step_start_time'] = datetime.utcnow().isoformat()

        logger.info("Step 7: Generating package for Trend-Jacker")

        try:
            # Create package using DataPackager
            package_result = self.data_packager.create_package(
                state,
                state['filtered_content'],
                state['extracted_tables']
            )

            # Update state
            state['output_package'] = package_result['package']

            # Update timing
            state = update_step_timing(state, step_name)

            # Mark as completed
            state['status'] = ProcessingStatus.COMPLETED

            logger.info(
                f"Step 7 completed: Package generated successfully, "
                f"package_id={package_result['package_id']}"
            )

            return state

        except Exception as e:
            logger.error(f"Step 7 failed: {str(e)}")
            state['status'] = ProcessingStatus.FAILED
            state['error_message'] = str(e)
            state['extraction_errors'].append(f"Package generation failed: {str(e)}")
            return state


# Convenience function for quick processing
def process_file(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to process a file through Archaeologist workflow.

    Args:
        file_path: Path to the file to process

    Returns:
        Dictionary with processing results
    """
    agent = ArchaeologistAgent()
    return agent.process_file(file_path)


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python archaeologist.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    result = process_file(file_path)

    if result['success']:
        print(f"✓ Processing completed successfully in {result['processing_time']:.2f}s")
        print(f"  Package ID: {result['package']['package_id']}")
        print(f"  Chunks: {len(result['package']['content'])}")
        print(f"  Tables: {len(result['package']['tables'])}")
    else:
        print(f"✗ Processing failed: {result['errors']}")
        sys.exit(1)
