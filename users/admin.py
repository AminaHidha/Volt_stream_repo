from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "email",
        "full_name",
        "role",
        "is_verified",
        "owner_verification_status",
    )

    list_filter = (
        "role",
        "is_verified",
        "owner_verification_status",
    )

    search_fields = (
        "email",
        "full_name",
    )
