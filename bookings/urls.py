from django.urls import path

from .views import (
    BookingCreateView,
    MyBookingsView,
    BookingDetailView,
    CancelBookingView,
)

urlpatterns = [

    path(
        "create/",
        BookingCreateView.as_view()
    ),

    path(
        "my/",
        MyBookingsView.as_view()
    ),

    path(
        "<int:booking_id>/",
        BookingDetailView.as_view()
    ),

    path(
        "<int:booking_id>/cancel/",
        CancelBookingView.as_view()
    ),
]