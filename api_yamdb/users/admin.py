from django.contrib import admin

from .models import User


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'confirmation_code',
        'password',
    )
    search_fields = ('username',)
    list_filter = ('username',)
    empty_value_display = '-пусто-'
