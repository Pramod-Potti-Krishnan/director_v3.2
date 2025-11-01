"""
Checkpoint Manager for Director E2E Testing
============================================

This module provides functionality to save and load test checkpoints,
allowing tests to start from any stage with pre-generated data.

Author: AI Assistant
Date: 2024
Version: 1.0
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


class CheckpointManager:
    """Manages checkpoint saving and loading for E2E tests."""
    
    # Define stage order and dependencies
    STAGES = [
        "PROVIDE_GREETING",
        "ASK_CLARIFYING_QUESTIONS", 
        "CREATE_CONFIRMATION_PLAN",
        "GENERATE_STRAWMAN",
        "REFINE_STRAWMAN",
        "CONTENT_GENERATION"
    ]
    
    # Map stages to their checkpoint file names
    STAGE_FILES = {
        "PROVIDE_GREETING": "stage_1_greeting.json",
        "ASK_CLARIFYING_QUESTIONS": "stage_2_clarifying.json",
        "CREATE_CONFIRMATION_PLAN": "stage_3_confirmation.json",
        "GENERATE_STRAWMAN": "stage_4_strawman.json",
        "REFINE_STRAWMAN": "stage_5_refined.json",
        "CONTENT_GENERATION": "stage_6_content_ready.json"
    }
    
    def __init__(self, checkpoint_dir: str = None):
        """
        Initialize the checkpoint manager.
        
        Args:
            checkpoint_dir: Base directory for checkpoints (default: test/checkpoints)
        """
        if checkpoint_dir:
            self.checkpoint_dir = Path(checkpoint_dir)
        else:
            # Default to test/checkpoints relative to this file
            self.checkpoint_dir = Path(__file__).parent / "checkpoints"
        
        # Ensure checkpoint directory exists
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def save_checkpoint(
        self,
        scenario: str,
        stage: str,
        context: Any,
        outputs: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a checkpoint for a specific stage.
        
        Args:
            scenario: The scenario name (e.g., "default", "executive")
            stage: The stage name (e.g., "GENERATE_STRAWMAN")
            context: The StateContext object
            outputs: Dictionary of outputs from previous stages
            metadata: Optional additional metadata
            
        Returns:
            Path to the saved checkpoint file
        """
        # Validate stage
        if stage not in self.STAGES:
            raise ValueError(f"Invalid stage: {stage}. Must be one of {self.STAGES}")
        
        # Create scenario directory if needed
        scenario_dir = self.checkpoint_dir / scenario
        scenario_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare checkpoint data
        checkpoint_data = {
            "checkpoint_version": "1.0",
            "scenario": scenario,
            "stage": stage,
            "timestamp": datetime.utcnow().isoformat(),
            "context": {
                "current_state": context.current_state,
                "conversation_history": [
                    {
                        "role": msg["role"],
                        "content": msg["content"]
                    }
                    for msg in context.conversation_history
                ],
                "session_data": context.session_data,
                "user_intent": context.user_intent.value if context.user_intent else None
            },
            "stage_outputs": outputs,
            "metadata": metadata or {}
        }
        
        # Convert any model objects to dicts
        checkpoint_data = self._serialize_checkpoint(checkpoint_data)
        
        # Save to file
        checkpoint_file = scenario_dir / self.STAGE_FILES[stage]
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2, default=str)
        
        print(f"✅ Checkpoint saved: {checkpoint_file}")
        return str(checkpoint_file)
    
    def load_checkpoint(
        self,
        scenario: str,
        stage: str
    ) -> Dict[str, Any]:
        """
        Load a checkpoint for a specific stage.
        
        Args:
            scenario: The scenario name
            stage: The stage to load
            
        Returns:
            Dictionary containing checkpoint data
        """
        # Validate stage
        if stage not in self.STAGES:
            raise ValueError(f"Invalid stage: {stage}. Must be one of {self.STAGES}")
        
        # Find checkpoint file
        checkpoint_file = self.checkpoint_dir / scenario / self.STAGE_FILES[stage]
        
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_file}")
        
        # Load checkpoint
        with open(checkpoint_file, 'r') as f:
            checkpoint_data = json.load(f)
        
        # Validate version
        if checkpoint_data.get("checkpoint_version") != "1.0":
            raise ValueError(f"Unsupported checkpoint version: {checkpoint_data.get('checkpoint_version')}")
        
        print(f"✅ Checkpoint loaded: {checkpoint_file}")
        print(f"   Stage: {checkpoint_data['stage']}")
        print(f"   Timestamp: {checkpoint_data['timestamp']}")
        
        return checkpoint_data
    
    def load_checkpoint_file(self, filepath: str) -> Dict[str, Any]:
        """
        Load a checkpoint from a specific file path.
        
        Args:
            filepath: Path to the checkpoint file
            
        Returns:
            Dictionary containing checkpoint data
        """
        checkpoint_file = Path(filepath)
        
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint file not found: {filepath}")
        
        with open(checkpoint_file, 'r') as f:
            checkpoint_data = json.load(f)
        
        # Validate version
        if checkpoint_data.get("checkpoint_version") != "1.0":
            raise ValueError(f"Unsupported checkpoint version: {checkpoint_data.get('checkpoint_version')}")
        
        print(f"✅ Checkpoint loaded from file: {filepath}")
        return checkpoint_data
    
    def list_checkpoints(self, scenario: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List available checkpoints.
        
        Args:
            scenario: Optional scenario to filter by
            
        Returns:
            List of checkpoint info dictionaries
        """
        checkpoints = []
        
        if scenario:
            # List checkpoints for specific scenario
            scenario_dir = self.checkpoint_dir / scenario
            if scenario_dir.exists():
                for stage, filename in self.STAGE_FILES.items():
                    filepath = scenario_dir / filename
                    if filepath.exists():
                        checkpoints.append({
                            "scenario": scenario,
                            "stage": stage,
                            "file": str(filepath),
                            "exists": True
                        })
        else:
            # List all checkpoints
            for scenario_dir in self.checkpoint_dir.iterdir():
                if scenario_dir.is_dir():
                    scenario_name = scenario_dir.name
                    for stage, filename in self.STAGE_FILES.items():
                        filepath = scenario_dir / filename
                        if filepath.exists():
                            checkpoints.append({
                                "scenario": scenario_name,
                                "stage": stage,
                                "file": str(filepath),
                                "exists": True
                            })
        
        return checkpoints
    
    def get_stage_index(self, stage: str) -> int:
        """Get the index of a stage in the progression."""
        if stage not in self.STAGES:
            raise ValueError(f"Invalid stage: {stage}")
        return self.STAGES.index(stage)
    
    def get_previous_stages(self, stage: str) -> List[str]:
        """Get all stages that come before the given stage."""
        stage_index = self.get_stage_index(stage)
        return self.STAGES[:stage_index]
    
    def _serialize_checkpoint(self, data: Any) -> Any:
        """
        Recursively serialize checkpoint data, converting objects to dicts.
        """
        if hasattr(data, 'model_dump'):
            # Pydantic model
            return data.model_dump()
        elif hasattr(data, 'dict'):
            # Pydantic model (older version)
            return data.dict()
        elif hasattr(data, '__dict__') and not isinstance(data, type):
            # Regular object with __dict__
            return {k: self._serialize_checkpoint(v) for k, v in data.__dict__.items()}
        elif isinstance(data, dict):
            # Dictionary
            return {k: self._serialize_checkpoint(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            # List or tuple
            return [self._serialize_checkpoint(item) for item in data]
        elif isinstance(data, (str, int, float, bool, type(None))):
            # Primitive types
            return data
        else:
            # Convert to string as fallback
            return str(data)
    
    def validate_checkpoint(self, checkpoint_data: Dict[str, Any]) -> bool:
        """
        Validate that checkpoint data has required fields.
        
        Args:
            checkpoint_data: The checkpoint data to validate
            
        Returns:
            True if valid, raises ValueError if not
        """
        required_fields = ["checkpoint_version", "scenario", "stage", "context", "stage_outputs"]
        
        for field in required_fields:
            if field not in checkpoint_data:
                raise ValueError(f"Checkpoint missing required field: {field}")
        
        # Validate stage
        if checkpoint_data["stage"] not in self.STAGES:
            raise ValueError(f"Invalid stage in checkpoint: {checkpoint_data['stage']}")
        
        # Validate context
        context = checkpoint_data["context"]
        required_context_fields = ["current_state", "conversation_history", "session_data"]
        for field in required_context_fields:
            if field not in context:
                raise ValueError(f"Checkpoint context missing required field: {field}")
        
        return True