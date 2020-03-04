from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag(takes_context=True)
def sorter(context, column_name, label):
    """Return a label with a sorting indicator that can be used for sorting.

    {% sorter column_name label %}

    This tag returns "label", possibly followed by a downward or an upward
    arrow that indicates the current sorting method, all that enclosed in a
    href hyperlink that would cause the sorting order to be changed so that it
    goes primarily by the specified column.  If the first column of the current
    sort_order is the same as "column_name", the tag adds a downward or upward
    arrow (depending on whether the sorting is direct or reverse), otherwise it
    adds a double up/down arrow.
    """
    sorting_tag = SortingTag(context, column_name, label)
    return sorting_tag.render()


class SortingTag:
    def __init__(self, context, column_name, label):
        self.request = context["request"]
        self.column_name = column_name
        self.label = label

    def render(self):
        self._determine_indicator_and_sign()
        self._determine_target_url()
        return format_html(
            f'<a href="{self.target_url}">{self.label}&nbsp;{self.indicator}</a>'
        )

    def _determine_indicator_and_sign(self):
        if self.sort_order and (self.sort_order[0] == self.column_name):
            self.indicator = "⇓"
            self.sign = "-"
        elif self.sort_order and (self.sort_order[0] == "-" + self.column_name):
            self.indicator = "⇑"
            self.sign = ""
        else:
            self.indicator = "⇕"
            self.sign = ""

    def _determine_target_url(self):
        new_sort_order = self._get_new_sort_order()
        self.target_url = self.request.path
        new_query_dict = self.request.GET.copy()
        if "sort" in new_query_dict:
            new_query_dict.pop("sort")
        new_query_dict.setlist("sort", new_sort_order)
        self.target_url += f"?{new_query_dict.urlencode()}"

    @property
    def sort_order(self):
        if not hasattr(self, "_cached_sort_order"):
            self._cached_sort_order = self._get_sort_order()
        return self._cached_sort_order

    def _get_sort_order(self):
        sort_order = self.request.GET.getlist("sort")
        return self._remove_duplicates_from_sort_order(sort_order)

    def _get_new_sort_order(self):
        result = self.sort_order
        result.insert(0, f"{self.sign}{self.column_name}")
        result = self._remove_duplicates_from_sort_order(result)
        return result

    def _remove_duplicates_from_sort_order(self, sort_order):
        result = []
        fields_seen = []
        for item in sort_order:
            field = item
            if field.startswith("-"):
                field = item[1:]
            if field in fields_seen:
                continue
            result.append(item)
            fields_seen.append(field)
        return result
