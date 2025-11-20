from django.db import models

class SliderImage(models.Model):
    title = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="home/sliders/")
    order = models.PositiveSmallIntegerField(default=0)
    active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-uploaded_at"]

    def __str__(self):
        return self.title or f"Slider {self.pk}"

class HomeVideo(models.Model):
    title = models.CharField(max_length=255, blank=True)
    video = models.FileField(upload_to="home/videos/")
    active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"HomeVideo {self.pk}"
