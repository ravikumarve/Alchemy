"""
End-to-End Orchestration Script for ALCHEMY Pipeline

Chains all three agents: Archaeologist → Trend-Jacker → Visionary
Reads from raw_ore/, writes final output to processed_gold/

Usage:
    python src/pipeline/orchestrator.py [file_path] [asset_type]

If no file_path is provided, processes all files in raw_ore/
"""

import sys
import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.archaeologist import ArchaeologistAgent
from src.agents.trend_jacker import TrendJackerAgent
from src.agents.visionary import VisionaryAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AlchemyOrchestrator:
    """
    Master orchestrator for the ALCHEMY content transmutation pipeline.

    Chains Archaeologist → Trend-Jacker → Visionary to transform
    raw content into Gumroad-ready digital assets.
    """

    def __init__(self):
        """Initialize orchestrator with all three agents."""
        self.archaeologist = ArchaeologistAgent()
        self.trend_jacker = TrendJackerAgent()
        self.visionary = VisionaryAgent()

        self.raw_dir = Path("raw_ore")
        self.output_dir = Path("processed_gold")

        # Ensure directories exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("AlchemyOrchestrator initialized")

    def process_file(self, file_path: str,
                     asset_type: str = "youtube_short") -> Dict[str, Any]:
        """
        Process a single file through the complete pipeline.

        Args:
            file_path: Path to input file
            asset_type: Target asset type

        Returns:
            Dictionary with complete processing results
        """
        total_start = time.time()
        file_name = Path(file_path).name
        logger.info(f"=" * 60)
        logger.info(f"Starting ALCHEMY pipeline for: {file_name}")
        logger.info(f"=" * 60)

        result: Dict[str, Any] = {
            'file': file_name,
            'success': False,
            'stages': {},
            'total_time': 0.0,
            'errors': []
        }

        try:
            # Stage 1: Archaeologist
            logger.info("\n[STAGE 1/3] Archaeologist - Extracting content...")
            stage_start = time.time()
            arch_result = self.archaeologist.process_file(file_path)
            stage_time = time.time() - stage_start

            result['stages']['archaeologist'] = {
                'success': arch_result['success'],
                'time': stage_time,
                'package_id': arch_result.get('package', {}).get('package_id', 'N/A'),
                'chunks': len(arch_result.get('package', {}).get('content', [])),
                'tables': len(arch_result.get('package', {}).get('tables', []))
            }

            if not arch_result['success']:
                raise Exception(f"Archaeologist failed: {arch_result.get('errors', ['Unknown error'])}")

            logger.info(f"  ✓ Archaeologist completed in {stage_time:.2f}s")

            # Stage 2: Trend-Jacker
            logger.info("\n[STAGE 2/3] Trend-Jacker - Contextualizing content...")
            stage_start = time.time()
            tj_result = self.trend_jacker.process(arch_result['package'])
            stage_time = time.time() - stage_start

            result['stages']['trend_jacker'] = {
                'success': tj_result['status'] == 'completed',
                'time': stage_time,
                'package_id': tj_result.get('package_id', 'N/A'),
                'hooks': len(tj_result.get('package', {}).get('hooks', [])),
                'engagement_score': tj_result.get('package', {}).get('engagement_score', 0.0)
            }

            if tj_result['status'] != 'completed':
                raise Exception(f"Trend-Jacker failed with status: {tj_result['status']}")

            logger.info(f"  ✓ Trend-Jacker completed in {stage_time:.2f}s")

            # Stage 3: Visionary
            logger.info("\n[STAGE 3/3] Visionary - Generating media assets...")
            stage_start = time.time()
            vis_result = self.visionary.process(tj_result['package'], asset_type)
            stage_time = time.time() - stage_start

            result['stages']['visionary'] = {
                'success': vis_result['status'] == 'completed',
                'time': stage_time,
                'package_id': vis_result.get('package_id', 'N/A'),
                'output_path': vis_result.get('output_path', 'N/A'),
                'scenes': vis_result.get('package', {}).get('metadata', {}).get('scene_count', 0),
                'prompts': vis_result.get('package', {}).get('metadata', {}).get('scene_count', 0)
            }

            if vis_result['status'] != 'completed':
                raise Exception(f"Visionary failed with status: {vis_result['status']}")

            logger.info(f"  ✓ Visionary completed in {stage_time:.2f}s")

            # Success
            result['success'] = True
            result['output_path'] = vis_result.get('output_path', '')
            result['final_package_id'] = vis_result.get('package_id', '')

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            result['errors'].append(str(e))

        result['total_time'] = time.time() - total_start

        # Print summary
        logger.info(f"\n{'=' * 60}")
        logger.info(f"PIPELINE {'COMPLETED' if result['success'] else 'FAILED'}")
        logger.info(f"Total time: {result['total_time']:.2f}s")
        logger.info(f"File: {file_name}")
        if result['success']:
            logger.info(f"Output: {result.get('output_path', 'N/A')}")
        else:
            logger.info(f"Errors: {result['errors']}")
        logger.info(f"{'=' * 60}")

        return result

    def process_all(self, asset_type: str = "youtube_short") -> Dict[str, Any]:
        """
        Process all files in raw_ore/ directory.

        Args:
            asset_type: Target asset type

        Returns:
            Dictionary with batch processing results
        """
        files = list(self.raw_dir.glob("*"))
        files = [f for f in files if f.suffix.lower() in ['.pdf', '.txt', '.html', '.htm']]

        if not files:
            logger.warning("No files found in raw_ore/")
            return {'processed': 0, 'results': []}

        logger.info(f"Found {len(files)} file(s) to process")

        results = []
        for file_path in files:
            result = self.process_file(str(file_path), asset_type)
            results.append(result)

        successful = sum(1 for r in results if r['success'])
        logger.info(f"\nBatch complete: {successful}/{len(files)} successful")

        return {
            'processed': len(files),
            'successful': successful,
            'failed': len(files) - successful,
            'results': results
        }


def main():
    """Main entry point for orchestrator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="ALCHEMY Content Transmutation Pipeline"
    )
    parser.add_argument(
        'file', nargs='?',
        help='Path to file to process (if omitted, processes all files in raw_ore/)'
    )
    parser.add_argument(
        '--asset-type', default='youtube_short',
        choices=['youtube_short', 'tiktok', 'instagram_reel', 'gumroad_pack', 'b_roll_library'],
        help='Target asset type (default: youtube_short)'
    )

    args = parser.parse_args()

    orchestrator = AlchemyOrchestrator()

    if args.file:
        result = orchestrator.process_file(args.file, args.asset_type)
        if not result['success']:
            sys.exit(1)
    else:
        batch_result = orchestrator.process_all(args.asset_type)
        if batch_result['failed'] > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()