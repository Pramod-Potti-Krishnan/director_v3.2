# -*- coding: utf-8 -*-
"""
Real Diagram Generator Service Client - v2.0
=============================================

Integration with Diagram Generator v3.0 Railway service.

Service Details:
- Production URL: https://web-production-e0ad0.up.railway.app
- Async job-based API with polling
- 21 SVG templates, 7 Mermaid types, 6 Python charts
- Response time: <2s for SVG, <500ms for Mermaid
"""

import os
import asyncio
import logging
from typing import Dict, Any
import requests
from dotenv import load_dotenv

from orchestration.models.director_models import GeneratedDiagram

load_dotenv()
logger = logging.getLogger(__name__)


class RealDiagramClient:
    """
    Real Diagram Generator service client.

    Integrates with production Railway deployment using async job polling pattern.
    """

    def __init__(self, base_url: str = None):
        """
        Initialize diagram service client.

        Args:
            base_url: Override URL (default: from DIAGRAM_SERVICE_URL env var)
        """
        self.base_url = base_url or os.getenv(
            "DIAGRAM_SERVICE_URL",
            "https://web-production-e0ad0.up.railway.app"
        )
        self.timeout = int(os.getenv("DIAGRAM_SERVICE_TIMEOUT", "60"))
        self.poll_interval = int(os.getenv("DIAGRAM_POLL_INTERVAL", "2"))

        logger.info(f"RealDiagramClient initialized (url: {self.base_url}, timeout: {self.timeout}s, poll: {self.poll_interval}s)")

    async def generate(self, request: Dict[str, Any]) -> GeneratedDiagram:
        """
        Generate diagram from production service using job polling.

        Args:
            request: Orchestrator request with content, type, theme
                Expected keys:
                - content: str - Diagram content/data
                - diagram_type: str - Type of diagram
                - theme: Dict - Primary color, style
                - slide_number: int - For reference

        Returns:
            GeneratedDiagram with URL and metadata
        """
        # Transform request to service format
        service_request = self._transform_request(request)

        # Submit job (non-blocking)
        loop = asyncio.get_event_loop()
        job_response = await loop.run_in_executor(
            None,
            self._sync_submit_job,
            service_request
        )

        job_id = job_response.get("job_id")
        if not job_id:
            raise RuntimeError(f"Diagram service did not return job_id: {job_response}")

        logger.info(f"Diagram job submitted: {job_id}")

        # Poll for completion (non-blocking)
        result = await self._poll_job(job_id)

        # Transform response to orchestrator format
        return self._transform_response(result, request)

    def _sync_submit_job(self, request: Dict) -> Dict:
        """
        Submit diagram generation job (synchronous).

        Args:
            request: Service-formatted request

        Returns:
            Job submission response with job_id

        Raises:
            requests.HTTPError: On API errors
            requests.Timeout: On timeout
        """
        endpoint = f"{self.base_url}/generate"

        try:
            response = requests.post(
                endpoint,
                json=request,
                timeout=10  # Short timeout for job submission
            )
            response.raise_for_status()
            return response.json()

        except requests.Timeout as e:
            logger.error(f"Diagram service job submission timeout")
            raise
        except requests.HTTPError as e:
            logger.error(f"Diagram service HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Diagram service job submission failed: {str(e)}")
            raise

    async def _poll_job(self, job_id: str) -> Dict:
        """
        Poll job status until completion (async, non-blocking).

        Args:
            job_id: Job identifier from submission

        Returns:
            Completed job result

        Raises:
            RuntimeError: If job fails
            TimeoutError: If polling times out
        """
        max_attempts = int(self.timeout / self.poll_interval)
        loop = asyncio.get_event_loop()

        for attempt in range(max_attempts):
            # Non-blocking sleep
            await asyncio.sleep(self.poll_interval)

            # Check status (run in executor to avoid blocking)
            status = await loop.run_in_executor(
                None,
                lambda: requests.get(
                    f"{self.base_url}/status/{job_id}",
                    timeout=10
                ).json()
            )

            job_status = status.get("status")

            if job_status == "completed":
                logger.info(f"Diagram job {job_id} completed")
                return status
            elif job_status == "failed":
                error = status.get("error", "Unknown error")
                logger.error(f"Diagram job {job_id} failed: {error}")
                raise RuntimeError(f"Diagram generation failed: {error}")
            elif job_status in ["pending", "processing"]:
                logger.debug(f"Diagram job {job_id} still {job_status} (attempt {attempt + 1}/{max_attempts})")
                continue
            else:
                logger.warning(f"Diagram job {job_id} unknown status: {job_status}")

        raise TimeoutError(f"Diagram generation timed out after {self.timeout}s (job_id: {job_id})")

    def _transform_request(self, orchestrator_request: Dict) -> Dict:
        """
        Transform orchestrator request to Diagram service format.

        Diagram Service API expects:
        {
            "content": str,
            "diagram_type": str,
            "theme": {
                "primaryColor": str,
                "style": str
            }
        }
        """
        # Extract theme colors
        theme = orchestrator_request.get("theme", {})
        primary_color = theme.get("primary_color", "#3B82F6")
        style = theme.get("style", "modern")

        return {
            "content": orchestrator_request.get("content", ""),
            "diagram_type": orchestrator_request.get("diagram_type", "flowchart"),
            "theme": {
                "primaryColor": primary_color,
                "style": style
            }
        }

    def _transform_response(self, service_response: Dict, original_request: Dict) -> GeneratedDiagram:
        """
        Transform Diagram service response to orchestrator format.

        Service response format (fields at top level):
        {
            "status": "completed",
            "diagram_url": str,
            "diagram_type": str,
            "generation_method": str,
            "metadata": {
                "generation_time_ms": int,
                "dimensions": dict,
                ...
            }
        }

        Returns:
            GeneratedDiagram model
        """
        return GeneratedDiagram(
            type=service_response.get("diagram_type", original_request.get("diagram_type", "unknown")),
            url=service_response.get("diagram_url", ""),
            data=None,  # Optional structured data
            metadata={
                "generation_method": service_response.get("generation_method"),
                "generation_time_ms": service_response.get("metadata", {}).get("generation_time_ms"),
                "dimensions": service_response.get("metadata", {}).get("dimensions"),
                "source": "diagram_service_v3.0"
            }
        )

    async def generate_batch(
        self,
        requests: list[Dict[str, Any]]
    ) -> list[GeneratedDiagram]:
        """
        Generate batch of diagrams.

        Args:
            requests: List of request dicts

        Returns:
            List of GeneratedDiagram
        """
        tasks = [self.generate(req) for req in requests]
        results = await asyncio.gather(*tasks)
        return results
