from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from decimal import Decimal


class Product(models.Model):
    """Furniture product with images and inventory."""
    
    CATEGORY_CHOICES = [
        ("sofa", "Sofa"),
        ("bed", "Bed"),
        ("table", "Table"),
        ("wardrobe", "Wardrobe"),
        ("office", "Office Furniture"),
        ("dining", "Dining"),
        ("outdoor", "Outdoor"),
        ("storage", "Storage"),
        ("other", "Other"),
    ]

    # Basic info
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    
    # Pricing
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    compare_at_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Original price for showing discounts"
    )
    
    # Categorization
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="other", db_index=True)
    tags = models.JSONField(
        blank=True, 
        null=True, 
        help_text="Array of tags for filtering"
    )
    
    # Media
    main_image = models.ImageField(upload_to="products/main/", blank=True)
    gallery = models.JSONField(
        blank=True, 
        null=True, 
        help_text="Array of additional image URLs or paths"
    )
    
    # Inventory
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    # Specifications
    dimensions = models.CharField(max_length=200, blank=True, help_text="e.g., '200x100x80 cm'")
    material = models.CharField(max_length=200, blank=True)
    color = models.CharField(max_length=100, blank=True)
    weight = models.CharField(max_length=50, blank=True)
    
    # Flags
    featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    on_sale = models.BooleanField(default=False)
    
    # SEO
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['featured', '-created_at']),
            models.Index(fields=['is_active', '-created_at']),
        ]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided."""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    @property
    def in_stock(self):
        """Check if product is available."""
        return self.stock > 0
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare_at_price is set."""
        if self.compare_at_price and self.compare_at_price > self.price:
            return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0
