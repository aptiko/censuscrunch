import csv
import datetime as dt
from io import StringIO

from django.conf import settings
from django.db.models import F, Q
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from . import models


class SearchView(ListView):
    model = models.Carrier
    paginate_by = 100
    template_name = "censuscrunch/search/main.html"

    def get(self, *args, **kwargs):
        if self.request.GET.get("format") == "csv":
            return self.get_csv(*args, **kwargs)
        else:
            return super().get(*args, **kwargs)

    def get_queryset(self):
        if self.request.GET:
            queryset = super().get_queryset()
            queryset = self._filter_queryset(queryset)
            queryset = self._sort_queryset(queryset)
        else:
            queryset = self.model.objects.none()
        return queryset

    def _filter_queryset(self, queryset):
        queryset = self._filter_by_state(queryset)
        queryset = self._filter_by_number_of_power_units(queryset)
        queryset = self._filter_by_simple_search_term(queryset)
        return queryset

    def _filter_by_simple_search_term(self, queryset):
        search_term = self.request.GET.get("q")
        if search_term:
            queryset = queryset.filter(
                Q(legal_name__icontains=search_term)
                | Q(dba_name__icontains=search_term)
            )
        return queryset

    def _filter_by_state(self, queryset):
        state = self.request.GET.get("state", "").strip()
        if state:
            queryset = queryset.filter(physical_state__iexact=state)
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
        context["states"] = models.STATES
        return context

    def get_csv(self, *args, **kwargs):
        return CsvResponse(self.get_queryset())


class CsvResponse(HttpResponse):
    def __init__(self, queryset):
        self.queryset = queryset
        if self.queryset.count() > settings.CENSUSCRUNCH_ROW_LIMIT:
            super().__init__(status=400, reason="Too many rows")
        else:
            response_content = self._create_csv().encode("us-ascii")
            super().__init__(response_content, content_type="text/csv")
            self["Content-Disposition"] = 'attachment; filename="fmcsacensuscrunch.csv"'

    def _create_csv(self):
        self.csv = StringIO()
        self.csvwriter = csv.writer(self.csv)
        self._add_csv_header()
        self._add_csv_body()
        return self.csv.getvalue()

    def _add_csv_header(self):
        row = (
            "DOT_NUMBER,LEGAL_NAME,DBA_NAME,CARRIER_OPERATION,HM_FLAG,PC_FLAG,"
            "PHY_STREET,PHY_CITY,PHY_STATE,PHY_ZIP,PHY_COUNTRY,MAILING_STREET,"
            "MAILING_CITY,MAILING_STATE,MAILING_ZIP,MAILING_COUNTRY,TELEPHONE,FAX,"
            "EMAIL_ADDRESS,MCS150_DATE,MCS150_MILEAGE,MCS150_MILEAGE_YEAR,ADD_DATE,"
            "OIC_STATE,NBR_POWER_UNIT,DRIVER_TOTAL"
        ).split(",")
        self.csvwriter.writerow(row)

    def _add_csv_body(self):
        for carrier in self.queryset:
            self._add_csv_body_row(carrier)

    def _add_csv_body_row(self, carrier):
        attrs = (
            "dot_number,legal_name,dba_name,carrier_operation,hm,pc,"
            "physical_address,physical_city,physical_state,physical_zip,"
            "physical_country,mailing_address,mailing_city,mailing_state,"
            "mailing_zip,mailing_country,tel,fax,email,mcs150_date,mcs150_mileage,"
            "mcs150_mileage_year,date_added_mcmis,oic_state,number_of_power_units,"
            "number_of_drivers"
        ).split(",")
        values = [getattr(carrier, attr) for attr in attrs]
        values = [self._format(v) for v in values]
        self.csvwriter.writerow(values)

    def _format(self, value):
        if value is True or value is False:
            return "NY"[value]
        elif isinstance(value, dt.date):
            return value.strftime("%d-%b-%y").upper()
        else:
            return value


class CarrierDetailView(DetailView):
    model = models.Carrier
    template_name_suffix = "_detail/main"
