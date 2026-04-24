"""
Table Extractor Module for Archaeologist Agent

Extracts structured data from tables within documents.
Implements Step 4 of the Archaeologist workflow.

Time Budget: 20 seconds for table extraction
"""

import re
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TableExtractor:
    """
    Extracts and structures table data from documents.

    Capabilities:
    - Detect tables in various formats (Markdown, HTML, CSV-like)
    - Extract table headers and data rows
    - Validate table structure and quality
    - Convert tables to structured JSON format
    - Handle nested or complex table structures

    Time Budget: 20 seconds for extraction
    """

    def __init__(self):
        """Initialize TableExtractor with extraction configuration."""
        self.extraction_timeout = 20.0  # 20 second timeout

        # Table detection patterns
        self.table_patterns = {
            'markdown': r'^\|.*\|$',  # Markdown tables
            'html': r'<table[^>]*>.*?</table>',  # HTML tables
            'csv': r'^[^,\n]+(,[^,\n]+)+$',  # CSV-like tables
            'grid': r'^[+-]+\s*$',  # ASCII grid tables
        }

        # Table quality indicators
        self.min_rows = 2  # Minimum rows (including header)
        self.min_cols = 2  # Minimum columns
        self.max_empty_cells = 0.3  # Max 30% empty cells

    def extract(self, text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract tables from text content.

        Args:
            text: Raw text containing tables
            metadata: File metadata from extraction

        Returns:
            Dictionary containing:
            - extracted_tables: List of structured tables
            - table_count: Number of tables found
            - extraction_time: Time taken for extraction
            - errors: List of extraction errors (if any)

        Raises:
            TimeoutError: If extraction exceeds time budget
        """
        start_time = time.time()

        logger.info("Starting table extraction")

        try:
            # Detect tables in different formats
            tables = []

            # Try Markdown tables first
            markdown_tables = self._extract_markdown_tables(text)
            tables.extend(markdown_tables)

            # Try HTML tables
            html_tables = self._extract_html_tables(text)
            tables.extend(html_tables)

            # Try CSV-like tables
            csv_tables = self._extract_csv_tables(text)
            tables.extend(csv_tables)

            # Try ASCII grid tables
            grid_tables = self._extract_grid_tables(text)
            tables.extend(grid_tables)

            # Validate and filter tables
            validated_tables = []
            for table in tables:
                if self._validate_table(table):
                    validated_tables.append(table)

            extraction_time = time.time() - start_time

            # Check timeout
            if extraction_time > self.extraction_timeout:
                logger.warning(
                    f"Extraction exceeded time budget: {extraction_time:.2f}s > {self.extraction_timeout}s"
                )

            result = {
                'extracted_tables': validated_tables,
                'table_count': len(validated_tables),
                'extraction_time': extraction_time,
                'errors': []
            }

            logger.info(
                f"Table extraction completed in {extraction_time:.2f}s: "
                f"{len(validated_tables)} tables found"
            )

            return result

        except Exception as e:
            extraction_time = time.time() - start_time
            logger.error(f"Table extraction failed after {extraction_time:.2f}s: {str(e)}")
            raise

    def _extract_markdown_tables(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract Markdown-style tables from text.

        Args:
            text: Text containing Markdown tables

        Returns:
            List of extracted tables
        """
        tables = []
        lines = text.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Check if line looks like a Markdown table row
            if re.match(r'^\|.*\|$', line):
                # Found potential table start
                table_lines = [line]
                i += 1

                # Look for separator line
                if i < len(lines) and re.match(r'^\|[\s\-:|]+\|$', lines[i].strip()):
                    table_lines.append(lines[i].strip())
                    i += 1

                    # Collect data rows
                    while i < len(lines) and re.match(r'^\|.*\|$', lines[i].strip()):
                        table_lines.append(lines[i].strip())
                        i += 1

                    # Parse table
                    if len(table_lines) >= 2:
                        table = self._parse_markdown_table(table_lines)
                        if table:
                            tables.append(table)

            i += 1

        return tables

    def _parse_markdown_table(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """
        Parse Markdown table lines into structured format.

        Args:
            lines: List of table lines

        Returns:
            Parsed table dictionary or None if parsing fails
        """
        if len(lines) < 2:
            return None

        try:
            # Parse header row (first line)
            header_row = lines[0]
            headers = [cell.strip() for cell in header_row.split('|')[1:-1]]

            # Skip separator line (second line)
            # Parse data rows (remaining lines)
            data_rows = []
            for line in lines[2:]:
                row = [cell.strip() for cell in line.split('|')[1:-1]]
                if row:  # Skip empty rows
                    data_rows.append(row)

            if not headers or not data_rows:
                return None

            return {
                'table_id': f"table_{len(tables) + 1}",
                'format': 'markdown',
                'headers': headers,
                'rows': data_rows,
                'row_count': len(data_rows),
                'col_count': len(headers),
                'metadata': {
                    'has_separator': True,
                    'alignment': self._detect_alignment(lines[1])
                }
            }

        except Exception as e:
            logger.warning(f"Failed to parse Markdown table: {str(e)}")
            return None

    def _detect_alignment(self, separator_line: str) -> List[str]:
        """
        Detect column alignment from Markdown separator line.

        Args:
            separator_line: Separator line (e.g., |---|---|)

        Returns:
            List of alignment strings ('left', 'right', 'center', 'default')
        """
        alignments = []
        cells = separator_line.split('|')[1:-1]

        for cell in cells:
            cell = cell.strip()
            if cell.startswith(':') and cell.endswith(':'):
                alignments.append('center')
            elif cell.startswith(':'):
                alignments.append('left')
            elif cell.endswith(':'):
                alignments.append('right')
            else:
                alignments.append('default')

        return alignments

    def _extract_html_tables(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract HTML-style tables from text.

        Args:
            text: Text containing HTML tables

        Returns:
            List of extracted tables
        """
        tables = []

        try:
            # Find all table blocks
            table_blocks = re.findall(r'<table[^>]*>.*?</table>', text, re.DOTALL | re.IGNORECASE)

            for i, table_block in enumerate(table_blocks):
                table = self._parse_html_table(table_block, i)
                if table:
                    tables.append(table)

        except Exception as e:
            logger.warning(f"Failed to extract HTML tables: {str(e)}")

        return tables

    def _parse_html_table(self, table_block: str, table_index: int) -> Optional[Dict[str, Any]]:
        """
        Parse HTML table block into structured format.

        Args:
            table_block: HTML table block
            table_index: Table index for ID generation

        Returns:
            Parsed table dictionary or None if parsing fails
        """
        try:
            # Extract headers (th elements)
            headers = re.findall(r'<th[^>]*>(.*?)</th>', table_block, re.DOTALL | re.IGNORECASE)
            headers = [re.sub(r'<[^>]+>', '', h).strip() for h in headers]

            # Extract data rows (tr elements with td)
            row_blocks = re.findall(r'<tr[^>]*>(.*?)</tr>', table_block, re.DOTALL | re.IGNORECASE)

            data_rows = []
            for row_block in row_blocks:
                # Check if row contains td elements (data cells)
                if re.search(r'<td', row_block, re.IGNORECASE):
                    cells = re.findall(r'<td[^>]*>(.*?)</td>', row_block, re.DOTALL | re.IGNORECASE)
                    row = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                    if row:  # Skip empty rows
                        data_rows.append(row)

            if not headers or not data_rows:
                return None

            return {
                'table_id': f"table_{table_index}",
                'format': 'html',
                'headers': headers,
                'rows': data_rows,
                'row_count': len(data_rows),
                'col_count': len(headers),
                'metadata': {
                    'html_parsed': True
                }
            }

        except Exception as e:
            logger.warning(f"Failed to parse HTML table: {str(e)}")
            return None

    def _extract_csv_tables(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract CSV-like tables from text.

        Args:
            text: Text containing CSV-like tables

        Returns:
            List of extracted tables
        """
        tables = []
        lines = text.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check if line looks like a CSV row
            if re.match(r'^[^,\n]+(,[^,\n]+)+$', line):
                # Found potential CSV table start
                table_lines = [line]
                i += 1

                # Collect consecutive CSV-like lines
                while i < len(lines) and re.match(r'^[^,\n]+(,[^,\n]+)*$', lines[i].strip()):
                    table_lines.append(lines[i].strip())
                    i += 1

                # Parse table
                if len(table_lines) >= 2:
                    table = self._parse_csv_table(table_lines)
                    if table:
                        tables.append(table)

            i += 1

        return tables

    def _parse_csv_table(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """
        Parse CSV table lines into structured format.

        Args:
            lines: List of CSV table lines

        Returns:
            Parsed table dictionary or None if parsing fails
        """
        if len(lines) < 2:
            return None

        try:
            # Parse header row (first line)
            headers = [cell.strip() for cell in lines[0].split(',')]

            # Parse data rows (remaining lines)
            data_rows = []
            for line in lines[1:]:
                row = [cell.strip() for cell in line.split(',')]
                if row:  # Skip empty rows
                    data_rows.append(row)

            if not headers or not data_rows:
                return None

            return {
                'table_id': f"table_{len(tables) + 1}",
                'format': 'csv',
                'headers': headers,
                'rows': data_rows,
                'row_count': len(data_rows),
                'col_count': len(headers),
                'metadata': {
                    'delimiter': ','
                }
            }

        except Exception as e:
            logger.warning(f"Failed to parse CSV table: {str(e)}")
            return None

    def _extract_grid_tables(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract ASCII grid tables from text.

        Args:
            text: Text containing ASCII grid tables

        Returns:
            List of extracted tables
        """
        tables = []
        lines = text.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check if line looks like a grid separator
            if re.match(r'^[+-]+\s*$', line):
                # Found potential grid table
                table_lines = [line]
                i += 1

                # Collect table content
                while i < len(lines):
                    current_line = lines[i].strip()

                    # Check if we've reached the end of the table
                    if re.match(r'^[+-]+\s*$', current_line):
                        table_lines.append(current_line)
                        i += 1
                        break

                    # Check if line looks like table content
                    if re.match(r'^\|.*\|$', current_line):
                        table_lines.append(current_line)

                    i += 1

                # Parse table
                if len(table_lines) >= 3:
                    table = self._parse_grid_table(table_lines)
                    if table:
                        tables.append(table)

            i += 1

        return tables

    def _parse_grid_table(self, lines: List[str]) -> Optional[Dict[str, Any]]:
        """
        Parse ASCII grid table into structured format.

        Args:
            lines: List of grid table lines

        Returns:
            Parsed table dictionary or None if parsing fails
        """
        if len(lines) < 3:
            return None

        try:
            # Parse header row (second line, after first separator)
            if len(lines) < 2:
                return None

            header_line = lines[1]
            headers = [cell.strip() for cell in header_line.split('|')[1:-1]]

            # Parse data rows (lines between separators)
            data_rows = []
            for line in lines[2:-1]:  # Skip first and last separators
                if re.match(r'^\|.*\|$', line):
                    row = [cell.strip() for cell in line.split('|')[1:-1]]
                    if row:  # Skip empty rows
                        data_rows.append(row)

            if not headers or not data_rows:
                return None

            return {
                'table_id': f"table_{len(tables) + 1}",
                'format': 'grid',
                'headers': headers,
                'rows': data_rows,
                'row_count': len(data_rows),
                'col_count': len(headers),
                'metadata': {
                    'grid_style': True
                }
            }

        except Exception as e:
            logger.warning(f"Failed to parse grid table: {str(e)}")
            return None

    def _validate_table(self, table: Dict[str, Any]) -> bool:
        """
        Validate table quality and structure.

        Args:
            table: Table dictionary to validate

        Returns:
            True if table is valid, False otherwise
        """
        # Check minimum dimensions
        row_count = table.get('row_count', 0)
        col_count = table.get('col_count', 0)

        if row_count < self.min_rows or col_count < self.min_cols:
            return False

        # Check for empty cells
        rows = table.get('rows', [])
        if not rows:
            return False

        total_cells = sum(len(row) for row in rows)
        empty_cells = sum(1 for row in rows for cell in row if not cell.strip())

        if total_cells > 0 and (empty_cells / total_cells) > self.max_empty_cells:
            return False

        # Check for consistent column count
        col_counts = [len(row) for row in rows]
        if len(set(col_counts)) > 1:  # Inconsistent column counts
            return False

        return True

    def convert_to_json(self, table: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert table to JSON-serializable format.

        Args:
            table: Table dictionary

        Returns:
            JSON-serializable table dictionary
        """
        return {
            'table_id': table.get('table_id'),
            'format': table.get('format'),
            'headers': table.get('headers', []),
            'data': [
                dict(zip(table.get('headers', []), row))
                for row in table.get('rows', [])
            ],
            'row_count': table.get('row_count', 0),
            'col_count': table.get('col_count', 0),
            'metadata': table.get('metadata', {})
        }


# Convenience function for quick table extraction
def extract_tables(text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to extract tables from text.

    Args:
        text: Text containing tables
        metadata: File metadata

    Returns:
        Dictionary with extracted tables
    """
    extractor = TableExtractor()
    return extractor.extract(text, metadata)
