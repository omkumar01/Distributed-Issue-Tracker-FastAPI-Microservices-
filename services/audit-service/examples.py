"""
Audit Service - Real-World Usage Examples

Example code for common audit logging scenarios.
"""

import asyncio
from uuid import uuid4
from datetime import datetime, timedelta
import httpx
from typing import Optional

# ============================================================================
# 1. LOGGING AUDIT EVENTS FROM OTHER SERVICES
# ============================================================================

async def example_log_user_creation():
    """
    Example: User Service logs when a new user is created.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/v1",
            json={
                "actor_id": str(uuid4()),  # Admin who created the user
                "action": "create",
                "resource_id": str(uuid4()),  # New user ID
                "resource_type": "user",
                "new_values": {
                    "username": "john.doe",
                    "email": "john@example.com",
                    "role": "developer"
                },
                "status": "success",
                "service": "user-service"
            }
        )
        print(f"Logged user creation: {response.status_code}")
        return response.json()


async def example_log_project_permission_change():
    """
    Example: Project Service logs permission changes.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/v1",
            json={
                "actor_id": str(uuid4()),  # Project owner
                "action": "update",
                "resource_id": str(uuid4()),  # Project ID
                "resource_type": "project",
                "old_values": {
                    "permissions": ["owner"]
                },
                "new_values": {
                    "permissions": ["owner", "editor", "viewer"]
                },
                "changes": {
                    "permissions": {
                        "old": ["owner"],
                        "new": ["owner", "editor", "viewer"]
                    }
                },
                "status": "success",
                "service": "project-service"
            }
        )
        print(f"Logged permission change: {response.status_code}")
        return response.json()


async def example_log_failed_action():
    """
    Example: Log a failed operation with error details.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/v1",
            json={
                "actor_id": str(uuid4()),
                "action": "delete",
                "resource_id": str(uuid4()),
                "resource_type": "issue",
                "status": "failure",
                "error_message": "Cannot delete issue with open comments",
                "service": "issue-service"
            }
        )
        print(f"Logged failed action: {response.status_code}")
        return response.json()


# ============================================================================
# 2. QUERYING AUDIT LOGS FOR COMPLIANCE
# ============================================================================

async def example_get_user_activity():
    """
    Example: Get all activities performed by a specific user.
    """
    user_id = uuid4()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8001/api/v1/user/{user_id}/activity"
        )
        activity = response.json()
        
        print(f"\nUser {user_id} activity:")
        print(f"Total actions: {activity['total']}")
        
        # Print recent actions
        for log in activity['items'][:5]:
            print(f"  - {log['action']} on {log['resource_type']} ({log['created_at']})")
        
        return activity


async def example_get_resource_history():
    """
    Example: Get complete change history for a resource (e.g., issue).
    
    Useful for:
    - Understanding how an issue evolved
    - Compliance audit trails
    - Troubleshooting changes
    """
    issue_id = uuid4()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8001/api/v1/resource/{issue_id}",
            params={"resource_type": "issue"}
        )
        history = response.json()
        
        print(f"\nIssue {issue_id} change history:")
        print(f"Total changes: {history['total_changes']}")
        
        # Print timeline
        for change in history['change_timeline']:
            print(f"\n  {change['timestamp']}")
            print(f"  Action: {change['action']}")
            print(f"  Actor: {change['actor_id']}")
            if change['changes']:
                print(f"  Changes:")
                for field, values in change['changes'].items():
                    print(f"    {field}: {values['old']} → {values['new']}")
        
        return history


async def example_list_audit_logs_with_filters():
    """
    Example: List audit logs with various filters.
    
    Useful for:
    - Finding specific events
    - Compliance investigations
    - Security monitoring
    """
    async with httpx.AsyncClient() as client:
        # Find all failed actions in the last 7 days
        response = await client.get(
            "http://localhost:8001/api/v1/logs",
            params={
                "status": "failure",
                "skip": 0,
                "limit": 50
            }
        )
        
        failed_logs = response.json()
        
        print(f"\nFailed actions in audit log:")
        print(f"Total: {failed_logs['total']}")
        
        for log in failed_logs['items']:
            print(f"  - {log['action']} by {log['actor_id']} ({log['error_message']})")
        
        return failed_logs


# ============================================================================
# 3. COMPLIANCE & SECURITY MONITORING
# ============================================================================

async def example_get_statistics_report():
    """
    Example: Generate activity statistics for compliance report.
    
    Useful for:
    - Monthly compliance reports
    - Executive summaries
    - Trend analysis
    """
    async with httpx.AsyncClient() as client:
        # Get last 30 days of statistics
        response = await client.get(
            "http://localhost:8001/api/v1/stats",
            params={"days": 30}
        )
        
        stats = response.json()
        
        print("\n=== 30-Day Activity Report ===")
        print(f"Total actions: {stats['total_actions']}")
        print(f"Success rate: {(stats['actions_by_status'].get('success', 0) / stats['total_actions'] * 100):.1f}%")
        print(f"Failed actions: {stats['actions_by_status'].get('failure', 0)}")
        
        print(f"\nActions by type:")
        for action, count in stats['actions_by_type'].items():
            print(f"  {action}: {count}")
        
        print(f"\nMost active services:")
        sorted_services = sorted(stats['actions_by_service'].items(), key=lambda x: x[1], reverse=True)
        for service, count in sorted_services[:5]:
            print(f"  {service}: {count}")
        
        print(f"\nMost active user: {stats['most_active_user']}")
        print(f"Actions in last 24h: {stats['actions_last_24h']}")
        
        return stats


async def example_log_data_access():
    """
    Example: Log access to sensitive data.
    
    Useful for:
    - GDPR/privacy compliance
    - Sensitive data tracking
    - Security audits
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/v1/data-access",
            json={
                "actor_id": str(uuid4()),
                "resource_id": str(uuid4()),
                "resource_type": "user",
                "fields_accessed": ["email", "phone", "ssn"],
                "access_method": "export",
                "operation": "export",
                "purpose": "GDPR data export request",
                "was_authorized": True
            }
        )
        
        print(f"Logged sensitive data access: {response.status_code}")
        return response.json()


