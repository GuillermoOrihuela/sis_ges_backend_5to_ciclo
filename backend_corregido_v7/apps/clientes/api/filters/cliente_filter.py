import django_filters
from ...models.cliente import Cliente

class ClienteFilter(django_filters.FilterSet):
    telefono = django_filters.CharFilter(lookup_expr='icontains')
    nombres = django_filters.CharFilter(lookup_expr='icontains')
    apellidos = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Cliente
        fields = ['telefono', 'nombres', 'apellidos', 'activo']