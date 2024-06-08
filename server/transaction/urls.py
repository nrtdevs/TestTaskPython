from django.urls import path
from transaction.views import paySubscription, listSubscriptions
from .payment_gateway_api import PaymentGatway, PlanGetView, PaymentSuccessView,PaymentFailView

app_name = "transaction"

urlpatterns = [
    path('pay', paySubscription),
    path('list', listSubscriptions),
    path('api/plan/checkout-session/', PaymentGatway.as_view(), name='api_checkout_session'),
    path('api/plan/stripe_product/', PlanGetView.as_view(), name='stripe-product'),
    path('api/plan/payment_success', PaymentSuccessView.as_view(), name='payment-suceess'),
    path('api/plan/payment_fail', PaymentFailView.as_view(), name='payment-fail'),
]
