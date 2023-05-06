import django_filters
from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    category = django_filters.CharFilter('category__slug')
    genre = django_filters.CharFilter('genre__slug')
    name = django_filters.CharFilter('name')
    year = django_filters.NumberFilter('year')

    class Meta:
        model = Title
        fields = '__all__'
