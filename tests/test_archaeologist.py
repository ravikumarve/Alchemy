"""
Unit Tests for Archaeologist Agent Components

Tests the core functionality of the Archaeologist agent including:
- State management
- Text extraction
- Semantic analysis
- Table extraction
- Data packaging
"""

import os
import sys
import tempfile
import json
from datetime import datetime
from typing import Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest

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


class TestArchaeologistState:
    """Test ArchaeologistState management functions."""

    def test_create_initial_state(self):
        """Test creation of initial state."""
        state = create_initial_state("/path/to/file.pdf", "test_job_123")

        assert state['file_path'] == "/path/to/file.pdf"
        assert state['job_id'] == "test_job_123"
        assert state['status'] == ProcessingStatus.PENDING
        assert state['current_step'] == 0
        assert state['raw_text'] is None
        assert state['content_chunks'] == []
        assert state['evergreen_score'] == 0.0
        assert state['quality_assessment'] == ExtractionQuality.LOW
        assert state['retry_count'] == 0
        assert state['max_retries'] == 3

    def test_update_step_timing(self):
        """Test step timing updates."""
        state = create_initial_state("/path/to/file.pdf", "test_job_123")
        state['step_start_time'] = datetime.utcnow().isoformat()

        # Simulate some processing time
        import time
        time.sleep(0.1)

        state = update_step_timing(state, "test_step")

        assert "test_step" in state['step_times']
        assert state['step_times']['test_step'] >= 0.1
        assert state['processing_time'] >= 0.1

    def test_calculate_evergreen_score(self):
        """Test evergreen score calculation."""
        # Test with evergreen content
        evergreen_text = "This is a fundamental principle of software architecture."
        score = calculate_evergreen_score(evergreen_text, OUTDATED_KEYWORDS)
        assert score >= 0.7  # Should be high

        # Test with outdated content
        outdated_text = "This is the latest news from 2023 about current events."
        score = calculate_evergreen_score(outdated_text, OUTDATED_KEYWORDS)
        assert score <= 0.5  # Should be low

        # Test with empty content
        score = calculate_evergreen_score("", OUTDATED_KEYWORDS)
        assert score == 0.0

    def test_assess_quality(self):
        """Test quality assessment."""
        # High quality
        quality = assess_quality(0.9, {'chunk1': 0.8, 'chunk2': 0.9}, 500)
        assert quality == ExtractionQuality.HIGH

        # Medium quality
        quality = assess_quality(0.6, {'chunk1': 0.6, 'chunk2': 0.5}, 200)
        assert quality == ExtractionQuality.MEDIUM

        # Low quality
        quality = assess_quality(0.4, {'chunk1': 0.4, 'chunk2': 0.3}, 100)
        assert quality == ExtractionQuality.LOW

        # Rejected
        quality = assess_quality(0.2, {'chunk1': 0.2, 'chunk2': 0.1}, 10)
        assert quality == ExtractionQuality.REJECTED


class TestTextExtractor:
    """Test TextExtractor functionality."""

    def test_extract_text_file(self):
        """Test extraction from plain text file."""
        extractor = TextExtractor()

        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document.\nIt has multiple lines.\nAnd some content.")
            temp_path = f.name

        try:
            result = extractor.extract(temp_path)

            assert 'raw_text' in result
            assert 'metadata' in result
            assert 'extraction_time' in result
            assert result['metadata']['file_type'] == 'txt'
            assert len(result['raw_text']) > 0
            assert result['extraction_time'] < 5.0  # Should be fast

        finally:
            os.unlink(temp_path)

    def test_extract_unsupported_format(self):
        """Test extraction with unsupported format."""
        extractor = TextExtractor()

        with pytest.raises(ValueError, match="Unsupported file format"):
            extractor.extract("/path/to/file.xyz")

    def test_extract_nonexistent_file(self):
        """Test extraction with nonexistent file."""
        extractor = TextExtractor()

        with pytest.raises(FileNotFoundError):
            extractor.extract("/path/to/nonexistent.pdf")


class TestSemanticChunker:
    """Test SemanticChunker functionality."""

    def test_analyze_text(self):
        """Test semantic analysis of text."""
        chunker = SemanticChunker()

        text = """
        This is a fundamental principle of software design.
        The latest news from 2023 shows current trends.
        Best practices include modular architecture.
        This year's conference was amazing.
        """

        metadata = {'file_type': 'txt', 'file_size': 100}

        result = chunker.analyze(text, metadata)

        assert 'content_chunks' in result
        assert 'evergreen_score' in result
        assert 'outdated_indicators' in result
        assert 'confidence_scores' in result
        assert 'analysis_time' in result
        assert len(result['content_chunks']) > 0
        assert 0.0 <= result['evergreen_score'] <= 1.0
        assert result['analysis_time'] < 35.0  # Should be within timeout

    def test_filter_chunks(self):
        """Test chunk filtering by quality."""
        chunker = SemanticChunker()

        chunks = [
            {
                'chunk_id': 'chunk_0',
                'text': 'High quality content',
                'evergreen_score': 0.9,
                'confidence_score': 0.8,
                'quality_level': 'high'
            },
            {
                'chunk_id': 'chunk_1',
                'text': 'Medium quality content',
                'evergreen_score': 0.6,
                'confidence_score': 0.6,
                'quality_level': 'medium'
            },
            {
                'chunk_id': 'chunk_2',
                'text': 'Low quality content',
                'evergreen_score': 0.3,
                'confidence_score': 0.3,
                'quality_level': 'low'
            },
            {
                'chunk_id': 'chunk_3',
                'text': 'Rejected content',
                'evergreen_score': 0.1,
                'confidence_score': 0.1,
                'quality_level': 'rejected'
            }
        ]

        # Filter by medium quality
        filtered = chunker.filter_chunks(chunks, min_quality='medium')

        assert len(filtered) == 2  # high and medium
        assert all(c['quality_level'] in ['high', 'medium'] for c in filtered)


