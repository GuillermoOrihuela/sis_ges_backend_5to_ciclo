import django_filters
from ...models.cita import Cita

class CitaFilter(django_filters.FilterSet):
    fecha = django_filters.DateFilter()
    especialista = django_filters.NumberFilter()
    estado = django_filters.CharFilter(lookup_expr='iexact')
    cliente = django_filters.NumberFilter()

    class Meta:
        model = Cita
        fields = ['fecha', 'especialista', 'estado', 'cliente']