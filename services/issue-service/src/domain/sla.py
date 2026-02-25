"""
Service Level Agreement (SLA) domain logic.
Defines expected resolution times based on priority.
"""

from datetime import timedelta
from shared.schemas import IssuePriority

# SLA configuration (Time to Resolve in hours)
SLA_HOURS: dict[IssuePriority, int] = {
    IssuePriority.LOW: 168,      # 1 week
    IssuePriority.MEDIUM: 72,    # 3 days
    IssuePriority.HIGH: 24,      # 1 day
    IssuePriority.URGENT: 4      # 4 hours
}

class SLAService:
    """Service to handle SLA calculations."""

    @staticmethod
    def get_sla_hours(priority: IssuePriority) -> int:
        """Get SLA hours for a priority."""
        return SLA_HOURS.get(priority, 168)

    @staticmethod
    def get_expected_resolution_time(priority: IssuePriority) -> timedelta:
        """Get expected resolution timedelta."""
        hours = SLAService.get_sla_hours(priority)
        return timedelta(hours=hours)

    @staticmethod
    def is_urgent(priority: IssuePriority) -> bool:
        """Check if priority counts as urgent."""
        return priority == IssuePriority.URGENT
