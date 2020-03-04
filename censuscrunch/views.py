from django.conf import settings
from django.db.models import F, Q
from django.db.models.functions import Concat
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from . import models


class SearchView(ListView):
    model = models.Carrier
    paginate_by = 100
    template_name = "censuscrunch/search/main.html"

    def get_queryset(self):
        if self.request.GET:
            queryset = super().get_queryset()
            queryset = self._filter_queryset(queryset)
            queryset = self._sort_queryset(queryset)
        else:
            queryset = self.model.objects.none()
        return queryset

    def _filter_queryset(self, queryset):
        queryset = self._filter_by_simple_search_term(queryset)
        queryset = self._filter_by_number_of_power_units(queryset)
        return queryset

    def _filter_by_simple_search_term(self, queryset):
        search_term = self.request.GET.get("q")
        if search_term:
            queryset = queryset.filter(
                Q(legal_name__icontains=search_term)
                | Q(dba_name__icontains=search_term)
            )
        return queryset

    def _filter_by_number_of_power_units(self, queryset):
        min_power_units = self.request.GET.get("min_number_of_power_units")
        max_power_units = self.request.GET.get("max_number_of_power_units")
        if min_power_units:
            queryset = queryset.filter(number_of_power_units__gte=min_power_units)
        if max_power_units:
            queryset = queryset.filter(number_of_power_units__lte=max_power_units)
        return queryset

    def _sort_queryset(self, queryset):
        sort_order = self._get_sort_order()
        if not sort_order:
            return queryset
        queryset = queryset.annotate(name=Concat(F("dba_name"), F("legal_name")))
        return queryset.order_by(*sort_order)

    def _get_sort_order(self):
        valid_fields = {
            "name",
            "physical_state",
            "number_of_power_units",
            "number_of_drivers",
        }
        sort_order = [
            x for x in self.request.GET.getlist("sort") if x.lstrip("-") in valid_fields
        ]
        return sort_order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["row_limit"] = settings.CENSUSCRUNCH_ROW_LIMIT
        context["searched"] = bool(self.request.GET)
        return context


class CarrierDetailView(DetailView):
    model = models.Carrier
    template_name_suffix = "_detail/main"
