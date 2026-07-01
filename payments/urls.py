from django.urls import path

from .views import (CreatePaymentView, PaymentDetailView, PaymentHistoryView,
                    VerifyPaymentView)

urlpatterns = [
    path("create/", CreatePaymentView.as_view()),
    path("verify/", VerifyPaymentView.as_view()),
    path("history/", PaymentHistoryView.as_view()),
    path("<int:payment_id>/", PaymentDetailView.as_view()),
]
