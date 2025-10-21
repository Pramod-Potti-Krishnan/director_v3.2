"""
Mock Diagram API Client - v2.0
================================

Fast mock implementation for testing.

In production, this will be replaced with real diagram generation API client.
"""

import asyncio
import logging
from typing import Dict, Any

from orchestration.models.director_models import GeneratedDiagram

logger = logging.getLogger(__name__)


class MockDiagramClient:
    """
    Mock diagram generation API client.

    Simulates fast diagram generation with placeholder SVG URLs.
    """

    def __init__(self, delay_ms: int = 150):
        """
        Initialize mock client.

        Args:
            delay_ms: Simulated API delay in milliseconds
        """
        self.delay_ms = delay_ms
        logger.info(f"MockDiagramClient initialized (delay: {delay_ms}ms)")

    async def generate(self, request: Dict[str, Any]) -> GeneratedDiagram:
        """
        Generate mock diagram.

        Args:
            request: Request dict with goal, content, diagram_type, style

        Returns:
            GeneratedDiagram with URL
        """
        # Simulate API delay
        await asyncio.sleep(self.delay_ms / 1000.0)

        diagram_type = request.get("diagram_type", "flowchart")
        goal = request.get("goal", "")
        content = request.get("content", "")
        slide_number = request.get("slide_number", "000")

        # Generate URL
        url = f"https://cdn.example.com/diagrams/{diagram_type}-{slide_number}.svg"

        return GeneratedDiagram(
            type=diagram_type,
            url=url,
            metadata={
                "source": "mock_diagram_client",
                "goal": goal,
                "content": content,
                "delay_ms": self.delay_ms
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
