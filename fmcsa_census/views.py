from django.views.generic.list import ListView

from . import models


class SearchView(ListView):
    model = models.Carrier
    paginate_by = 100
    template_name = "fmcsa_census/search/main.html"
