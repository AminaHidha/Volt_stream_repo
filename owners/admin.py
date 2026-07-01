from django.contrib import admin

from .models import OwnerProfile


@admin.action(description="Approve Owner")
def approve_owner(modeladmin, request, queryset):

    for profile in queryset:

        profile.approval_status = "approved"
        profile.save()

        profile.user.owner_verification_status = "approved"
        profile.user.save()


@admin.action(description="Reject Owner")
def reject_owner(modeladmin, request, queryset):

    for profile in queryset:

        profile.approval_status = "rejected"
        profile.save()

        profile.user.owner_verification_status = "rejected"
        profile.user.save()


@admin.register(OwnerProfile)
class OwnerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "station_name",
        "user",
        "approval_status",
        "submitted_at",
    )

    search_fields = (
        "user__email",
        "business_name",
        "station_name",
    )

    list_filter = (
        "approval_status",
        "submitted_at",
    )

    actions = [
        approve_owner,
        reject_owner,
    ]
