from django.contrib import admin
from .models import User, Flag


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_guest', 'score', 'created_at')
    list_filter = ('is_guest',)
    search_fields = ('username', 'email')


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('flag_id', 'country_name', 'country_code', 'continent')
    search_fields = ('country_name',)
