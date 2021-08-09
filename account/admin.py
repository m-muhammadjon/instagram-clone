from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfielAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'gender', 'joined']
    list_filter = ['joined']
    ordering = ['-joined']
