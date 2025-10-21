"""
Mock Image API Client - v2.0
==============================

Fast mock implementation for testing.

In production, this will be replaced with real image generation API client.
"""

import asyncio
import logging
from typing import Dict, Any

from orchestration.models.director_models import GeneratedImage

logger = logging.getLogger(__name__)


class MockImageClient:
    """
    Mock image generation API client.

    Simulates fast image generation with placeholder URLs.
    """

    def __init__(self, delay_ms: int = 200):
        """
        Initialize mock client.

        Args:
            delay_ms: Simulated API delay in milliseconds
        """
        self.delay_ms = delay_ms
        logger.info(f"MockImageClient initialized (delay: {delay_ms}ms)")

    async def generate(self, request: Dict[str, Any]) -> GeneratedImage:
        """
        Generate mock image.

        Args:
            request: Request dict with goal, content, style, dimensions

        Returns:
            GeneratedImage with URL and caption
        """
        # Simulate API delay
        await asyncio.sleep(self.delay_ms / 1000.0)

        goal = request.get("goal", "")
        content = request.get("content", "")
        style = request.get("style", "")
        dimensions = request.get("dimensions", {
            "width": 1600,
            "height": 900,
            "aspect_ratio": "16:9"
        })

        # Generate caption from goal or content
        if goal:
            caption = goal
        elif content:
            caption = content
        else:
            caption = "Illustrative image"

        # Generate URL based on aspect ratio and slide number
        aspect_ratio = dimensions.get("aspect_ratio", "16:9")
        width = dimensions.get("width", 1600)
        height = dimensions.get("height", 900)
        slide_number = request.get("slide_number", "000")

        url = f"https://cdn.example.com/images/{aspect_ratio.replace(':', 'x')}-{slide_number}.jpg"

        return GeneratedImage(
            url=url,
            caption=caption,
            metadata={
                "source": "mock_image_client",
                "style": style,
                "dimensions": dimensions,
                "delay_ms": self.delay_ms
            }
        )

    async def generate_batch(
        self,
        requests: list[Dict[str, Any]]
    ) -> list[GeneratedImage]:
        """
        Generate batch of images.

        Args:
            requests: List of request dicts

        Returns:
            List of GeneratedImage
        """
        tasks = [self.generate(req) for req in requests]
        results = await asyncio.gather(*tasks)
        return results
