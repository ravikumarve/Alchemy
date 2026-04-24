"""
Data Packager Module for Archaeologist Agent

Creates final JSON package for handoff to Trend-Jacker agent.
Implements Step 7 of the Archaeologist workflow.

Time Budget: 3 seconds for packaging
"""

import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPackager:
    """
    Packages extracted and analyzed content into a structured JSON format
    for handoff to the Trend-Jacker agent.

    Package Structure:
    - metadata: Package metadata (timestamp, source, quality metrics)
    - content: Filtered and structured content chunks
    - tables: Extracted and validated table data
    - quality: Overall quality assessment and confidence scores
    - handoff: Trend-Jacker specific handoff information

    Time Budget: 3 seconds for packaging
    """

    def __init__(self):
        """Initialize DataPackager with packaging configuration."""
        self.packaging_timeout = 3.0  # 3 second timeout

        # Handoff contract specification
        self.handoff_schema = {
            'version': '1.0',
            'source_agent': 'archaeologist',
            'target_agent': 'trend_jacker',
            'timestamp': str,
            'package_id': str,
            'metadata': dict,
            'content': list,
            'tables': list,
            'quality': dict,
            'handoff': dict
        }

    def create_package(
        self,
        state: Dict[str, Any],
        filtered_chunks: List[Dict[str, Any]],
        extracted_tables: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create final JSON package for Trend-Jacker handoff.

        Args:
            state: ArchaeologistState with processing results
            filtered_chunks: Quality-filtered content chunks
            extracted_tables: Extracted and validated tables

        Returns:
            Dictionary containing:
            - package: Complete JSON package for handoff
            - package_id: Unique package identifier
            - packaging_time: Time taken for packaging

        Raises:
            TimeoutError: If packaging exceeds time budget
        """
        start_time = time.time()

        logger.info("Starting package creation")

        try:
            # Generate package ID
            package_id = self._generate_package_id(state)

            # Create package structure
            package = {
                'version': '1.0',
                'source_agent': 'archaeologist',
                'target_agent': 'trend_jacker',
                'timestamp': datetime.utcnow().isoformat(),
                'package_id': package_id,
                'metadata': self._create_metadata(state),
                'content': self._package_content(filtered_chunks),
                'tables': self._package_tables(extracted_tables),
                'quality': self._create_quality_assessment(state, filtered_chunks),
                'handoff': self._create_handoff_info(state)
            }

            # Validate package structure
            if not self._validate_package(package):
                raise ValueError("Package validation failed")

            packaging_time = time.time() - start_time

            # Check timeout
            if packaging_time > self.packaging_timeout:
                logger.warning(
                    f"Packaging exceeded time budget: {packaging_time:.2f}s > {self.packaging_timeout}s"
                )

            result = {
                'package': package,
                'package_id': package_id,
                'packaging_time': packaging_time
            }

            logger.info(
                f"Package created in {packaging_time:.2f}s: "
                f"package_id={package_id}, "
                f"chunks={len(filtered_chunks)}, "
                f"tables={len(extracted_tables)}"
            )

            return result

        except Exception as e:
            packaging_time = time.time() - start_time
            logger.error(f"Package creation failed after {packaging_time:.2f}s: {str(e)}")
            raise

    def _generate_package_id(self, state: Dict[str, Any]) -> str:
        """
        Generate unique package identifier.

        Args:
            state: ArchaeologistState

        Returns:
            Unique package ID string
        """
        job_id = state.get('job_id', 'unknown')
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"pkg_{job_id}_{timestamp}"

    def _create_metadata(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create package metadata section.

        Args:
            state: ArchaeologistState

        Returns:
            Metadata dictionary
        """
        file_metadata = state.get('file_metadata', {})

        return {
            'source_file': state.get('file_path', 'unknown'),
            'file_type': file_metadata.get('file_type', 'unknown'),
            'file_size': file_metadata.get('file_size', 0),
            'extraction_method': file_metadata.get('extraction_method', 'unknown'),
            'processing_time': state.get('processing_time', 0.0),
            'step_times': state.get('step_times', {}),
            'retry_count': state.get('retry_count', 0),
            'fallback_triggered': state.get('fallback_triggered', False)
        }

    def _package_content(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Package content chunks for handoff.

        Args:
            chunks: Filtered content chunks

        Returns:
            List of packaged content chunks
        """
        packaged_chunks = []

        for chunk in chunks:
            packaged_chunk = {
                'chunk_id': chunk.get('chunk_id'),
                'text': chunk.get('text'),
                'content_type': chunk.get('content_type'),
                'evergreen_score': chunk.get('evergreen_score'),
                'confidence_score': chunk.get('confidence_score'),
                'quality_level': chunk.get('quality_level'),
                'length': chunk.get('length'),
                'word_count': chunk.get('word_count'),
                'metadata': chunk.get('metadata', {})
            }
            packaged_chunks.append(packaged_chunk)

        return packaged_chunks

    def _package_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Package extracted tables for handoff.

        Args:
            tables: Extracted tables

        Returns:
            List of packaged tables
        """
        packaged_tables = []

        for table in tables:
            packaged_table = {
                'table_id': table.get('table_id'),
                'format': table.get('format'),
                'headers': table.get('headers', []),
                'row_count': table.get('row_count', 0),
                'col_count': table.get('col_count', 0),
                'data': [
                    dict(zip(table.get('headers', []), row))
                    for row in table.get('rows', [])
                ],
                'metadata': table.get('metadata', {})
            }
            packaged_tables.append(packaged_table)

        return packaged_tables

    def _create_quality_assessment(
        self,
        state: Dict[str, Any],
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create quality assessment section.

        Args:
            state: ArchaeologistState
            chunks: Filtered content chunks

        Returns:
            Quality assessment dictionary
        """
        # Calculate quality metrics
        if chunks:
            avg_evergreen = sum(c.get('evergreen_score', 0) for c in chunks) / len(chunks)
            avg_confidence = sum(c.get('confidence_score', 0) for c in chunks) / len(chunks)

            quality_distribution = {
                'high': sum(1 for c in chunks if c.get('quality_level') == 'high'),
                'medium': sum(1 for c in chunks if c.get('quality_level') == 'medium'),
                'low': sum(1 for c in chunks if c.get('quality_level') == 'low'),
                'rejected': sum(1 for c in chunks if c.get('quality_level') == 'rejected')
            }
        else:
            avg_evergreen = 0.0
            avg_confidence = 0.0
            quality_distribution = {'high': 0, 'medium': 0, 'low': 0, 'rejected': 0}

        return {
            'overall_evergreen_score': state.get('evergreen_score', 0.0),
            'overall_quality': state.get('quality_assessment', 'unknown'),
            'average_evergreen_score': avg_evergreen,
            'average_confidence_score': avg_confidence,
            'quality_distribution': quality_distribution,
            'total_chunks': len(chunks),
            'outdated_indicators': state.get('outdated_indicators', [])
        }

    def _create_handoff_info(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create Trend-Jacker specific handoff information.

        Args:
            state: ArchaeologistState

        Returns:
            Handoff information dictionary
        """
        return {
            'processing_complete': True,
            'ready_for_contextualization': True,
            'suggested_hooks': self._generate_suggested_hooks(state),
            'content_themes': self._extract_content_themes(state),
            'processing_notes': [
                "Content has been filtered for evergreen quality",
                "Outdated indicators have been identified and tagged",
                "Tables have been extracted and structured",
                "Ready for trend-jacking and contextualization"
            ]
        }

    def _generate_suggested_hooks(self, state: Dict[str, Any]) -> List[str]:
        """
        Generate suggested content hooks for Trend-Jacker.

        Args:
            state: ArchaeologistState

        Returns:
            List of suggested hook themes
        """
        outdated_indicators = state.get('outdated_indicators', [])
        evergreen_score = state.get('evergreen_score', 0.0)

        hooks = []

        # Suggest hooks based on evergreen score
        if evergreen_score > 0.8:
            hooks.append("Timeless principles that still apply today")
        elif evergreen_score > 0.5:
            hooks.append("Foundational concepts with modern relevance")
        else:
            hooks.append("Historical context for understanding current trends")

        # Suggest hooks based on outdated indicators
        if outdated_indicators:
            hooks.append("Evolution of ideas over time")
            hooks.append("How concepts have changed")

        return hooks

    def _extract_content_themes(self, state: Dict[str, Any]) -> List[str]:
        """
        Extract main content themes from processed data.

        Args:
            state: ArchaeologistState

        Returns:
            List of content themes
        """
        content_chunks = state.get('content_chunks', [])
        themes = set()

        for chunk in content_chunks:
            content_type = chunk.get('content_type', 'general')
            if content_type != 'general':
                themes.add(content_type)

        return sorted(list(themes))

    def _validate_package(self, package: Dict[str, Any]) -> bool:
        """
        Validate package structure against handoff schema.

        Args:
            package: Package dictionary to validate

        Returns:
            True if package is valid, False otherwise
        """
        # Check required fields
        required_fields = [
            'version', 'source_agent', 'target_agent',
            'timestamp', 'package_id', 'metadata',
            'content', 'tables', 'quality', 'handoff'
        ]

        for field in required_fields:
            if field not in package:
                logger.error(f"Missing required field: {field}")
                return False

        # Check field types
        if not isinstance(package['content'], list):
            logger.error("Content must be a list")
            return False

        if not isinstance(package['tables'], list):
            logger.error("Tables must be a list")
            return False

        if not isinstance(package['quality'], dict):
            logger.error("Quality must be a dictionary")
            return False

        if not isinstance(package['handoff'], dict):
            logger.error("Handoff must be a dictionary")
            return False

        return True

    def save_package(self, package: Dict[str, Any], output_path: str) -> bool:
        """
        Save package to JSON file.

        Args:
            package: Package dictionary
            output_path: Path to save package

        Returns:
            True if save successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(package, f, indent=2, ensure_ascii=False)

            logger.info(f"Package saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save package: {str(e)}")
            return False

    def load_package(self, input_path: str) -> Optional[Dict[str, Any]]:
        """
        Load package from JSON file.

        Args:
            input_path: Path to load package from

        Returns:
            Package dictionary or None if loading fails
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                package = json.load(f)

            # Validate package
            if self._validate_package(package):
                logger.info(f"Package loaded from {input_path}")
                return package
            else:
                logger.error("Loaded package failed validation")
                return None

        except Exception as e:
            logger.error(f"Failed to load package: {str(e)}")
            return None


# Convenience function for quick packaging
def create_package(
    state: Dict[str, Any],
    filtered_chunks: List[Dict[str, Any]],
    extracted_tables: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Convenience function to create package for handoff.

    Args:
        state: ArchaeologistState
        filtered_chunks: Quality-filtered content chunks
        extracted_tables: Extracted tables

    Returns:
        Dictionary with package and metadata
    """
    packager = DataPackager()
    return packager.create_package(state, filtered_chunks, extracted_tables)
