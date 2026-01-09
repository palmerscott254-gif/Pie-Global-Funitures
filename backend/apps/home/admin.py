from django.contrib import admin
from django import forms
from django.db.models import Max
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow multi-upload without requiring the base image field
        if 'image' in self.fields:
            self.fields['image'].required = False

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
        # Compute next order starting at 1
        start_order = (SliderImage.objects.aggregate(max_order=Max('order'))['max_order'] or 0) + 1

        # If the main object lacks an explicit order, assign the next slot
        if not obj.order:
            obj.order = start_order

        if 'images' in request.FILES:
            files = request.FILES.getlist('images')
            for idx, file in enumerate(files):
                SliderImage.objects.create(
                    title=obj.title,
                    image=file,
                    order=start_order + idx,
                    active=obj.active
                )
            # All created; skip saving the base object
            return

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
