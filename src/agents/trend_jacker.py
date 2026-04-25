"""
Trend-Jacker Agent - Main Orchestration

Orchestrates the 7-step Trend-Jacker workflow for contextualizing
evergreen content into modern hook frameworks.

Workflow Steps:
1. Receive Data Pack (5s)
2. Analyze Trends (15s)
3. Generate Hooks (20s)
4. Structure Narrative (25s)
5. Optimize Attention (10s)
6. Enhance Content (5s)
7. Package for Visionary (5s)

Total Time Budget: 90 seconds
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Try to import LangGraph, use fallback if not available
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available, using fallback mode")

# Import Trend-Jacker state and pipeline modules
from src.agents.trend_jacker_state import (
    TrendJackerState,
    ProcessingStatus,
    create_initial_state
)
from src.pipeline.trend_mapper import TrendMapper, map_trends
from src.pipeline.hook_generator import HookGenerator, generate_hooks
from src.pipeline.narrative_structurer import NarrativeStructurer, structure_narrative
from src.pipeline.attention_optimizer import AttentionOptimizer, optimize_attention
from src.pipeline.content_enhancer import ContentEnhancer, enhance_content
from src.pipeline.content_packager import ContentPackager, package_content

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrendJackerAgent:
    """
    Trend-Jacker Agent - Contextualizes evergreen content into modern frameworks.

    Takes data packs from Archaeologist and transforms them into engaging,
    modern content optimized for current trends and attention patterns.
    """

    def __init__(self):
        """Initialize TrendJackerAgent with pipeline components."""
        self.state = None  # Will be initialized in process()
        self.total_timeout = 90.0  # 90 second total timeout

        # Initialize pipeline components
        self.trend_mapper = TrendMapper()
        self.hook_generator = HookGenerator()
        self.narrative_structurer = NarrativeStructurer()
        self.attention_optimizer = AttentionOptimizer()
        self.content_enhancer = ContentEnhancer()
        self.content_packager = ContentPackager()

        logger.info("TrendJackerAgent initialized")

    def process(self, data_pack: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data pack through complete Trend-Jacker workflow.

        Args:
            data_pack: Data pack from Archaeologist agent

        Returns:
            Dictionary containing:
            - package: Complete package for Visionary agent
            - package_id: Unique package identifier
            - total_time: Total processing time
            - status: Processing status

        Raises:
            TrendJackerError: If processing fails
        """
        start_time = time.time()

        logger.info("Starting Trend-Jacker workflow")

        try:
            # Initialize state
            self.state = create_initial_state(data_pack, f"tj_{int(time.time())}")
            self.state['status'] = ProcessingStatus.ANALYZING

            # Execute workflow
            if LANGGRAPH_AVAILABLE:
                result = self._execute_with_langgraph()
            else:
                result = self._execute_fallback()

            total_time = time.time() - start_time

            # Check timeout
            if total_time > self.total_timeout:
                logger.warning(
                    f"Trend-Jacker workflow exceeded time budget: {total_time:.2f}s > {self.total_timeout}s"
                )
                self.state['status'] = ProcessingStatus.FAILED
                self.state['error_message'] = f"Timeout: {total_time:.2f}s > {self.total_timeout}s"
            else:
                self.state['status'] = ProcessingStatus.COMPLETED

            self.state['processing_time'] = total_time

            result['total_time'] = total_time
            result['status'] = self.state['status'].value

            logger.info(
                f"Trend-Jacker workflow completed in {total_time:.2f}s: "
                f"status={self.state['status'].value}, package_id={result.get('package_id', 'N/A')}"
            )

            return result

        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Trend-Jacker workflow failed after {total_time:.2f}s: {str(e)}")

            if self.state:
                self.state['status'] = ProcessingStatus.FAILED
                self.state['error_message'] = str(e)

            raise Exception(f"Trend-Jacker processing failed: {str(e)}")

    def _execute_with_langgraph(self) -> Dict[str, Any]:
        """
        Execute workflow using LangGraph orchestration.

        Returns:
            Dictionary with processing results
        """
        # Create LangGraph workflow
        workflow = StateGraph(TrendJackerState)

        # Add nodes for each step
        workflow.add_node("receive_data_pack", self._step_1_receive_data_pack)
        workflow.add_node("analyze_trends", self._step_2_analyze_trends)
        workflow.add_node("generate_hooks", self._step_3_generate_hooks)
        workflow.add_node("structure_narrative", self._step_4_structure_narrative)
        workflow.add_node("optimize_attention", self._step_5_optimize_attention)
        workflow.add_node("enhance_content", self._step_6_enhance_content)
        workflow.add_node("package_for_visionary", self._step_7_package_for_visionary)

        # Define workflow edges
        workflow.set_entry_point("receive_data_pack")
        workflow.add_edge("receive_data_pack", "analyze_trends")
        workflow.add_edge("analyze_trends", "generate_hooks")
        workflow.add_edge("generate_hooks", "structure_narrative")
        workflow.add_edge("structure_narrative", "optimize_attention")
        workflow.add_edge("optimize_attention", "enhance_content")
        workflow.add_edge("enhance_content", "package_for_visionary")
        workflow.add_edge("package_for_visionary", END)

        # Compile workflow
        app = workflow.compile()

        # Execute workflow
        result = app.invoke(self.state)

        return {
            'package': result['output_package'],
            'package_id': result['package_id'],
            'workflow_mode': 'langgraph'
        }

    def _execute_fallback(self) -> Dict[str, Any]:
        """
        Execute workflow in fallback mode without LangGraph.

        Returns:
            Dictionary with processing results
        """
        # Step 1: Receive Data Pack
        self._step_1_receive_data_pack(self.state)

        # Step 2: Analyze Trends
        self._step_2_analyze_trends(self.state)

        # Step 3: Generate Hooks
        self._step_3_generate_hooks(self.state)

        # Step 4: Structure Narrative
        self._step_4_structure_narrative(self.state)

        # Step 5: Optimize Attention
        self._step_5_optimize_attention(self.state)

        # Step 6: Enhance Content
        self._step_6_enhance_content(self.state)

        # Step 7: Package for Visionary
        self._step_7_package_for_visionary(self.state)

        return {
            'package': self.state['output_package'],
            'package_id': self.state['package_id'],
            'workflow_mode': 'fallback'
        }

    def _step_1_receive_data_pack(self, state: TrendJackerState) -> TrendJackerState:
        """
        Step 1: Receive Data Pack from Archaeologist (5s).

        Args:
            state: Current state

        Returns:
            Updated state
        """
        step_start = time.time()
        logger.info("Step 1: Receiving data pack")

        try:
            # Validate data pack
            if not state.get('data_pack'):
                raise ValueError("No data pack received")

            # Extract content chunks
            state['content_chunks'] = state.get('data_pack', {}).get('content_chunks', [])

            # Extract source file
            state['source_file'] = state.get('data_pack', {}).get('metadata', {}).get('source_file', 'unknown')

            # Update state
            state['current_step'] = "receive_data_pack"
            state['step_times']['receive_data_pack'] = time.time() - step_start

            logger.info(
                f"Step 1 completed in {state['step_times']['receive_data_pack']:.2f}s: "
                f"received {len(state['content_chunks'])} chunks from {state['source_file']}"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 1 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'data_pack_error', 'message': str(e), 'step': 'receive_data_pack'}
            raise

    def _step_2_analyze_trends(self, state: TrendJackerState) -> TrendJackerState:
        """
        Step 2: Analyze Trends (15s).

        Args:
            state: Current state

        Returns:
            Updated state
        """
        step_start = time.time()
        logger.info("Step 2: Analyzing trends")

        try:
            # Analyze trends
            trend_result = self.trend_mapper.map(state['content_chunks'], ['productivity', 'efficiency'])

            # Update state
            state['trend_analysis'] = trend_result
            state['trend_mappings'] = trend_result.get('mapped_trends', [])
            state['mapped_trends'] = trend_result.get('mapped_trends', [])  # Alias
            state['current_step'] = "analyze_trends"
            state['step_times']['analyze_trends'] = time.time() - step_start

            logger.info(
                f"Step 2 completed in {state['step_times']['analyze_trends']:.2f}s: "
                f"identified {len(state['trend_mappings'])} trend mappings"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 2 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'trend_analysis_error', 'message': str(e), 'step': 'analyze_trends'}
            raise

    def _step_3_generate_hooks(self, state: TrendJackerState) -> TrendJackerState:
        """
        Step 3: Generate Hooks (20s).

        Args:
            state: Current state

        Returns:
            Updated state
        """
        step_start = time.time()
        logger.info("Step 3: Generating hooks")

        try:
            # Generate hooks
            hook_result = self.hook_generator.generate(
                state['content_chunks'],
                ['productivity', 'efficiency']
            )

            # Update state
            state['hooks'] = hook_result.get('hooks', [])
            state['generated_hooks'] = hook_result.get('hooks', [])  # Alias
            state['current_step'] = "generate_hooks"
            state['step_times']['generate_hooks'] = time.time() - step_start

            logger.info(
                f"Step 3 completed in {state['step_times']['generate_hooks']:.2f}s: "
                f"generated {len(state['hooks'])} hooks"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 3 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'hook_generation_error', 'message': str(e), 'step': 'generate_hooks'}
            raise

    def _step_4_structure_narrative(self, state: TrendJackerState) -> TrendJackerState:
        """
        Step 4: Structure Narrative (25s).

        Args:
            state: Current state

        Returns:
            Updated state
        """
        step_start = time.time()
        logger.info("Step 4: Structuring narrative")

        try:
            # Structure narrative
            narrative_result = self.narrative_structurer.structure(
                state['content_chunks'],
                state['trend_mappings'],
                state['hooks']
            )

            # Update state
            state['narrative_structure'] = narrative_result['narrative_structure']
            state['current_step'] = "structure_narrative"
            state['step_times']['structure_narrative'] = time.time() - step_start

            logger.info(
                f"Step 4 completed in {state['step_times']['structure_narrative']:.2f}s: "
                f"coherence_score={state['narrative_structure'].get('coherence_score', 0):.2f}"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 4 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'narrative_structuring_error', 'message': str(e), 'step': 'structure_narrative'}
            raise

    def _step_5_optimize_attention(self, state: TrendJackerState) -> TrendJackerState:
        """
        Step 5: Optimize Attention (10s).

        Args:
            state: Current state

        Returns:
            Updated state
        """
        step_start = time.time()
        logger.info("Step 5: Optimizing attention")

        try:
            # Optimize attention
            attention_result = self.attention_optimizer.optimize(
                state['content_chunks'],
                state['narrative_structure'],
                state['hooks']
            )

            # Update state
            state['optimized_content'] = attention_result['optimized_content']
            state['attention_metrics'] = attention_result['attention_metrics']
            state['retention_score'] = attention_result['retention_score']
            state['current_step'] = "optimize_attention"
            state['step_times']['optimize_attention'] = time.time() - step_start

            logger.info(
                f"Step 5 completed in {state['step_times']['optimize_attention']:.2f}s: "
                f"retention_score={state['retention_score']:.2f}"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 5 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'attention_optimization_error', 'message': str(e), 'step': 'optimize_attention'}
            raise

    def _step_6_enhance_content(self, state: TrendJackerState) -> TrendJackerState:
        """
        Step 6: Enhance Content (5s).

        Args:
            state: Current state

        Returns:
            Updated state
        """
        step_start = time.time()
        logger.info("Step 6: Enhancing content")

        try:
            # Enhance content
            enhancement_result = self.content_enhancer.enhance(
                state['optimized_content'],
                state['narrative_structure'],
                state['hooks']
            )

            # Update state
            state['enhanced_content'] = enhancement_result['enhanced_content']
            state['enhancement_metrics'] = enhancement_result['enhancement_metrics']
            state['engagement_score'] = enhancement_result['engagement_score']
            state['current_step'] = "enhance_content"
            state['step_times']['enhance_content'] = time.time() - step_start

            logger.info(
                f"Step 6 completed in {state['step_times']['enhance_content']:.2f}s: "
                f"engagement_score={state['engagement_score']:.2f}"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 6 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'content_enhancement_error', 'message': str(e), 'step': 'enhance_content'}
            raise

    def _step_7_package_for_visionary(self, state: TrendJackerState) -> TrendJackerState:
        """
        Step 7: Package for Visionary (5s).

        Args:
            state: Current state

        Returns:
            Updated state
        """
        step_start = time.time()
        logger.info("Step 7: Packaging for Visionary")

        try:
            # Package content
            packaging_result = self.content_packager.package(
                state['enhanced_content'],
                state['narrative_structure'],
                state['hooks'],
                state['enhancement_metrics'],
                state['engagement_score'],
                state['retention_score'],
                state['source_file']
            )

            # Update state
            state['package'] = packaging_result['package']
            state['output_package'] = packaging_result['package']  # Alias
            state['package_id'] = packaging_result['package_id']
            state['current_step'] = "package_for_visionary"
            state['step_times']['package_for_visionary'] = time.time() - step_start

            logger.info(
                f"Step 7 completed in {state['step_times']['package_for_visionary']:.2f}s: "
                f"package_id={state['package_id']}"
            )

            return state

        except Exception as e:
            step_time = time.time() - step_start
            logger.error(f"Step 7 failed after {step_time:.2f}s: {str(e)}")
            state['error_message'] = str(e)
            state['error'] = {'error_type': 'packaging_error', 'message': str(e), 'step': 'package_for_visionary'}
            raise

    def get_status(self) -> Dict[str, Any]:
        """
        Get current processing status.

        Returns:
            Dictionary with status information
        """
        if not self.state:
            return {
                'status': 'idle',
                'current_step': '',
                'package_id': None,
                'step_times': {},
                'error': None
            }

        return {
            'status': self.state['status'].value,
            'current_step': self.state['current_step'],
            'package_id': self.state['package_id'],
            'step_times': self.state['step_times'],
            'error': self.state['error']
        }


# Convenience function for quick Trend-Jacker processing
def process_trend_jacker(data_pack: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to process data pack through Trend-Jacker workflow.

    Args:
        data_pack: Data pack from Archaeologist agent

    Returns:
        Dictionary with processing results
    """
    agent = TrendJackerAgent()
    return agent.process(data_pack)


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python trend_jacker.py <data_pack_path>")
        sys.exit(1)

    data_pack_path = sys.argv[1]

    # Load data pack
    with open(data_pack_path, 'r') as f:
        data_pack = json.load(f)

    # Process through Trend-Jacker
    result = process_trend_jacker(data_pack)

    # Print results
    print(f"Package ID: {result['package_id']}")
    print(f"Total Time: {result['total_time']:.2f}s")
    print(f"Status: {result['status']}")
    print(f"Workflow Mode: {result['workflow_mode']}")
