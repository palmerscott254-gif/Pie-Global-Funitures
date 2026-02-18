from django.db import models

class AboutPage(models.Model):
    headline = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return "About Page"
