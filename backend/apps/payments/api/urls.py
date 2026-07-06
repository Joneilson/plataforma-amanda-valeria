from django.urls import path

from .views import (
    CheckoutPixView,
    MarkAsPaidView,
    MonthlyReportView,
    MyPaymentsView,
    PaymentAdminListView,
)

urlpatterns = [
    path("payments/checkout", CheckoutPixView.as_view()),
    path("payments/my", MyPaymentsView.as_view()),
    path("payments", PaymentAdminListView.as_view()),
    path("payments/<int:payment_id>/marcar-pago", MarkAsPaidView.as_view()),
    path("reports/monthly", MonthlyReportView.as_view()),
]
