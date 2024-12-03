from django.urls import path
from .views import optimize_fuel

urlpatterns = [
    path('optimized-fuel-stops/', optimize_fuel, name='optimize-fuel')
]