from django.db import migrations


def corregir_rol_superusuarios(apps, schema_editor):
    """
    `createsuperuser` no pregunta por 'rol' (no está en REQUIRED_FIELDS),
    así que cualquier superusuario creado antes de este arreglo quedó con
    el valor por defecto RECEPCIONISTA — bloqueado de facto de los
    endpoints restringidos a ADMINISTRADOR/GERENTE (p. ej.
    /gestion/usuarios/), aunque HasRole ahora además deja pasar a
    cualquier superusuario sin importar su 'rol' (ver
    common/permissions/base.py). Esta migración deja además el dato
    correcto en la base, por prolijidad y para que se vea bien en el
    panel de Usuarios.
    """
    Usuario = apps.get_model('usuarios', 'Usuario')
    Usuario.objects.filter(is_superuser=True).exclude(rol='ADMINISTRADOR').update(rol='ADMINISTRADOR')


def revertir(apps, schema_editor):
    # No hay una forma segura de saber cuál era el rol original antes de
    # esta migración, así que la reversión es un no-op intencional.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(corregir_rol_superusuarios, revertir),
    ]
