"""Structured logging and audit trail utilities."""
import logging
import json
import uuid
from typing import Any, Dict, Optional
from datetime import datetime
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class AuditLogger:
    """Structured audit logging for sensitive operations."""

    # Audit event types
    AUTH_LOGIN = "auth.login"
    AUTH_LOGIN_FAILED = "auth.login_failed"
    AUTH_REGISTER = "auth.register"
    AUTH_LOGOUT = "auth.logout"
    AUTH_REFRESH_TOKEN = "auth.refresh_token"

    MESSAGE_CREATED = "message.created"
    MESSAGE_REPLIED = "message.replied"
    MESSAGE_RESOLVED = "message.resolved"

    ORDER_CREATED = "order.created"
    ORDER_STATUS_CHANGED = "order.status_changed"
    ORDER_PAID = "order.paid"

    ADMIN_ACTION = "admin.action"
    ERROR_EVENT = "error.event"

    @staticmethod
    def log_event(
        event_type: str,
        user_id: str = None,
        ip_address: str = None,
        resource_id: str = None,
        resource_type: str = None,
        details: Dict[str, Any] = None,
        status: str = "success",
    ) -> str:
        """Log an audit event with structured data."""
        audit_id = str(uuid.uuid4())
        timestamp = timezone.now().isoformat()

        audit_entry = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "resource_id": resource_id,
            "resource_type": resource_type,
            "status": status,
            "details": details or {},
        }

        message = json.dumps(audit_entry)
        
        if status == "success":
            logger.info(message, extra={"audit": True})
        else:
            logger.warning(message, extra={"audit": True})

        return audit_id

    @staticmethod
    def log_auth_login(user_id: str, email: str, ip_address: str = None) -> str:
        """Log successful login."""
        return AuditLogger.log_event(
            AuditLogger.AUTH_LOGIN,
            user_id=user_id,
            ip_address=ip_address,
            details={"email": email},
            status="success",
        )

    @staticmethod
    def log_auth_failed(email: str, ip_address: str = None, reason: str = "invalid_credentials") -> str:
        """Log failed login attempt."""
        return AuditLogger.log_event(
            AuditLogger.AUTH_LOGIN_FAILED,
            ip_address=ip_address,
            details={"email": email, "reason": reason},
            status="failed",
        )

    @staticmethod
    def log_auth_register(user_id: str, email: str, ip_address: str = None) -> str:
        """Log user registration."""
        return AuditLogger.log_event(
            AuditLogger.AUTH_REGISTER,
            user_id=user_id,
            ip_address=ip_address,
            details={"email": email},
            status="success",
        )

    @staticmethod
    def log_message_created(message_id: str, email: str, ip_address: str = None) -> str:
        """Log message creation."""
        return AuditLogger.log_event(
            AuditLogger.MESSAGE_CREATED,
            ip_address=ip_address,
            resource_id=str(message_id),
            resource_type="message",
            details={"email": email},
            status="success",
        )

    @staticmethod
    def log_order_created(order_id: str, email: str, total: str, ip_address: str = None) -> str:
        """Log order creation."""
        return AuditLogger.log_event(
            AuditLogger.ORDER_CREATED,
            ip_address=ip_address,
            resource_id=str(order_id),
            resource_type="order",
            details={"email": email, "total": total},
            status="success",
        )

    @staticmethod
    def log_order_status_change(
        user_id: str, order_id: str, old_status: str, new_status: str
    ) -> str:
        """Log order status change."""
        return AuditLogger.log_event(
            AuditLogger.ORDER_STATUS_CHANGED,
            user_id=user_id,
            resource_id=str(order_id),
            resource_type="order",
            details={"old_status": old_status, "new_status": new_status},
            status="success",
        )


def extract_client_ip(request) -> Optional[str]:
    """Extract client IP from request, respecting proxies."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def get_request_id(request) -> str:
    """Get or generate request ID from headers."""
    request_id = request.META.get("HTTP_X_REQUEST_ID")
    if not request_id:
        request_id = str(uuid.uuid4())
    return request_id
