from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'full_name', 'is_active', 'is_staff')
    search_fields = ('email', 'full_name')
    ordering = ('email',)
