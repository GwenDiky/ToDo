import django_filters
from projects.models import Project


class ProjectFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name="tasks__user_id",
                                     lookup_expr="exact")

    class Meta:
        model = Project
        fields = ['user']
