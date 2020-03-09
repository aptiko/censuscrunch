from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def urlparams_set_page(context, page):
    query = context["request"].GET.copy()
    query.pop("page", None)
    query.update({"page": page})
    return query.urlencode()
