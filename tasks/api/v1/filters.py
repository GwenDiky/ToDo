import django_filters

from tasks.enums import StatusChoices
from tasks.models import Task


class FilterTasks(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.ChoiceFilter(choices=StatusChoices)

    class Meta:
        model = Task
        fields = ["title", "status"]
