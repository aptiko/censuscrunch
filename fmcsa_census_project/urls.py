from django.urls import include, path

urlpatterns = [path("", include("fmcsa_census.urls"))]
