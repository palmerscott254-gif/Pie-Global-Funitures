from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid


class User(models.Model):
    """Custom User model for authentication."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=255)  # Hashed password
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        """Hash and set the password."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check if the provided password matches the stored hash."""
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
        """Override save to ensure password is hashed."""
        # Only hash if password looks like plain text (doesn't start with algorithm prefix)
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)
        super().save(*args, **kwargs)