class TestTableExtractor:
    """Test TableExtractor functionality."""

    def test_extract_markdown_table(self):
        """Test extraction of Markdown tables."""
        extractor = TableExtractor()

        text = """
        | Name | Age | City |
        |------|-----|------|
        | John | 30  | NYC  |
        | Jane | 25  | LA   |
        """

        metadata = {'file_type': 'md', 'file_size': 100}

        result = extractor.extract(text, metadata)

        assert 'extracted_tables' in result
        assert 'table_count' in result
        assert 'extraction_time' in result
        assert result['table_count'] >= 1
        assert result['extraction_time'] < 25.0  # Should be within timeout

        if result['table_count'] > 0:
            table = result['extracted_tables'][0]
            assert 'headers' in table
            assert 'rows' in table
            assert len(table['headers']) == 3
            assert len(table['rows']) == 2

    def test_extract_csv_table(self):
        """Test extraction of CSV-like tables."""
        extractor = TableExtractor()

        text = """
        Name,Age,City
        John,30,NYC
        Jane,25,LA
        """

        metadata = {'file_type': 'csv', 'file_size': 100}

        result = extractor.extract(text, metadata)

        assert 'extracted_tables' in result
        assert result['table_count'] >= 1

        if result['table_count'] > 0:
            table = result['extracted_tables'][0]
            assert table['format'] == 'csv'
            assert len(table['headers']) == 3
            assert len(table['rows']) == 2

    def test_validate_table(self):
        """Test table validation."""
        extractor = TableExtractor()

        # Valid table
        valid_table = {
            'table_id': 'table_1',
            'headers': ['Name', 'Age'],
            'rows': [['John', '30'], ['Jane', '25']],
            'row_count': 2,
            'col_count': 2
        }
        assert extractor._validate_table(valid_table) is True

        # Invalid table (too few rows)
        invalid_table = {
            'table_id': 'table_2',
            'headers': ['Name', 'Age'],
            'rows': [['John', '30']],
            'row_count': 1,
            'col_count': 2
        }
        assert extractor._validate_table(invalid_table) is False


class TestDataPackager:
    """Test DataPackager functionality."""

    def test_create_package(self):
        """Test package creation."""
        packager = DataPackager()

        # Create mock state
        state = create_initial_state("/path/to/file.pdf", "test_job_123")
        state['evergreen_score'] = 0.8
        state['quality_assessment'] = ExtractionQuality.HIGH
        state['outdated_indicators'] = ['latest', 'current year']

        # Create mock chunks
        chunks = [
            {
                'chunk_id': 'chunk_0',
                'text': 'Test content',
                'content_type': 'general',
                'evergreen_score': 0.8,
                'confidence_score': 0.9,
                'quality_level': 'high',
                'length': 100,
                'word_count': 20,
                'metadata': {'source_file': 'pdf', 'chunk_index': 0}
            }
        ]

        # Create mock tables
        tables = [
            {
                'table_id': 'table_1',
                'format': 'markdown',
                'headers': ['Name', 'Age'],
                'rows': [['John', '30']],
                'row_count': 1,
                'col_count': 2,
                'metadata': {}
            }
        ]

        result = packager.create_package(state, chunks, tables)

        assert 'package' in result
        assert 'package_id' in result
        assert 'packaging_time' in result
        assert result['packaging_time'] < 5.0  # Should be fast

        package = result['package']
        assert package['version'] == '1.0'
        assert package['source_agent'] == 'archaeologist'
        assert package['target_agent'] == 'trend_jacker'
        assert 'metadata' in package
        assert 'content' in package
        assert 'tables' in package
        assert 'quality' in package
        assert 'handoff' in package

    def test_validate_package(self):
        """Test package validation."""
        packager = DataPackager()

        # Valid package
        valid_package = {
            'version': '1.0',
            'source_agent': 'archaeologist',
            'target_agent': 'trend_jacker',
            'timestamp': datetime.utcnow().isoformat(),
            'package_id': 'pkg_test_123',
            'metadata': {},
            'content': [],
            'tables': [],
            'quality': {},
            'handoff': {}
        }
        assert packager._validate_package(valid_package) is True

        # Invalid package (missing field)
        invalid_package = {
            'version': '1.0',
            'source_agent': 'archaeologist',
            # Missing required fields
        }
        assert packager._validate_package(invalid_package) is False


class TestIntegration:
    """Integration tests for complete workflow."""

    def test_end_to_end_text_processing(self):
        """Test end-to-end processing of a text file."""
        from src.agents.archaeologist import ArchaeologistAgent

        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
            This is a fundamental principle of software architecture.
            Modular design allows for better maintainability.
            The latest trends in 2023 show microservices are popular.
            Best practices include separation of concerns.
            """)
            temp_path = f.name

        try:
            agent = ArchaeologistAgent()
            result = agent.process_file(temp_path)

            assert 'success' in result
            assert 'package' in result or not result['success']
            assert 'processing_time' in result

            if result['success']:
                package = result['package']
                assert package['source_agent'] == 'archaeologist'
                assert package['target_agent'] == 'trend_jacker'
                assert len(package['content']) > 0

        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
