#!/usr/bin/env python3
"""
ALCHEMY Unattended Processing Daemon

Watches raw_ore/ for new files and processes them through the full pipeline.
Designed for cron-based (one-shot) or continuous (watch) operation.

Usage:
    # One-shot: process all pending files (for cron)
    python scripts/process-daemon.py --oneshot

    # Continuous: watch for new files (long-running daemon)
    python scripts/process-daemon.py --watch

    # Process a specific file
    python scripts/process-daemon.py --file /path/to/file.txt

    # Dry run (show what would be processed)
    python scripts/process-daemon.py --oneshot --dry-run
"""

import os
import sys
import json
import time
import argparse
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Set

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline.orchestrator import AlchemyOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent.parent / 'logs' / 'daemon.log')
    ]
)
logger = logging.getLogger('alchemy-daemon')


class ProcessingTracker:
    """Tracks processed files to avoid re-processing."""

    def __init__(self, state_file: str = 'processed_gold/.processed_state.json'):
        self.state_file = Path(state_file)
        self.processed: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """Load processed state from disk."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    self.processed = json.load(f)
                logger.info(f"Loaded {len(self.processed)} processed file records")
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Could not load state file: {e}")
                self.processed = {}

    def _save(self) -> None:
        """Save processed state to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.processed, f, indent=2)

    def is_processed(self, file_path: str) -> bool:
        """Check if a file has already been processed (by path + hash)."""
        if file_path not in self.processed:
            return False
        current_hash = self._file_hash(file_path)
        stored_hash = self.processed[file_path].get('hash', '')
        return current_hash == stored_hash

    def mark_processed(self, file_path: str, result: Dict[str, Any]) -> None:
        """Mark a file as successfully processed."""
        self.processed[file_path] = {
            'hash': self._file_hash(file_path),
            'timestamp': datetime.utcnow().isoformat(),
            'success': result.get('success', False),
            'total_time': result.get('total_time', 0),
            'output_path': result.get('output_path', ''),
            'final_package_id': result.get('final_package_id', ''),
            'file_size': os.path.getsize(file_path)
        }
        self._save()

    def mark_failed(self, file_path: str, error: str) -> None:
        """Mark a file as failed."""
        self.processed[file_path] = {
            'hash': self._file_hash(file_path),
            'timestamp': datetime.utcnow().isoformat(),
            'success': False,
            'error': error
        }
        self._save()

    def _file_hash(self, file_path: str) -> str:
        """Compute a quick hash of a file to detect changes."""
        try:
            h = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    h.update(chunk)
            return h.hexdigest()
        except OSError:
            return ''

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of processed files."""
        total = len(self.processed)
        succeeded = sum(1 for v in self.processed.values() if v.get('success'))
        failed = total - succeeded
        return {
            'total': total,
            'succeeded': succeeded,
            'failed': failed,
            'last_run': max((v['timestamp'] for v in self.processed.values()), default='N/A')
        }


def find_pending_files(raw_dir: str, tracker: ProcessingTracker,
                       supported_extensions: Optional[Set[str]] = None) -> List[Path]:
    """Find all unprocessed files in the raw directory."""
    if supported_extensions is None:
        supported_extensions = {'.txt', '.pdf', '.html', '.htm'}

    raw_path = Path(raw_dir)
    if not raw_path.exists():
        logger.warning(f"Raw directory not found: {raw_dir}")
        return []

    pending = []
    for f in sorted(raw_path.iterdir()):
        if f.is_file() and f.suffix.lower() in supported_extensions:
            if not tracker.is_processed(str(f)):
                pending.append(f)

    return pending


def process_files(file_paths: List[Path], tracker: ProcessingTracker,
                  asset_type: str = "youtube_short",
                  dry_run: bool = False) -> Dict[str, Any]:
    """Process a list of files through the pipeline."""
    orchestrator = AlchemyOrchestrator()

    results = {
        'processed': 0,
        'succeeded': 0,
        'failed': 0,
        'total_time': 0.0,
        'files': []
    }

    for file_path in file_paths:
        if dry_run:
            logger.info(f"[DRY RUN] Would process: {file_path.name}")
            results['processed'] += 1
            continue

        logger.info(f"Processing: {file_path.name} ({file_path.stat().st_size} bytes)")

        try:
            start = time.time()
            result = orchestrator.process_file(str(file_path), asset_type)
            elapsed = time.time() - start

            if result.get('success'):
                tracker.mark_processed(str(file_path), result)
                results['succeeded'] += 1
                logger.info(f"  ✓ {file_path.name} completed in {elapsed:.2f}s")
            else:
                error_msg = '; '.join(result.get('errors', ['Unknown error']))
                tracker.mark_failed(str(file_path), error_msg)
                results['failed'] += 1
                logger.error(f"  ✗ {file_path.name} failed: {error_msg}")

            results['processed'] += 1
            results['total_time'] += elapsed
            results['files'].append({
                'file': file_path.name,
                'success': result.get('success', False),
                'time': elapsed,
                'output_path': result.get('output_path', ''),
                'package_id': result.get('final_package_id', '')
            })

        except Exception as e:
            tracker.mark_failed(str(file_path), str(e))
            results['failed'] += 1
            results['processed'] += 1
            logger.error(f"  ✗ {file_path.name} crashed: {e}")
            results['files'].append({
                'file': file_path.name,
                'success': False,
                'error': str(e)
            })

    return results


def watch_mode(raw_dir: str, tracker: ProcessingTracker,
               poll_interval: int = 30, asset_type: str = "youtube_short") -> None:
    """Continuously watch for new files."""
    logger.info(f"Starting watch mode on {raw_dir}/ (poll every {poll_interval}s)")
    logger.info("Press Ctrl+C to stop")

    while True:
        try:
            pending = find_pending_files(raw_dir, tracker)
            if pending:
                logger.info(f"Found {len(pending)} pending files")
                results = process_files(pending, tracker, asset_type)

                # Log summary
                summary = tracker.get_summary()
                logger.info(
                    f"Batch complete: {results['succeeded']} succeeded, "
                    f"{results['failed']} failed "
                    f"(all-time: {summary['succeeded']}/{summary['total']})"
                )
            else:
                logger.debug(f"No pending files (next check in {poll_interval}s)")

            time.sleep(poll_interval)

        except KeyboardInterrupt:
            logger.info("Watch mode stopped by user")
            break
        except Exception as e:
            logger.error(f"Watch loop error: {e}", exc_info=True)
            time.sleep(poll_interval)


def one_shot_mode(raw_dir: str, tracker: ProcessingTracker,
                  asset_type: str = "youtube_short",
                  dry_run: bool = False) -> Dict[str, Any]:
    """Process all pending files and exit."""
    pending = find_pending_files(raw_dir, tracker)
    if not pending:
        summary = tracker.get_summary()
        logger.info(f"No pending files. All-time: {summary['succeeded']}/{summary['total']}")
        return {'processed': 0, 'succeeded': 0, 'failed': 0, 'total_time': 0, 'files': []}

    logger.info(f"Found {len(pending)} pending files for one-shot processing")
    results = process_files(pending, tracker, asset_type, dry_run)

    summary = tracker.get_summary()
    logger.info(f"One-shot complete: {results['succeeded']}/{results['processed']} succeeded")
    logger.info(f"All-time: {summary['succeeded']}/{summary['total']}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description='ALCHEMY Unattended Processing Daemon',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--oneshot', action='store_true',
                      help='Process all pending files and exit (for cron)')
    mode.add_argument('--watch', action='store_true',
                      help='Continuously watch for new files')
    mode.add_argument('--file', type=str,
                      help='Process a specific file')

    parser.add_argument('--raw-dir', type=str, default='raw_ore',
                        help='Directory to watch for input files')
    parser.add_argument('--asset-type', type=str, default='youtube_short',
                        choices=['youtube_short', 'tiktok', 'instagram_reel', 'blog_post'],
                        help='Target asset type')
    parser.add_argument('--poll-interval', type=int, default=30,
                        help='Poll interval in seconds (watch mode)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be processed without processing')

    args = parser.parse_args()

    # Resolve raw directory
    raw_dir = Path(args.raw_dir)
    if not raw_dir.is_absolute():
        raw_dir = Path(__file__).parent.parent / raw_dir

    # Initialize tracker
    tracker = ProcessingTracker()

    # Determine mode
    if args.file:
        # Process specific file
        file_path = Path(args.file)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            sys.exit(1)

        results = process_files([file_path], tracker, args.asset_type, args.dry_run)

    elif args.watch:
        watch_mode(str(raw_dir), tracker, args.poll_interval, args.asset_type)

    else:
        # Default to oneshot
        results = one_shot_mode(str(raw_dir), tracker, args.asset_type, args.dry_run)

    # Print JSON summary for cron logging
    if not args.watch:
        summary = {
            'mode': 'oneshot' if not args.file else 'file',
            'processed': results['processed'],
            'succeeded': results['succeeded'],
            'failed': results['failed'],
            'total_time': round(results['total_time'], 2),
            'asset_type': args.asset_type,
            'timestamp': datetime.utcnow().isoformat()
        }
        print(json.dumps(summary))


if __name__ == '__main__':
    main()
