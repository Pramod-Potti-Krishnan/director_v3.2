# -*- coding: utf-8 -*-
"""
Real Analytics Microservice Client - v2.0
==========================================

Integration with Analytics Microservice v3 Railway service.

Service Details:
- Production URL: https://analytics-v30-production.up.railway.app
- Async job-based API with polling
- 20+ chart types (bar, line, pie, scatter, heatmap, etc.)
- LLM-enhanced data synthesis with OpenAI GPT-4o-mini
"""

import os
import asyncio
import logging
from typing import Dict, Any
import requests
from dotenv import load_dotenv

from orchestration.models.director_models import GeneratedChart

load_dotenv()
logger = logging.getLogger(__name__)


class RealChartClient:
    """
    Real Analytics Microservice client.

    Integrates with production Railway deployment using async job polling pattern.
    """

    def __init__(self, base_url: str = None):
        """
        Initialize chart/analytics service client.

        Args:
            base_url: Override URL (default: from CHART_SERVICE_URL env var)
        """
        self.base_url = base_url or os.getenv(
            "CHART_SERVICE_URL",
            "https://analytics-v30-production.up.railway.app"
        )
        self.timeout = int(os.getenv("CHART_SERVICE_TIMEOUT", "60"))
        self.poll_interval = int(os.getenv("CHART_POLL_INTERVAL", "2"))

        logger.info(f"RealChartClient initialized (url: {self.base_url}, timeout: {self.timeout}s, poll: {self.poll_interval}s)")

    async def generate(self, request: Dict[str, Any]) -> GeneratedChart:
        """
        Generate chart from production service using job polling.

        Args:
            request: Orchestrator request with content, chart_type, data, theme
                Expected keys:
                - content: str - Chart content/description
                - chart_type: str - Type of chart (bar, line, pie, etc.)
                - data: Dict - Chart data
                - theme: Dict - Primary color, background color
                - slide_number: int - For reference

        Returns:
            GeneratedChart with URL, data, and metadata
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
            raise RuntimeError(f"Chart service did not return job_id: {job_response}")

        logger.info(f"Chart job submitted: {job_id}")

        # Poll for completion (non-blocking)
        result = await self._poll_job(job_id)

        # Transform response to orchestrator format
        return self._transform_response(result, request)

    def _sync_submit_job(self, request: Dict) -> Dict:
        """
        Submit chart generation job (synchronous).

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
            logger.error(f"Chart service job submission timeout")
            raise
        except requests.HTTPError as e:
            logger.error(f"Chart service HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Chart service job submission failed: {str(e)}")
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
                logger.info(f"Chart job {job_id} completed")
                return status
            elif job_status == "failed":
                error = status.get("error", "Unknown error")
                logger.error(f"Chart job {job_id} failed: {error}")
                raise RuntimeError(f"Chart generation failed: {error}")
            elif job_status in ["pending", "processing"]:
                logger.debug(f"Chart job {job_id} still {job_status} (attempt {attempt + 1}/{max_attempts})")
                continue
            else:
                logger.warning(f"Chart job {job_id} unknown status: {job_status}")

        raise TimeoutError(f"Chart generation timed out after {self.timeout}s (job_id: {job_id})")

    def _transform_request(self, orchestrator_request: Dict) -> Dict:
        """
        Transform orchestrator request to Analytics service format.

        Analytics Service API expects:
        {
            "content": str,
            "title": str,
            "data": list (optional),
            "chart_type": str,
            "theme": str  // Theme name: default, dark, professional, colorful, minimal
        }
        """
        # Get data - ensure it's a list or omit it
        data = orchestrator_request.get("data")
        if data is not None and not isinstance(data, list):
            data = None  # Service expects list or nothing

        # Get theme - if dict provided, convert to theme name
        theme = orchestrator_request.get("theme", {})
        if isinstance(theme, dict):
            # Use professional as default theme name
            theme_name = "professional"
        else:
            theme_name = theme or "professional"

        request = {
            "content": orchestrator_request.get("content", ""),
            "title": orchestrator_request.get("title", "Chart"),
            "chart_type": orchestrator_request.get("chart_type", "bar")
        }

        # Only add data if it's a valid list
        if data is not None:
            request["data"] = data

        # Add theme
        request["theme"] = theme_name

        return request

    def _transform_response(self, service_response: Dict, original_request: Dict) -> GeneratedChart:
        """
        Transform Analytics service response to orchestrator format.

        Service response format (fields at top level):
        {
            "status": "completed",
            "chart_url": str,
            "chart_data": dict,
            "chart_type": str,
            "theme": str,
            "metadata": {
                "generated_at": str,
                "data_points": int
            }
        }

        Returns:
            GeneratedChart model
        """
        return GeneratedChart(
            type=service_response.get("chart_type", original_request.get("chart_type", "bar")),
            data=service_response.get("chart_data", {}),
            url=service_response.get("chart_url"),
            metadata={
                "theme": service_response.get("theme"),
                "generated_at": service_response.get("metadata", {}).get("generated_at"),
                "data_points": service_response.get("metadata", {}).get("data_points"),
                "source": "analytics_service_v3"
            }
        )

    async def generate_batch(
        self,
        requests: list[Dict[str, Any]]
    ) -> list[GeneratedChart]:
        """
        Generate batch of charts.

        Args:
            requests: List of request dicts

        Returns:
            List of GeneratedChart
        """
        tasks = [self.generate(req) for req in requests]
        results = await asyncio.gather(*tasks)
        return results