async def example_find_unauthorized_access():
    """
    Example: Find unauthorized access attempts.
    
    Useful for:
    - Security incident response
    - Access control violation detection
    - Compliance audits
    """
    async with httpx.AsyncClient() as client:
        # Find unauthorized access in last 7 days
        response = await client.get(
            "http://localhost:8001/api/v1/data-access/unauthorized",
            params={
                "days": 7,
                "limit": 100
            }
        )
        
        unauthorized = response.json()
        
        print(f"\n⚠️  Unauthorized Access Attempts (Last 7 Days)")
        print(f"Total: {unauthorized['total']}")
        
        if unauthorized['total'] > 0:
            for access in unauthorized['items']:
                print(f"\n  User: {access['actor_id']}")
                print(f"  Tried to access: {access['resource_type']} ({access['resource_id']})")
                print(f"  Method: {access['access_method']}")
                print(f"  Time: {access['accessed_at']}")
        
        return unauthorized


async def example_create_compliance_event():
    """
    Example: Log a compliance-related event.
    
    Useful for:
    - Policy violations
    - Security incidents
    - Regulatory events
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/v1/compliance",
            json={
                "event_type": "unauthorized_access_attempt",
                "severity": "critical",
                "actor_id": str(uuid4()),
                "action": "unauthorized_access",
                "resource_id": str(uuid4()),
                "resource_type": "user_data",
                "description": "Multiple unauthorized access attempts detected",
                "details": {
                    "attempt_count": 5,
                    "time_period": "10 minutes",
                    "ip_addresses": ["192.168.1.100", "192.168.1.101"],
                    "suspicious": True
                },
                "retention_days": "permanent"
            }
        )
        
        print(f"Created compliance event: {response.status_code}")
        return response.json()


async def example_get_compliance_events():
    """
    Example: Query compliance events for review.
    """
    async with httpx.AsyncClient() as client:
        # Get all critical security events in last 30 days
        response = await client.get(
            "http://localhost:8001/api/v1/compliance",
            params={
                "severity": "critical",
                "limit": 50
            }
        )
        
        events = response.json()
        
        print(f"\n🔴 Critical Compliance Events")
        print(f"Total: {events['total']}")
        
        for event in events['items']:
            print(f"\n  {event['created_at']}")
            print(f"  Event: {event['event_type']}")
            print(f"  Description: {event['description']}")
        
        return events


# ============================================================================
# 4. AUDIT TRAIL FOR TROUBLESHOOTING
# ============================================================================

async def example_investigate_issue_change():
    """
    Example: Investigate how an issue changed state.
    
    Scenario: Issue moved from closed back to open unexpectedly.
    Find out who did it and why.
    """
    issue_id = uuid4()
    
    async with httpx.AsyncClient() as client:
        # Get full change history for the issue
        response = await client.get(
            f"http://localhost:8001/api/v1/resource/{issue_id}",
            params={"resource_type": "issue"}
        )
        
        history = response.json()
        
        print(f"\nInvestigating issue {issue_id}")
        
        # Find status changes
        status_changes = []
        for change in history['change_timeline']:
            if 'status' in (change.get('changes') or {}):
                status_changes.append(change)
        
        print(f"\nStatus changes ({len(status_changes)}):")
        for change in status_changes:
            print(f"\n  {change['timestamp']}")
            print(f"  Changed by: {change['actor_id']}")
            status_change = change['changes']['status']
            print(f"  {status_change['old']} → {status_change['new']}")
        
        return history


# ============================================================================
# MAIN - Run Examples
# ============================================================================

async def main():
    """Run all examples."""
    print("=" * 80)
    print("Audit Service - Real-World Usage Examples")
    print("=" * 80)
    
    try:
        # Examples can be run individually
        # Uncomment to test:
        
        # await example_log_user_creation()
        # await example_get_user_activity()
        # await example_get_resource_history()
        # await example_get_statistics_report()
        # await example_find_unauthorized_access()
        # await example_create_compliance_event()
        
        print("\n✅ See commented code for individual examples")
        print("\nExamples available:")
        print("  1. example_log_user_creation()")
        print("  2. example_log_project_permission_change()")
        print("  3. example_log_failed_action()")
        print("  4. example_get_user_activity()")
        print("  5. example_get_resource_history()")
        print("  6. example_list_audit_logs_with_filters()")
        print("  7. example_get_statistics_report()")
        print("  8. example_log_data_access()")
        print("  9. example_find_unauthorized_access()")
        print("  10. example_create_compliance_event()")
        print("  11. example_get_compliance_events()")
        print("  12. example_investigate_issue_change()")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the Audit Service is running on http://localhost:8001")


if __name__ == "__main__":
    asyncio.run(main())
