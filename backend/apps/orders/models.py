from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Order(models.Model):
    """Customer order with JSON cart items.
    
    Tracks complete order lifecycle from pending to delivered.
    Stores snapshot of items, prices, and quantities at order time.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Customer info
    name = models.CharField(max_length=200)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=40)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Order data - JSON snapshot of cart at order time
    items = models.JSONField(
        help_text="Array of objects: [{product_id, name, price, qty, image}]"
    )
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        db_index=True,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
    )
    paid = models.BooleanField(default=False, db_index=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Tracking
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = 'Customer Order'
        verbose_name_plural = 'Customer Orders'
        indexes = [
            models.Index(fields=['email', '-created_at'], name='order_email_created_idx'),
            models.Index(fields=['status', 'paid'], name='order_status_paid_idx'),
            models.Index(fields=['-created_at'], name='order_created_idx'),
        ]

    def __str__(self):
        return f"Order #{self.pk} - {self.name} - ${self.total_amount}"

    @property
    def item_count(self) -> int:
        """Total number of items in order."""
        if not self.items:
            return 0
        return sum(item.get('qty', 0) for item in self.items)

    @property
    def is_pending(self) -> bool:
        """Check if order is pending."""
        return self.status == 'pending'

    @property
    def is_delivered(self) -> bool:
        """Check if order is delivered."""
        return self.status == 'delivered'

    @property
    def is_shipped(self) -> bool:
        """Check if order is shipped."""
        return self.status in {'shipped', 'out_for_delivery'}

    @property
    def is_in_transit(self) -> bool:
        """Check if order is out for delivery."""
        return self.status in {'shipped', 'out_for_delivery'}
