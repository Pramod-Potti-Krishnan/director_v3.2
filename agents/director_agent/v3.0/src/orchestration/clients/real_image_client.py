# -*- coding: utf-8 -*-
"""
Real Image Builder Service Client - v2.0
==========================================

Integration with Image Builder v2.0 Railway service.

Service Details:
- Production URL: https://web-production-1b5df.up.railway.app
- Synchronous API (7-12s response time)
- Custom aspect ratios (2:7, 21:9, 16:9, etc.)
- Vertex AI Imagen 3 powered
"""

import os
import asyncio
import logging
from typing import Dict, Any
import requests
from dotenv import load_dotenv

from orchestration.models.director_models import GeneratedImage

load_dotenv()
logger = logging.getLogger(__name__)


class RealImageClient:
    """
    Real Image Builder service client.

    Integrates with production Railway deployment, replacing MockImageClient.
    """

    def __init__(self, base_url: str = None):
        """
        Initialize image service client.

        Args:
            base_url: Override URL (default: from IMAGE_SERVICE_URL env var)
        """
        self.base_url = base_url or os.getenv(
            "IMAGE_SERVICE_URL",
            "https://web-production-1b5df.up.railway.app"
        )
        self.api_base = f"{self.base_url}/api/v2"
        self.timeout = int(os.getenv("IMAGE_SERVICE_TIMEOUT", "60"))

        logger.info(f"RealImageClient initialized (url: {self.base_url}, timeout: {self.timeout}s)")

    async def generate(self, request: Dict[str, Any]) -> GeneratedImage:
        """
        Generate image from production service.

        Args:
            request: Orchestrator request with goal, content, style, dimensions
                Expected keys:
                - goal: str - Image description/prompt
                - content: str - Alternative prompt
                - style: str - Image style/archetype
                - dimensions: Dict - Width, height, aspect_ratio
                - slide_number: int - For reference

        Returns:
            GeneratedImage with URL and metadata
        """
        # Transform request to service format
        service_request = self._transform_request(request)

        # Run synchronous HTTP request in executor (non-blocking)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            self._sync_generate_image,
            service_request
        )

        # Transform response to orchestrator format
        return self._transform_response(response, request)

    def _sync_generate_image(self, request: Dict) -> Dict:
        """
        Synchronous HTTP request to Image service.

        Args:
            request: Service-formatted request

        Returns:
            Service response dict

        Raises:
            requests.HTTPError: On API errors
            requests.Timeout: On timeout
        """
        endpoint = f"{self.api_base}/generate"

        try:
            response = requests.post(
                endpoint,
                json=request,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.Timeout as e:
            logger.error(f"Image service timeout after {self.timeout}s")
            raise
        except requests.HTTPError as e:
            logger.error(f"Image service HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Image service request failed: {str(e)}")
            raise

    def _transform_request(self, orchestrator_request: Dict) -> Dict:
        """
        Transform orchestrator request to Image service format.

        Image Service API expects:
        {
            "prompt": str,
            "aspect_ratio": str,
            "archetype": str,
            "options": {
                "remove_background": bool,
                "crop_anchor": str,
                "store_in_cloud": bool
            }
        }
        """
        # Extract prompt from goal or content
        prompt = orchestrator_request.get("goal") or orchestrator_request.get("content", "")

        # Extract aspect ratio from dimensions
        dimensions = orchestrator_request.get("dimensions", {})
        aspect_ratio = dimensions.get("aspect_ratio", "16:9")

        # Extract style/archetype
        style = orchestrator_request.get("style", "spot_illustration")

        return {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "archetype": style,
            "options": {
                "remove_background": orchestrator_request.get("remove_background", False),
                "crop_anchor": orchestrator_request.get("crop_anchor", "center"),
                "store_in_cloud": True
            }
        }

    def _transform_response(self, service_response: Dict, original_request: Dict) -> GeneratedImage:
        """
        Transform Image service response to orchestrator format.

        Service response format:
        {
            "success": bool,
            "image_id": str,
            "urls": {
                "original": str,
                "cropped": str,
                "transparent": str
            },
            "metadata": {
                "model": str,
                "target_aspect_ratio": str,
                "generation_time_ms": int,
                ...
            }
        }

        Returns:
            GeneratedImage model
        """
        # Use cropped URL if available, otherwise original
        urls = service_response.get("urls", {})
        image_url = urls.get("cropped") or urls.get("original", "")

        # Generate caption from original request
        caption = original_request.get("goal") or original_request.get("content", "")

        return GeneratedImage(
            url=image_url,
            caption=caption,
            metadata={
                "image_id": service_response.get("image_id"),
                "aspect_ratio": service_response["metadata"].get("target_aspect_ratio"),
                "generation_time_ms": service_response["metadata"].get("generation_time_ms"),
                "model": service_response["metadata"].get("model"),
                "all_urls": urls,
                "source": "image_service_v2.0"
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
