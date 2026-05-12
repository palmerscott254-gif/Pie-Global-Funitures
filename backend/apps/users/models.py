from django.db import models
from django.contrib.auth.hashers import make_password, check_password, identify_hasher
from django.contrib.auth.base_user import BaseUserManager
import uuid


class UserManager(BaseUserManager):
    """Custom manager for email-based user lookup/authentication."""

    use_in_migrations = True

    def get_by_natural_key(self, username):
        return self.get(**{self.model.USERNAME_FIELD: username})

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.password = make_password(None)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(models.Model):
    """Custom User model for authentication.
    
    UUID primary key for distributed systems.
    Email-based authentication with secure password hashing.
    Timestamps for audit purposes.
    """
    # Django AUTH_USER_MODEL required attributes
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False, db_index=False)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=255)  # Hashed password (PBKDF2)
    is_active = models.BooleanField(default=True, db_index=True)
    is_staff = models.BooleanField(default=False, db_index=True, help_text="Designates whether user is staff (can access admin)")
    is_superuser = models.BooleanField(default=False, db_index=True, help_text="Designates whether user is superuser (full admin)")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Role-based access for admin dashboard and responsibilities.
    # Values: super_admin, staff_admin, support_agent, delivery_manager, customer
    ROLE_SUPER = 'super_admin'
    ROLE_STAFF = 'staff_admin'
    ROLE_SUPPORT = 'support_agent'
    ROLE_DELIVERY = 'delivery_manager'
    ROLE_CUSTOMER = 'customer'

    ROLE_CHOICES = [
        (ROLE_SUPER, 'Super Admin'),
        (ROLE_STAFF, 'Staff Admin'),
        (ROLE_SUPPORT, 'Support Agent'),
        (ROLE_DELIVERY, 'Delivery Manager'),
        (ROLE_CUSTOMER, 'Customer'),
    ]

    role = models.CharField(
        max_length=32,
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER,
        help_text='Primary role for admin dashboard access and permissions',
        db_index=True,
    )

    objects = UserManager()

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

    def save(self, *args, **kwargs):
        """Override save to ensure password is hashed before storage.
        
        Only hashes if password looks like plain text (doesn't already have algorithm prefix).
        """
        if self.password:
            try:
                identify_hasher(self.password)
            except Exception:
                self.set_password(self.password)
        super().save(*args, **kwargs)

    # Django admin/auth compatibility helpers
    def has_perm(self, perm, obj=None):
        """Return True if the user has a specific permission.

        Simplified: treat staff and superusers as having all perms in admin.
        """
        return bool(self.is_active and (self.is_superuser or self.is_staff))

    def has_module_perms(self, app_label):
        """Return True if the user has permissions to view the app `app_label`.

        Simplified: staff and superusers may view admin app modules.
        """
        return bool(self.is_active and (self.is_superuser or self.is_staff))

    def get_full_name(self):
        return self.name or self.email

    def get_short_name(self):
        return (self.name.split()[0] if self.name and self.name.strip() else self.email)
