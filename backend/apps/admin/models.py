from django.db import models
from django.contrib.contenttypes.models import ContentType
from apps.users.models import User


class AdminAuditLog(models.Model):
    """Audit trail for admin actions on orders and messages.
    
    Tracks who did what, when, and on which object.
    Supports reverting changes if needed in future.
    """
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('status_change', 'Status Changed'),
        ('marked_paid', 'Marked as Paid'),
        ('message_reply', 'Message Replied'),
        ('message_resolved', 'Message Resolved'),
    ]

    # Who did it
    admin_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_audit_logs',
        help_text="Admin user who performed the action"
    )

    # What object was affected
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    # What changed
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        db_index=True
    )
    
    # Store old and new values for auditing
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON of {field: {old: value, new: value}}"
    )

    # When
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # IP address for security
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Admin Audit Log'
        verbose_name_plural = 'Admin Audit Logs'
        indexes = [
            models.Index(fields=['admin_user', '-timestamp'], name='audit_user_time_idx'),
            models.Index(fields=['content_type', '-timestamp'], name='audit_type_time_idx'),
        ]

    def __str__(self):
        admin_name = getattr(self.admin_user, 'name', 'Unknown admin')
        return f"{self.action.title()} by {admin_name} on {self.content_type} at {self.timestamp}"
