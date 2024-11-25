import django_filters

from tasks.models import Task


class FilterTasks(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.ChoiceFilter(
        choices=Task.STATUS_CHOICES, lookup_expr="exact"
    )

    class Meta:
        model = Task
        fields = ["title", "status"]
