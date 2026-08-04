"""
Researcher Agent - Web Research & Synthesis for ALCHEMY Content Pipeline

Researches a user topic via web search and produces an
Archaeologist-compatible data package so the existing Trend-Jacker and
Visionary agents consume it with ZERO changes.

Workflow (5 steps):
1. Generate Queries (1s)
2. Web Search (5-15s)  — Tavily API or offline corpus
3. Synthesize Content (5s)
4. Quality Filter (3s)
5. Package Generation (2s)

Total Time Budget: ~30-60s (dominated by web search latency)

Usage:
    agent = ResearcherAgent()
    result = agent.process_topic("Stoicism for modern entrepreneurs")
"""

import uuid
import time
import logging
from typing import Dict, Any, Optional

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:  # pragma: no cover
    StateGraph = type('StateGraph', (), {})  # type: ignore
    END = 'END'  # type: ignore
    LANGGRAPH_AVAILABLE = False

from src.agents.researcher_state import (
    ResearcherState,
    ResearchStatus,
    create_initial_state,
)
from src.pipeline.web_researcher import (
    research_topic,
    generate_queries,
    synthesize_chunks,
    filter_chunks,
    WebSearchClient,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearcherAgent:
    """
    Researcher Agent - researches web content on a user topic.

    Implements a 5-step LangGraph workflow that outputs an
    Archaeologist-compatible package for the Trend-Jacker agent.
    """

    def __init__(self, force_offline: bool = False):
        """
        Initialize the Researcher agent.

        Args:
            force_offline: Force local corpus backend (tests/demos)
        """
        self.force_offline = force_offline
        self.state: Optional[ResearcherState] = None
        self.memory = None
        self.workflow = None

        if LANGGRAPH_AVAILABLE:
            try:
                self.memory = MemorySaver()
                self.workflow = self._build_workflow()
            except Exception as e:
                logger.warning(f"LangGraph workflow build failed, using fallback: {e}")
                self.workflow = None

    def _build_workflow(self):
        """Build the 5-step LangGraph workflow."""
        workflow = StateGraph(ResearcherState)
        workflow.add_node("generate_queries", self._step_1_generate_queries)
        workflow.add_node("web_search", self._step_2_web_search)
        workflow.add_node("synthesize_content", self._step_3_synthesize_content)
        workflow.add_node("quality_filter", self._step_4_quality_filter)
        workflow.add_node("generate_package", self._step_5_generate_package)
        workflow.add_edge("generate_queries", "web_search")
        workflow.add_edge("web_search", "synthesize_content")
        workflow.add_edge("synthesize_content", "quality_filter")
        workflow.add_edge("quality_filter", "generate_package")
        workflow.add_edge("generate_package", END)
        return workflow.compile()

    def process_topic(
        self,
        topic: str,
        max_queries: int = 5,
        max_results_per_query: int = 3,
    ) -> Dict[str, Any]:
        """
        Research a topic through the complete Researcher workflow.

        Args:
            topic: User topic string
            max_queries: Number of search queries to generate
            max_results_per_query: Results per query

        Returns:
            Dictionary containing:
            - success: Whether research succeeded
            - package: Archaeologist-compatible package (if successful)
            - state: Final ResearcherState
            - processing_time: Total processing time
            - errors: List of errors (if any)

        Raises:
            ValueError: If topic is empty
        """
        if not topic or not topic.strip():
            raise ValueError("Topic cannot be empty")

        # Generate job ID
        job_id = str(uuid.uuid4())

        # Create initial state
        state = create_initial_state(topic, job_id)

        logger.info(f"Starting Researcher workflow for topic: {topic} (job_id: {job_id})")

        start_time = time.time()

        try:
            if LANGGRAPH_AVAILABLE and self.workflow:
                final_state = self._execute_with_langgraph(state, topic, max_queries, max_results_per_query)
            else:
                final_state = self._execute_fallback(state, topic, max_queries, max_results_per_query)

            processing_time = time.time() - start_time
            final_state["processing_time"] = processing_time

            result = {
                'success': final_state.get('status') == ResearchStatus.COMPLETED,
                'package': final_state.get('output_package'),
                'state': final_state,
                'processing_time': processing_time,
                'errors': final_state.get('errors', []),
            }

            if result['success']:
                logger.info(
                    f"Researcher workflow completed successfully in {processing_time:.2f}s: "
                    f"chunks={len(final_state.get('filtered_content', []))}"
                )
            else:
                logger.warning(
                    f"Researcher workflow completed with errors in {processing_time:.2f}s: "
                    f"{final_state.get('errors', [])}"
                )

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Researcher workflow failed after {processing_time:.2f}s: {str(e)}")
            return {
                'success': False,
                'package': None,
                'state': state,
                'processing_time': processing_time,
                'errors': [str(e)],
            }

    def _execute_with_langgraph(self, state, topic, max_queries, max_results_per_query):
        """Execute the workflow through LangGraph."""
        state['status'] = ResearchStatus.GENERATING_QUERIES
        config = {"configurable": {"thread_id": state['job_id']}}
        return self.workflow.invoke(
            state,
            config,
            {"topic": topic, "max_queries": max_queries, "max_results_per_query": max_results_per_query},
        )

    def _execute_fallback(self, state, topic, max_queries, max_results_per_query):
        """Execute the workflow steps sequentially (no LangGraph)."""
        state = self._step_1_generate_queries(state)
        state = self._step_2_web_search(state)
        state = self._step_3_synthesize_content(state)
        state = self._step_4_quality_filter(state)
        state = self._step_5_generate_package(state)
        return state

    # ------------------------------------------------------------------
    # LangGraph Step Implementations
    # ------------------------------------------------------------------

    def _step_1_generate_queries(self, state: ResearcherState) -> ResearcherState:
        """Step 1: Generate search queries from topic (1s)."""
        step_start = time.time()
        logger.info("Step 1: Generating search queries")

        try:
            topic = state.get('topic', '')
            queries = generate_queries(topic, 5)
            state['search_queries'] = queries
            state['current_step'] = "generate_queries"
            state['step_times']['generate_queries'] = time.time() - step_start
            state['status'] = ResearchStatus.GENERATING_QUERIES
            logger.info(f"Step 1 completed: {len(queries)} queries generated")
            return state
        except Exception as e:
            step_time = time.time() - step_start
            state['step_times']['generate_queries'] = step_time
            state['errors'].append(f"Query generation failed: {str(e)}")
            state['error_message'] = str(e)
            state['status'] = ResearchStatus.FAILED
            raise

    def _step_2_web_search(self, state: ResearcherState) -> ResearcherState:
        """Step 2: Run web searches (5-15s)."""
        step_start = time.time()
        logger.info("Step 2: Running web searches")

        try:
            client = WebSearchClient(force_offline=self.force_offline)
            state['search_backend'] = client.backend_used

            all_results = []
            for query in state.get('search_queries', []):
                try:
                    results = client.search(query, 3)
                    all_results.extend(results)
                except Exception as e:
                    state['errors'].append(f"Search '{query}' failed: {str(e)}")

            state['search_results'] = all_results
            state['current_step'] = "web_search"
            state['step_times']['web_search'] = time.time() - step_start
            state['status'] = ResearchStatus.SEARCHING
            logger.info(
                f"Step 2 completed: {len(all_results)} results via {state['search_backend']}"
            )
            return state
        except Exception as e:
            step_time = time.time() - step_start
            state['step_times']['web_search'] = step_time
            state['errors'].append(f"Web search failed: {str(e)}")
            state['error_message'] = str(e)
            state['status'] = ResearchStatus.FAILED
            raise

    def _step_3_synthesize_content(self, state: ResearcherState) -> ResearcherState:
        """Step 3: Synthesize search results into content chunks (5s)."""
        step_start = time.time()
        logger.info("Step 3: Synthesizing content")

        try:
            topic = state.get('topic', '')
            chunks = synthesize_chunks(topic, state.get('search_results', []))
            state['content_chunks'] = chunks
            state['current_step'] = "synthesize_content"
            state['step_times']['synthesize_content'] = time.time() - step_start
            state['status'] = ResearchStatus.SYNTHESIZING
            logger.info(f"Step 3 completed: {len(chunks)} chunks synthesized")
            return state
        except Exception as e:
            step_time = time.time() - step_start
            state['step_times']['synthesize_content'] = step_time
            state['errors'].append(f"Content synthesis failed: {str(e)}")
            state['error_message'] = str(e)
            state['status'] = ResearchStatus.FAILED
            raise

    def _step_4_quality_filter(self, state: ResearcherState) -> ResearcherState:
        """Step 4: Filter low-quality chunks (3s)."""
        step_start = time.time()
        logger.info("Step 4: Filtering quality")

        try:
            filtered = filter_chunks(state.get('content_chunks', []))
            state['filtered_content'] = filtered
            state['current_step'] = "quality_filter"
            state['step_times']['quality_filter'] = time.time() - step_start
            state['status'] = ResearchStatus.FILTERING
            logger.info(
                f"Step 4 completed: kept {len(filtered)}/{len(state.get('content_chunks', []))} chunks"
            )
            return state
        except Exception as e:
            step_time = time.time() - step_start
            state['step_times']['quality_filter'] = step_time
            state['errors'].append(f"Quality filter failed: {str(e)}")
            state['error_message'] = str(e)
            state['status'] = ResearchStatus.FAILED
            raise

    def _step_5_generate_package(self, state: ResearcherState) -> ResearcherState:
        """Step 5: Generate Archaeologist-compatible package (2s)."""
        step_start = time.time()
        logger.info("Step 5: Generating package")

        try:
            from src.pipeline.web_researcher import build_package

            topic = state.get('topic', '')
            chunks = state.get('filtered_content', [])
            package = build_package(
                topic,
                chunks,
                state.get('search_queries', []),
                state.get('step_times', {}).get('web_search', 0.0),
                state.get('job_id', 'unknown'),
            )
            state['output_package'] = package
            state['current_step'] = "generate_package"
            state['step_times']['generate_package'] = time.time() - step_start
            state['status'] = ResearchStatus.COMPLETED
            logger.info(
                f"Step 5 completed: package={package.get('package_id', 'N/A')}, "
                f"chunks={len(chunks)}"
            )
            return state
        except Exception as e:
            step_time = time.time() - step_start
            state['step_times']['generate_package'] = step_time
            state['errors'].append(f"Package generation failed: {str(e)}")
            state['error_message'] = str(e)
            state['status'] = ResearchStatus.FAILED
            raise


def main():
    """CLI entry point for standalone research runs."""
    import argparse

    parser = argparse.ArgumentParser(description="ALCHEMY Researcher Agent")
    parser.add_argument('topic', help='Topic to research')
    parser.add_argument('--offline', action='store_true', help='Force offline corpus backend')
    args = parser.parse_args()

    agent = ResearcherAgent(force_offline=args.offline)
    result = agent.process_topic(args.topic)

    print(f"Success: {result['success']}")
    print(f"Backend: {result.get('state', {}).get('search_backend', 'unknown')}")
    print(f"Time: {result['processing_time']:.2f}s")
    if result['success']:
        pkg = result['package']
        print(f"Package: {pkg.get('package_id')}")
        print(f"Chunks: {len(pkg.get('content', []))}")
        for i, chunk in enumerate(pkg.get('content', []), 1):
            print(f"  [{i}] ({chunk.get('quality_level')}) {chunk.get('text', '')[:100]}...")
    else:
        print(f"Errors: {result['errors']}")


if __name__ == "__main__":
    main()
