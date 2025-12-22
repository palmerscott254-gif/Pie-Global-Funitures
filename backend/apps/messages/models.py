from django.db import models
from django.core.validators import EmailValidator

class UserMessage(models.Model):
    """Customer contact form messages."""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('resolved', 'Resolved'),
    ]
    
    # Customer Info
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Message Content
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Admin Reply
    reply_text = models.TextField(blank=True, null=True)
    replied_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['status', '-created_at'], name='user_messag_status_idx'),
        ]

    def __str__(self):
        return f"Message from {self.name} ({self.status}) - {self.created_at:%Y-%m-%d}"

    @property
    def is_replied(self):
        """Check if message has been replied to."""
        return self.status == 'replied'
