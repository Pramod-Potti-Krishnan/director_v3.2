"""
Mock Text API Client - v2.0
=============================

Fast mock implementation for testing.

In production, this will be replaced with real text generation API client.
"""

import asyncio
import logging
from typing import Dict, Any

from orchestration.models.director_models import GeneratedText

logger = logging.getLogger(__name__)


class MockTextClient:
    """
    Mock text generation API client.

    Simulates fast text generation without actual API calls.
    """

    def __init__(self, delay_ms: int = 100):
        """
        Initialize mock client.

        Args:
            delay_ms: Simulated API delay in milliseconds
        """
        self.delay_ms = delay_ms
        logger.info(f"MockTextClient initialized (delay: {delay_ms}ms)")

    async def generate(self, request: Dict[str, Any]) -> GeneratedText:
        """
        Generate mock text from topics.

        Args:
            request: Request dict with topics, narrative, context, constraints

        Returns:
            GeneratedText
        """
        # Simulate API delay
        await asyncio.sleep(self.delay_ms / 1000.0)

        topics = request.get("topics", [])
        narrative = request.get("narrative", "")
        context = request.get("context", {})
        constraints = request.get("constraints", {})

        # Generate mock content from topics
        expanded_content = []

        for topic in topics:
            topic_lower = topic.lower()

            # Pattern matching for realistic expansion
            if "revenue" in topic_lower and "growth" in topic_lower:
                expanded_content.append(
                    "Q3 revenue reached $127M, representing 32% growth over Q2."
                )
            elif "margin" in topic_lower or "ebitda" in topic_lower:
                expanded_content.append(
                    "EBITDA margin improved to 32.3%, up 340 basis points year-over-year."
                )
            elif "cost" in topic_lower:
                expanded_content.append(
                    "Operating costs reduced by 28% through efficiency initiatives."
                )
            elif "market" in topic_lower:
                expanded_content.append(
                    "Market share increased to 23.5%, driven by product innovation."
                )
            elif "customer" in topic_lower:
                expanded_content.append(
                    "Customer satisfaction scores reached 92%, highest in company history."
                )
            else:
                # Generic expansion
                expanded_content.append(
                    f"{topic}: Significant progress achieved with measurable results."
                )

        content = " ".join(expanded_content)

        # Respect character limit if provided
        max_chars = constraints.get("max_characters")
        if max_chars and len(content) > max_chars:
            content = content[:max_chars - 3] + "..."

        return GeneratedText(
            content=content,
            metadata={
                "word_count": len(content.split()),
                "source": "mock_text_client",
                "topics_count": len(topics),
                "delay_ms": self.delay_ms
            }
        )

    async def generate_batch(
        self,
        requests: list[Dict[str, Any]]
    ) -> list[GeneratedText]:
        """
        Generate batch of texts.

        Args:
            requests: List of request dicts

        Returns:
            List of GeneratedText
        """
        tasks = [self.generate(req) for req in requests]
        results = await asyncio.gather(*tasks)
        return results
