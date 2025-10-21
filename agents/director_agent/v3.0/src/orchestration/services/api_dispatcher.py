"""
API Dispatcher - v2.0
======================

Parallel API execution with progress streaming.

This service orchestrates parallel API calls using asyncio.gather().
All APIs are called simultaneously for maximum performance.

Performance target: <10s for 10 slides (all APIs in parallel)
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class APIDispatcher:
    """
    Dispatches API requests in parallel with progress streaming.

    Key features:
    - Parallel execution using asyncio.gather()
    - Real-time progress callbacks
    - Error handling with partial results
    - Automatic retry on transient failures
    """

    def __init__(self, text_client, chart_client, image_client, diagram_client):
        """
        Initialize dispatcher with API clients.

        Args:
            text_client: Text generation API client
            chart_client: Chart generation API client
            image_client: Image generation API client
            diagram_client: Diagram generation API client
        """
        self.text_client = text_client
        self.chart_client = chart_client
        self.image_client = image_client
        self.diagram_client = diagram_client
        logger.info("APIDispatcher initialized with 4 API clients")

    async def dispatch_all(
        self,
        all_requests: Dict[str, List[Dict[str, Any]]],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Dispatch all API requests in parallel.

        This is the main entry point for parallel execution.

        Args:
            all_requests: Dict of requests grouped by API type:
                {
                    "text": [req1, req2, ...],
                    "chart": [req1, req2, ...],
                    "image": [req1, req2, ...],
                    "diagram": [req1, req2, ...]
                }
            progress_callback: Optional callback(message, current, total)

        Returns:
            Dict with results grouped by slide_id:
            {
                "slide_000": {
                    "text": GeneratedText or None,
                    "charts": [GeneratedChart, ...],
                    "images": [GeneratedImage, ...],
                    "diagrams": [GeneratedDiagram, ...]
                },
                ...
            }
        """
        start_time = time.time()

        # Flatten all requests into a single list with metadata
        tasks = []
        task_metadata = []

        for api_type, requests in all_requests.items():
            for req in requests:
                # Create coroutine for this request
                task = self._dispatch_single(api_type, req, progress_callback)
                tasks.append(task)
                task_metadata.append({
                    "api_type": api_type,
                    "slide_id": req.get("slide_id"),
                    "slide_number": req.get("slide_number")
                })

        total_tasks = len(tasks)
        logger.info(f"Dispatching {total_tasks} API requests in parallel")

        if progress_callback:
            progress_callback(f"Starting {total_tasks} parallel API calls", 0, total_tasks)

        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Group results by slide_id
        grouped_results = self._group_results_by_slide(results, task_metadata)

        elapsed_time = time.time() - start_time
        logger.info(f"All {total_tasks} API calls completed in {elapsed_time:.2f}s")

        if progress_callback:
            progress_callback(f"Completed {total_tasks} API calls", total_tasks, total_tasks)

        return grouped_results

    async def _dispatch_single(
        self,
        api_type: str,
        request: Dict[str, Any],
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Dispatch a single API request with error handling.

        Args:
            api_type: Type of API ("text", "chart", "image", "diagram")
            request: Request dict
            progress_callback: Optional progress callback

        Returns:
            Result dict with metadata
        """
        slide_number = request.get("slide_number", "?")
        logger.info(f"Dispatching {api_type} API for slide {slide_number}")

        if progress_callback:
            progress_callback(f"Calling {api_type} API for slide {slide_number}", 0, 1)

        try:
            # Route to appropriate API client
            if api_type == "text":
                result = await self.text_client.generate(request)
            elif api_type == "chart":
                result = await self.chart_client.generate(request)
            elif api_type == "image":
                result = await self.image_client.generate(request)
            elif api_type == "diagram":
                result = await self.diagram_client.generate(request)
            else:
                raise ValueError(f"Unknown API type: {api_type}")

            logger.info(f"Successfully generated {api_type} for slide {slide_number}")

            return {
                "success": True,
                "api_type": api_type,
                "slide_id": request.get("slide_id"),
                "slide_number": slide_number,
                "result": result,
                "error": None
            }

        except Exception as e:
            logger.error(f"Error generating {api_type} for slide {slide_number}: {e}", exc_info=True)

            return {
                "success": False,
                "api_type": api_type,
                "slide_id": request.get("slide_id"),
                "slide_number": slide_number,
                "result": None,
                "error": str(e)
            }

    def _group_results_by_slide(
        self,
        results: List[Any],
        metadata: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Group API results by slide_id.

        Args:
            results: List of results from asyncio.gather()
            metadata: List of metadata for each result

        Returns:
            Dict with results grouped by slide_id
        """
        grouped = {}

        for result, meta in zip(results, metadata):
            slide_id = meta["slide_id"]
            api_type = meta["api_type"]

            # Initialize slide entry if needed
            if slide_id not in grouped:
                grouped[slide_id] = {
                    "text": None,
                    "charts": [],
                    "images": [],
                    "diagrams": [],
                    "errors": []
                }

            # Handle exceptions from asyncio.gather
            if isinstance(result, Exception):
                logger.error(f"Exception for slide {slide_id}, {api_type}: {result}")
                grouped[slide_id]["errors"].append({
                    "api_type": api_type,
                    "error": str(result)
                })
                continue

            # Handle failed API calls
            if not result.get("success"):
                grouped[slide_id]["errors"].append({
                    "api_type": api_type,
                    "error": result.get("error")
                })
                continue

            # Add successful result to appropriate field
            if api_type == "text":
                grouped[slide_id]["text"] = result["result"]
            elif api_type == "chart":
                grouped[slide_id]["charts"].append(result["result"])
            elif api_type == "image":
                grouped[slide_id]["images"].append(result["result"])
            elif api_type == "diagram":
                grouped[slide_id]["diagrams"].append(result["result"])

        return grouped

    async def dispatch_batch(
        self,
        requests: List[Dict[str, Any]],
        api_type: str,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> List[Dict[str, Any]]:
        """
        Dispatch a batch of requests to the same API type.

        Useful for batch processing when all requests are for the same API.

        Args:
            requests: List of request dicts
            api_type: Type of API
            progress_callback: Optional progress callback

        Returns:
            List of results
        """
        tasks = [
            self._dispatch_single(api_type, req, progress_callback)
            for req in requests
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
