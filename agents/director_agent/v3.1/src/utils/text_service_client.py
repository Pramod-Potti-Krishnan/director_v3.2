"""
Text & Table Builder Service Client - v3.1
===========================================

Integration with Text & Table Builder v1.0 Railway service.

Service Details:
- Production URL: https://web-production-e3796.up.railway.app
- Synchronous API (5-15s response time)
- Session-based context retention (1-hour TTL, last 5 slides)
- LLM-powered with Gemini 2.5-flash default
"""

import asyncio
from typing import Dict, Any
import requests
from src.utils.logger import setup_logger
from src.models.content import GeneratedText  # Use Pydantic model

logger = setup_logger(__name__)


class TextServiceClient:
    """
    Text & Table Builder service client for v3.1.

    Simplified version focusing on TEXT ONLY generation.
    No batch processing, no complex orchestration.
    """

    def __init__(self, base_url: str = None):
        """
        Initialize text service client.

        Args:
            base_url: Override URL (default: production Railway URL)
        """
        self.base_url = base_url or "https://web-production-e3796.up.railway.app"
        self.api_base = f"{self.base_url}/api/v1"
        self.timeout = 60  # 60 seconds timeout

        logger.info(f"TextServiceClient initialized (url: {self.base_url}, timeout: {self.timeout}s)")

    async def generate(self, request: Dict[str, Any]) -> GeneratedText:
        """
        Generate text/table content from production service.

        Args:
            request: Request with topics, narrative, context, constraints
                Expected keys:
                - topics: List[str] - Topics to expand
                - narrative: str - Context/narrative
                - context: Dict - Presentation and slide context
                - constraints: Dict - Word count, tone, format constraints
                - slide_id: str - Slide identifier
                - slide_number: int - Slide position
                - presentation_id: str - Presentation identifier (for session tracking)

        Returns:
            GeneratedText with content and metadata

        Raises:
            Exception: On API errors or timeouts
        """
        # Transform request to service format
        service_request = self._transform_request(request)

        # Run synchronous HTTP request in executor (non-blocking)
        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                self._sync_generate_text,
                service_request
            )
        except Exception as e:
            logger.error(f"Text Service call failed: {str(e)}")
            raise

        # Transform response to our format
        return self._transform_response(response)

    def _sync_generate_text(self, request: Dict) -> Dict:
        """
        Synchronous HTTP request to Text service.

        Args:
            request: Service-formatted request

        Returns:
            Service response dict

        Raises:
            requests.HTTPError: On API errors
            requests.Timeout: On timeout
        """
        endpoint = f"{self.api_base}/generate/text"

        try:
            logger.info(f"Calling Text Service: {endpoint}")
            response = requests.post(
                endpoint,
                json=request,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Text Service responded: {response.status_code}")
            return response.json()

        except requests.Timeout as e:
            logger.error(f"Text service timeout after {self.timeout}s")
            raise Exception(f"Text Service timeout after {self.timeout}s")
        except requests.HTTPError as e:
            logger.error(f"Text service HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Text Service HTTP error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Text service request failed: {str(e)}")
            raise

    def _transform_request(self, orchestrator_request: Dict) -> Dict:
        """
        Transform orchestrator request to Text service format.

        Text Service API expects:
        {
            "presentation_id": str,
            "slide_id": str,
            "slide_number": int,
            "topics": List[str],
            "narrative": str,
            "context": {
                "presentation_context": str,
                "slide_context": str,
                "previous_slides": List[Dict]
            },
            "constraints": {
                "word_count": int,
                "tone": str,
                "format": str
            }
        }
        """
        return {
            "presentation_id": orchestrator_request.get("presentation_id", "default_pres"),
            "slide_id": orchestrator_request.get("slide_id", "unknown"),
            "slide_number": orchestrator_request.get("slide_number", 1),
            "topics": orchestrator_request.get("topics", []),
            "narrative": orchestrator_request.get("narrative", ""),
            "context": {
                "presentation_context": orchestrator_request.get("context", {}).get("presentation_context", ""),
                "slide_context": orchestrator_request.get("context", {}).get("slide_context", ""),
                "previous_slides": orchestrator_request.get("context", {}).get("previous_slides", [])
            },
            "constraints": {
                "word_count": orchestrator_request.get("constraints", {}).get("word_count", 150),
                "tone": orchestrator_request.get("constraints", {}).get("tone", "professional"),
                "format": orchestrator_request.get("constraints", {}).get("format", "paragraph")
            }
        }

    def _transform_response(self, service_response: Dict) -> GeneratedText:
        """
        Transform Text service response to our format.

        Service response format:
        {
            "content": str (HTML),
            "metadata": {
                "word_count": int,
                "generation_time_ms": int,
                "model_used": str
            },
            "session_id": str
        }

        Returns:
            GeneratedText object
        """
        return GeneratedText(
            content=service_response["content"],
            metadata={
                "word_count": service_response["metadata"]["word_count"],
                "generation_time_ms": service_response["metadata"]["generation_time_ms"],
                "model_used": service_response["metadata"]["model_used"],
                "session_id": service_response.get("session_id"),
                "source": "text_service_v1.0"
            }
        )
