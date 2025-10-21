"""
Mock Chart API Client - v2.0
==============================

Fast mock implementation for testing.

In production, this will be replaced with real chart generation API client.
"""

import asyncio
import logging
from typing import Dict, Any

from orchestration.models.director_models import GeneratedChart

logger = logging.getLogger(__name__)


class MockChartClient:
    """
    Mock chart generation API client.

    Simulates fast chart generation with Chart.js data.
    """

    def __init__(self, delay_ms: int = 150):
        """
        Initialize mock client.

        Args:
            delay_ms: Simulated API delay in milliseconds
        """
        self.delay_ms = delay_ms
        logger.info(f"MockChartClient initialized (delay: {delay_ms}ms)")

    async def generate(self, request: Dict[str, Any]) -> GeneratedChart:
        """
        Generate mock chart with Chart.js data.

        Args:
            request: Request dict with goal, content, chart_type, style, dimensions

        Returns:
            GeneratedChart with Chart.js data
        """
        # Simulate API delay
        await asyncio.sleep(self.delay_ms / 1000.0)

        chart_type = request.get("chart_type", "bar")
        content = request.get("content", "").lower()
        goal = request.get("goal", "")
        dimensions = request.get("dimensions", {"width": 800, "height": 400})

        # Generate realistic Chart.js data based on content
        if "revenue" in content:
            data = {
                "labels": ["Q4 '24", "Q1 '25", "Q2 '25", "Q3 '25"],
                "datasets": [
                    {
                        "label": "Revenue ($M)",
                        "data": [95, 107, 118, 127],
                        "backgroundColor": ["#e0e0e0", "#e0e0e0", "#e0e0e0", "#007bff"],
                        "borderColor": "#333",
                        "borderWidth": 1
                    }
                ]
            }
        elif "margin" in content or "ebitda" in content:
            data = {
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "datasets": [
                    {
                        "label": "EBITDA Margin (%)",
                        "data": [28.5, 29.8, 31.2, 32.3],
                        "borderColor": "#007bff",
                        "backgroundColor": "rgba(0, 123, 255, 0.1)",
                        "fill": True,
                        "tension": 0.4
                    }
                ]
            }
        elif "cost" in content:
            data = {
                "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                "datasets": [
                    {
                        "label": "Operating Costs ($M)",
                        "data": [45, 43, 40, 38, 35, 32],
                        "borderColor": "#dc3545",
                        "backgroundColor": "rgba(220, 53, 69, 0.1)",
                        "fill": True
                    }
                ]
            }
        elif "market" in content:
            data = {
                "labels": ["Us", "Competitor A", "Competitor B", "Others"],
                "datasets": [
                    {
                        "label": "Market Share (%)",
                        "data": [23.5, 19.2, 15.8, 41.5],
                        "backgroundColor": ["#007bff", "#6c757d", "#6c757d", "#e0e0e0"]
                    }
                ]
            }
        else:
            # Generic data
            data = {
                "labels": ["Jan", "Feb", "Mar", "Apr"],
                "datasets": [
                    {
                        "label": "Metric",
                        "data": [12, 19, 15, 25],
                        "backgroundColor": "#007bff"
                    }
                ]
            }

        # Generate URL (mock CDN)
        url = f"https://cdn.example.com/charts/chart-{chart_type}-{request.get('slide_number', '000')}.png"

        return GeneratedChart(
            type=chart_type,
            data=data,
            url=url,
            metadata={
                "source": "mock_chart_client",
                "goal": goal,
                "dimensions": dimensions,
                "delay_ms": self.delay_ms
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
