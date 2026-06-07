from django.contrib import admin

from .models import User, Skill


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "surname", "is_staff", "is_active")
    search_fields = ("email", "name", "surname")
    list_filter = ("is_staff", "is_active")


admin.site.register(Skill)
