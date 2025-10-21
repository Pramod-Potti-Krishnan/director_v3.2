"""
Simple state machine for Deckster workflow orchestration.
"""
from typing import Dict, Any, Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class WorkflowOrchestrator:
    """
    Simple workflow orchestrator for state management.
    
    This is a placeholder for Phase 1. In future phases, this could be
    enhanced with LangGraph for more complex workflows.
    """
    
    # Valid states
    STATES = [
        "PROVIDE_GREETING",
        "ASK_CLARIFYING_QUESTIONS",
        "CREATE_CONFIRMATION_PLAN",
        "GENERATE_STRAWMAN",
        "REFINE_STRAWMAN",
        "CONTENT_GENERATION"  # v3.1: Stage 6 - Text Service content generation
    ]

    # State transitions
    TRANSITIONS = {
        "PROVIDE_GREETING": ["ASK_CLARIFYING_QUESTIONS"],
        "ASK_CLARIFYING_QUESTIONS": ["CREATE_CONFIRMATION_PLAN"],  # Only forward, no loops
        "CREATE_CONFIRMATION_PLAN": ["GENERATE_STRAWMAN", "ASK_CLARIFYING_QUESTIONS", "CREATE_CONFIRMATION_PLAN"],
        "GENERATE_STRAWMAN": ["REFINE_STRAWMAN", "CONTENT_GENERATION"],  # v3.1: Can go to Stage 6
        "REFINE_STRAWMAN": ["REFINE_STRAWMAN", "CONTENT_GENERATION"],    # v3.1: Can go to Stage 6
        "CONTENT_GENERATION": []  # v3.1: Terminal state - enriched content ready
    }
    
    def __init__(self):
        """Initialize the workflow orchestrator."""
        logger.info("WorkflowOrchestrator initialized")
    
    def validate_state(self, state: str) -> bool:
        """
        Validate if a state is valid.
        
        Args:
            state: State to validate
            
        Returns:
            True if valid, False otherwise
        """
        return state in self.STATES
    
    def validate_transition(self, from_state: str, to_state: str) -> bool:
        """
        Validate if a state transition is allowed.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            True if transition is valid, False otherwise
        """
        if from_state not in self.TRANSITIONS:
            return False
        
        return to_state in self.TRANSITIONS[from_state]
    
    def get_next_states(self, current_state: str) -> list:
        """
        Get possible next states from current state.
        
        Args:
            current_state: Current state
            
        Returns:
            List of possible next states
        """
        return self.TRANSITIONS.get(current_state, [])