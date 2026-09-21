from django.db import migrations


def crear_almacen_por_defecto(apps, schema_editor):
    """
    VentaService.confirmar_venta/anular_venta necesitan un Almacen para
    descontar/devolver stock. Antes de este arreglo, si la base de datos
    estaba recién migrada y nadie había creado un Almacen todavía,
    confirmar la primera venta fallaba (FK inexistente). Esta migración de
    datos asegura que exista al menos uno, sin pisar nada si el equipo ya
    creó sus propios almacenes.
    """
    Almacen = apps.get_model('inventario', 'Almacen')
    if not Almacen.objects.exists():
        Almacen.objects.create(
            nombre='Almacén Principal',
            ubicacion='Sede principal',
            activo=True,
        )


def eliminar_almacen_por_defecto(apps, schema_editor):
    # Reversión segura: sólo borra el que esta migración pudo haber creado,
    # y sólo si sigue sin tener movimientos/existencias asociadas.
    Almacen = apps.get_model('inventario', 'Almacen')
    Almacen.objects.filter(
        nombre='Almacén Principal',
        movimientos__isnull=True,
        existencias__isnull=True,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_almacen_por_defecto, eliminar_almacen_por_defecto),
    ]
