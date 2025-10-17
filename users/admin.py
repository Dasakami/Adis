from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PhoneVerificationCode

class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'phone_number', 'first_name', 'last_name', 'role', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'role')
    search_fields = ('email', 'phone_number', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

    fieldsets = (
        (None, {'fields': ('email', 'phone_number', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'role')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(PhoneVerificationCode)
