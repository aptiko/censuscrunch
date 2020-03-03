from django.conf import settings
from django.db.models import Q
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from . import models


class SearchView(ListView):
    model = models.Carrier
    paginate_by = 100
    template_name = "censuscrunch/search/main.html"

    def get_queryset(self):
        if self.request.GET:
            qs = super().get_queryset()
            qs = self._filter_queryset(qs)
        else:
            qs = self.model.objects.none()
        return qs

    def _filter_queryset(self, qs):
        qs = self._filter_by_simple_search_term(qs)
        qs = self._filter_by_number_of_power_units(qs)
        return qs

    def _filter_by_simple_search_term(self, qs):
        search_term = self.request.GET.get("q")
        if search_term:
            qs = qs.filter(
                Q(legal_name__icontains=search_term)
                | Q(dba_name__icontains=search_term)
            )
        return qs

    def _filter_by_number_of_power_units(self, qs):
        min_power_units = self.request.GET.get("min_number_of_power_units")
        max_power_units = self.request.GET.get("max_number_of_power_units")
        if min_power_units:
            qs = qs.filter(number_of_power_units__gte=min_power_units)
        if max_power_units:
            qs = qs.filter(number_of_power_units__lte=max_power_units)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["row_limit"] = settings.CENSUSCRUNCH_ROW_LIMIT
        context["searched"] = bool(self.request.GET)
        return context


class CarrierDetailView(DetailView):
    model = models.Carrier
    template_name_suffix = "_detail/main"
