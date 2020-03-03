from django.urls import path

from .views import CarrierDetailView, SearchView

urlpatterns = [
    path("", SearchView.as_view()),
    path("carriers/<int:pk>/", CarrierDetailView.as_view(), name="carrier_detail"),
]
