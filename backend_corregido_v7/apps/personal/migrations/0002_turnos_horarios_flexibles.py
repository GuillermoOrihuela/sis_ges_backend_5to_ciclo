from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personal', '0001_initial'),
    ]

    operations = [
        # 'nombre' de Turno ya no está limitado a 3 valores fijos ni es
        # único: cada negocio puede crear los turnos que necesite (Mañana,
        # Tarde, Noche, Fin de semana, turnos a medida por empleado, etc.).
        migrations.AlterField(
            model_name='turno',
            name='nombre',
            field=models.CharField(max_length=50),
        ),
        # Antes un empleado sólo podía tener UN horario por día de la
        # semana. Se quita esa restricción para permitir turnos partidos
        # (mañana + tarde) y horarios variados; la validación de que los
        # rangos de hora no se superpongan pasa a hacerse en el serializer.
        migrations.AlterUniqueTogether(
            name='horarioempleado',
            unique_together=set(),
        ),
    ]
