from django.contrib import admin
from django import forms
from .models import SliderImage, HomeVideo

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class SliderImageAdminForm(forms.ModelForm):
    images = MultipleFileField(label='Select images', required=False)

    class Meta:
        model = SliderImage
        fields = '__all__'

@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    """Admin interface for homepage slider images."""
    form = SliderImageAdminForm
    
    list_display = ("id", "title", "order", "active", "uploaded_at")
    list_editable = ("order", "active")
    list_filter = ("active", "uploaded_at")
    search_fields = ("title",)
    ordering = ("order", "-uploaded_at")

    def save_model(self, request, obj, form, change):
        if 'images' in request.FILES:
            files = request.FILES.getlist('images')
            for file in files:
                SliderImage.objects.create(
                    title=obj.title,
                    image=file,
                    order=obj.order,
                    active=obj.active
                )
        else:
            super().save_model(request, obj, form, change)

@admin.register(HomeVideo)
class HomeVideoAdmin(admin.ModelAdmin):
    """Admin interface for homepage videos."""
    
    list_display = ("id", "title", "active", "uploaded_at")
    list_editable = ("active",)
    list_filter = ("active", "uploaded_at")
    search_fields = ("title",)
    date_hierarchy = "uploaded_at"
    ordering = ("-uploaded_at",)
