"""Workflow router."""

from fastapi import APIRouter, HTTPException, status
from typing import List

from shared.schemas import IssueStatus
from src.domain.workflow import WorkflowService

router = APIRouter()

@router.get("/transitions", response_model=List[IssueStatus])
async def get_allowed_transitions(current_status: IssueStatus):
    """Get allowed transitions for a given status."""
    transitions = WorkflowService.get_allowed_transitions(current_status)
    return list(transitions)
