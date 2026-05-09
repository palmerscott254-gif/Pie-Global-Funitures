from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid


class User(models.Model):
    """Custom User model for authentication.
    
    UUID primary key for distributed systems.
    Email-based authentication with secure password hashing.
    Timestamps for audit purposes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False, db_index=False)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=255)  # Hashed password (PBKDF2)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        verbose_name = 'Frontend User Account'
        verbose_name_plural = 'Frontend User Accounts'
        indexes = [
            models.Index(fields=['email', 'is_active'], name='user_email_active_idx'),
            models.Index(fields=['-created_at'], name='user_created_idx'),
        ]

    def __str__(self):
        return f"{self.name} <{self.email}>"

    def set_password(self, raw_password: str) -> None:
        """Hash and set the password.
        
        Args:
            raw_password: Plain text password to hash
        """
        if not raw_password:
            raise ValueError("Password cannot be empty.")
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Check if the provided password matches the stored hash.
        
        Args:
            raw_password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        return check_password(raw_password, self.password)

    @property
    def is_authenticated(self):
        """Compatibility with Django auth checks used by DRF throttling."""
        return True

    @property
    def is_anonymous(self):
        """Compatibility with Django auth checks for anonymous users."""
        return False

    @property
    def is_staff(self):
        """Compatibility with admin/staff checks in views."""
        return False

    @property
    def is_superuser(self):
        """Compatibility with superuser checks in views."""
        return False

    def save(self, *args, **kwargs):
        """Override save to ensure password is hashed before storage.
        
        Only hashes if password looks like plain text (doesn't already have algorithm prefix).
        """
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)
        super().save(*args, **kwargs)
