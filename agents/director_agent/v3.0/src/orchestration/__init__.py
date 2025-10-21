"""
Internal Content Orchestration Module
======================================

Consolidated orchestration logic for coordinating content generation services.
Previously a separate microservice (Content Orchestrator v2.0), now integrated
directly into Director Agent for simplified architecture and reduced latency.
"""

from orchestration.orchestrator import ContentOrchestratorV2 as ContentOrchestrator

__all__ = ["ContentOrchestrator"]
