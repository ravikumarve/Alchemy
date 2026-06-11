"""
Text Extractor Module for Archaeologist Agent

Handles extraction of raw text and metadata from PDF, TXT, and HTML files
using lightweight libraries (PyPDF2, BeautifulSoup, built-in reader).
Implements Step 2 of the Archaeologist workflow.

Time Budget: 2 seconds for extraction
"""

import os
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextExtractor:
    """
    Extracts text and metadata from various file formats.

    Supported formats:
    - PDF (.pdf) via PyPDF2
    - Plain Text (.txt) via built-in reader
    - HTML (.html, .htm) via BeautifulSoup

    Time Budget: 2 seconds per file
    """

    def __init__(self):
        """Initialize TextExtractor configuration."""
        self.extraction_timeout = 2.0  # 2 second timeout
        self.supported_formats = ['.pdf', '.txt', '.html', '.htm']

    def extract(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text and metadata from a file.

        Args:
            file_path: Path to the file to extract

        Returns:
            Dictionary containing:
            - raw_text: Extracted text content
            - metadata: File metadata (size, type, pages, etc.)
            - errors: List of extraction errors (if any)
            - extraction_time: Time taken for extraction

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
            TimeoutError: If extraction exceeds time budget
        """
        start_time = time.time()

        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Validate file format
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_formats:
            raise ValueError(
                f"Unsupported file format: {file_ext}. "
                f"Supported formats: {', '.join(self.supported_formats)}"
            )

        logger.info(f"Starting extraction for {file_path}")

        try:
            # Extract based on file type
            if file_ext == '.pdf':
                result = self._extract_pdf(file_path, start_time)
            elif file_ext in ['.html', '.htm']:
                result = self._extract_html(file_path, start_time)
            else:  # .txt
                result = self._extract_text(file_path, start_time)

            extraction_time = time.time() - start_time

            # Check timeout
            if extraction_time > self.extraction_timeout:
                logger.warning(
                    f"Extraction exceeded time budget: {extraction_time:.2f}s > {self.extraction_timeout}s"
                )
                result['timeout_warning'] = True

            result['extraction_time'] = extraction_time
            logger.info(f"Extraction completed in {extraction_time:.2f}s")

            return result

        except Exception as e:
            extraction_time = time.time() - start_time
            logger.error(f"Extraction failed after {extraction_time:.2f}s: {str(e)}")
            raise

    def _extract_pdf(self, file_path: str, start_time: float) -> Dict[str, Any]:
        """
        Extract text from PDF file.

        Uses PyPDF2 for lightweight extraction. Falls back if unavailable.

        Args:
            file_path: Path to PDF file
            start_time: Extraction start time for timeout checking

        Returns:
            Dictionary with extracted text and metadata
        """
        # Check timeout before extraction
        if time.time() - start_time > self.extraction_timeout * 0.8:
            raise TimeoutError("Approaching extraction timeout")

        try:
            import PyPDF2

            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                raw_text = ""

                for page in pdf_reader.pages:
                    raw_text += page.extract_text() + "\n"

                metadata = {
                    'file_type': 'pdf',
                    'file_size': os.path.getsize(file_path),
                    'num_pages': num_pages,
                    'extraction_method': 'PyPDF2',
                    'extraction_strategy': 'basic'
                }

                return {
                    'raw_text': raw_text,
                    'metadata': metadata,
                    'errors': []
                }

        except ImportError:
            raise ImportError(
                "PyPDF2 is required for PDF extraction. "
                "Install it: pip install PyPDF2"
            )

    def _extract_html(self, file_path: str, start_time: float) -> Dict[str, Any]:
        """
        Extract text from HTML file using BeautifulSoup.

        Args:
            file_path: Path to HTML file
            start_time: Extraction start time for timeout checking

        Returns:
            Dictionary with extracted text and metadata
        """
        # Check timeout before extraction
        if time.time() - start_time > self.extraction_timeout * 0.8:
            raise TimeoutError("Approaching extraction timeout")

        try:
            from bs4 import BeautifulSoup

            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            raw_text = soup.get_text(separator='\n', strip=True)

            metadata = {
                'file_type': 'html',
                'file_size': os.path.getsize(file_path),
                'extraction_method': 'BeautifulSoup',
                'extraction_strategy': 'basic'
            }

            return {
                'raw_text': raw_text,
                'metadata': metadata,
                'errors': []
            }

        except ImportError:
            raise ImportError(
                "BeautifulSoup is required for HTML extraction. "
                "Install it: pip install beautifulsoup4"
            )

    def _extract_text(self, file_path: str, start_time: float) -> Dict[str, Any]:
        """
        Extract text from plain text file.

        Args:
            file_path: Path to text file
            start_time: Extraction start time for timeout checking

        Returns:
            Dictionary with extracted text and metadata
        """
        # Check timeout before extraction
        if time.time() - start_time > self.extraction_timeout * 0.8:
            raise TimeoutError("Approaching extraction timeout")

        with open(file_path, 'r', encoding='utf-8') as file:
            raw_text = file.read()

        metadata = {
            'file_type': 'txt',
            'file_size': os.path.getsize(file_path),
            'num_characters': len(raw_text),
            'num_words': len(raw_text.split()),
            'extraction_method': 'built-in',
            'extraction_strategy': 'basic'
        }

        return {
            'raw_text': raw_text,
            'metadata': metadata,
            'errors': []
        }

    def validate_extraction_quality(self, result: Dict[str, Any]) -> bool:
        """
        Validate the quality of extraction results.

        Args:
            result: Extraction result dictionary

        Returns:
            True if extraction quality is acceptable, False otherwise
        """
        raw_text = result.get('raw_text', '')
        metadata = result.get('metadata', {})
        errors = result.get('errors', [])

        # Check for critical errors
        if any('critical' in error.lower() for error in errors):
            return False

        # Check if text was extracted
        if not raw_text or len(raw_text.strip()) < 10:
            return False

        # Check if metadata is present
        if not metadata:
            return False

        # Check extraction time
        extraction_time = result.get('extraction_time', 0)
        if extraction_time > self.extraction_timeout * 2:
            logger.warning(f"Extraction took too long: {extraction_time:.2f}s")
            return False

        return True


# Convenience function for quick extraction
def extract_text(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to extract text from a file.

    Args:
        file_path: Path to the file to extract

    Returns:
        Dictionary with extracted text and metadata
    """
    extractor = TextExtractor()
    return extractor.extract(file_path)
