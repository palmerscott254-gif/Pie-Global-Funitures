from django.db import models
from django.core.validators import MinLengthValidator


class UserMessage(models.Model):
    """Customer contact form messages.
    
    Tracks customer inquiries with status workflow:
    new -> read -> replied -> resolved
    Supports optional replies from admin and timestamped tracking.
    """
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('resolved', 'Resolved'),
    ]
    
    # Customer Info
    name = models.CharField(max_length=200, validators=[MinLengthValidator(2)])
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Message Content
    message = models.TextField(validators=[MinLengthValidator(5)])
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        db_index=True,
    )
    
    # Admin Reply
    reply_text = models.TextField(blank=True, null=True, validators=[MinLengthValidator(5)])
    replied_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = 'Customer Message'
        verbose_name_plural = 'Customer Messages'
        indexes = [
            models.Index(fields=['status', '-created_at'], name='msg_status_created_idx'),
            models.Index(fields=['email', '-created_at'], name='msg_email_created_idx'),
        ]

    def __str__(self):
        return f"Message from {self.name} ({self.status}) - {self.created_at:%Y-%m-%d}"

    @property
    def is_replied(self) -> bool:
        """Check if message has been replied to."""
        return self.status == 'replied'

    @property
    def is_new(self) -> bool:
        """Check if message is new (unread)."""
        return self.status == 'new'

    @property
    def days_since_created(self) -> int:
        """Get days elapsed since message creation."""
        from django.utils import timezone
        return (timezone.now() - self.created_at).days
