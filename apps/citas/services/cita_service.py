import uuid
from datetime import datetime, timedelta
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models.cita import Cita, DetalleCita, EstadoCita
from apps.clientes.models.cliente import Cliente
from apps.servicios.models.servicio import Servicio
from apps.personal.models.empleado import Empleado
from common.utils.phone import normalizar_telefono

# Máquina de estados oficial de una Cita. Clave = estado origen,
# valor = conjunto de estados destino permitidos desde ese origen.
# FINALIZADA, CANCELADA y NO_ASISTIO son estados terminales (sin salida).
TRANSICIONES_PERMITIDAS = {
    EstadoCita.PENDIENTE: {EstadoCita.CONFIRMADA, EstadoCita.CANCELADA, EstadoCita.NO_ASISTIO},
    EstadoCita.CONFIRMADA: {EstadoCita.EN_PROCESO, EstadoCita.CANCELADA, EstadoCita.NO_ASISTIO},
    EstadoCita.EN_PROCESO: {EstadoCita.FINALIZADA, EstadoCita.CANCELADA},
    EstadoCita.FINALIZADA: set(),
    EstadoCita.CANCELADA: set(),
    EstadoCita.NO_ASISTIO: set(),
}


def _parse_hora(hora_str):
    """Acepta un time/datetime ya parseado, 'HH:MM' o 'HH:MM:SS'."""
    if hasattr(hora_str, "hour"):
        return hora_str
    formato = "%H:%M" if len(hora_str) == 5 else "%H:%M:%S"
    return datetime.strptime(hora_str, formato).time()


def _sumar_minutos(hora_inicio, minutos):
    dummy = datetime.combine(datetime.today(), hora_inicio)
    return (dummy + timedelta(minutes=minutos)).time()


def _generar_codigo_reserva():
    # Reintenta en el (muy improbable) caso de colisión, ya que el campo es único.
    for _ in range(5):
        codigo = uuid.uuid4().hex[:8].upper()
        if not Cita.objects.filter(codigo_reserva=codigo).exists():
            return codigo
    # Última red de seguridad si hubiera colisiones repetidas.
    return uuid.uuid4().hex.upper()


class CitaService:
    @staticmethod
    @transaction.atomic
    def crear_reserva_publica(data):
        nombres = data.get('nombres')
        apellidos = data.get('apellidos')
        telefono = normalizar_telefono(data.get('telefono'))
        email = data.get('email')
        fecha = data.get('fecha')
        hora_inicio_str = data.get('hora_inicio')
        especialista_id = data.get('especialista_id')
        servicios_ids = data.get('servicios', [])

        if not telefono:
            raise ValidationError("El teléfono es obligatorio.")

        # 1. Crear o actualizar cliente por teléfono (ya normalizado, así que
        #    "+51 999 999 999" y "999999999" se tratan como el mismo cliente).
        cliente, _ = Cliente.objects.update_or_create(
            telefono=telefono,
            defaults={
                'nombres': nombres,
                'apellidos': apellidos,
                'email': email
            }
        )

        # 2. Validar regla crítica: Un cliente solo puede tener UNA cita activa por día
        estados_activos = [EstadoCita.PENDIENTE, EstadoCita.CONFIRMADA, EstadoCita.EN_PROCESO]
        cita_activa_existente = Cita.objects.filter(
            cliente=cliente,
            fecha=fecha,
            estado__in=estados_activos
        ).exists()

        if cita_activa_existente:
            raise ValidationError("El cliente ya cuenta con una cita activa para esta fecha.")

        # 3. Validar Especialista y Servicios
        try:
            especialista = Empleado.objects.get(id=especialista_id, activo=True)
        except Empleado.DoesNotExist:
            raise ValidationError("El especialista seleccionado no existe o no está activo.")

        servicios = Servicio.objects.filter(id__in=servicios_ids, activo=True)
        if not servicios.exists():
            raise ValidationError("Debe seleccionar al menos un servicio válido.")

        # 4. Calcular duración total y hora fin
        duracion_total_minutos = sum(s.duracion_minutos for s in servicios)
        hora_inicio_dt = _parse_hora(hora_inicio_str)
        hora_fin_dt = _sumar_minutos(hora_inicio_dt, duracion_total_minutos)

        # 5. Validar que el especialista no tenga otra cita que se cruce en ese horario
        CitaService._validar_sin_cruce_horario(especialista, fecha, hora_inicio_dt, hora_fin_dt)

        # 6. Generar código de reserva único
        codigo_reserva = _generar_codigo_reserva()

        # 7. Crear la Cita
        cita = Cita.objects.create(
            cliente=cliente,
            especialista=especialista,
            fecha=fecha,
            hora_inicio=hora_inicio_dt,
            hora_fin=hora_fin_dt,
            estado=EstadoCita.PENDIENTE,
            codigo_reserva=codigo_reserva
        )

        # 8. Crear los detalles históricos (precio y duración fijos)
        for servicio in servicios:
            DetalleCita.objects.create(
                cita=cita,
                servicio=servicio,
                precio=servicio.precio,
                duracion_minutos=servicio.duracion_minutos
            )

        return cita

    @staticmethod
    def _validar_sin_cruce_horario(especialista, fecha, hora_inicio, hora_fin, excluir_cita_id=None):
        """Evita que un especialista quede con dos citas activas que se solapen el mismo día."""
        estados_activos = [EstadoCita.PENDIENTE, EstadoCita.CONFIRMADA, EstadoCita.EN_PROCESO]
        qs = Cita.objects.filter(
            especialista=especialista,
            fecha=fecha,
            estado__in=estados_activos,
        )
        if excluir_cita_id:
            qs = qs.exclude(id=excluir_cita_id)

        for cita in qs:
            se_cruza = hora_inicio < cita.hora_fin and hora_fin > cita.hora_inicio
            if se_cruza:
                raise ValidationError(
                    f"El especialista ya tiene una cita entre {cita.hora_inicio.strftime('%H:%M')} "
                    f"y {cita.hora_fin.strftime('%H:%M')} ese día."
                )

    @staticmethod
    @transaction.atomic
    def crear_cita_gestion(cliente, especialista, fecha, hora_inicio_str, servicios_ids, observaciones=None):
        """
        Creación de citas desde el panel interno (staff). A diferencia de la
        reserva pública, no aplica la regla de "una cita activa por día" del
        cliente (el staff puede necesitar agendar excepciones), pero sí:
        - calcula hora_fin y codigo_reserva automáticamente (antes faltaba
          por completo en este flujo, ver sección de "problemas" del doc),
        - valida que el especialista no tenga otra cita que se cruce.
        """
        servicios = Servicio.objects.filter(id__in=servicios_ids, activo=True)
        if not servicios.exists():
            raise ValidationError("Debe seleccionar al menos un servicio válido.")

        duracion_total_minutos = sum(s.duracion_minutos for s in servicios)
        hora_inicio_dt = _parse_hora(hora_inicio_str)
        hora_fin_dt = _sumar_minutos(hora_inicio_dt, duracion_total_minutos)

        CitaService._validar_sin_cruce_horario(especialista, fecha, hora_inicio_dt, hora_fin_dt)

        cita = Cita.objects.create(
            cliente=cliente,
            especialista=especialista,
            fecha=fecha,
            hora_inicio=hora_inicio_dt,
            hora_fin=hora_fin_dt,
            estado=EstadoCita.PENDIENTE,
            codigo_reserva=_generar_codigo_reserva(),
            observaciones=observaciones or None,
        )

        for servicio in servicios:
            DetalleCita.objects.create(
                cita=cita,
                servicio=servicio,
                precio=servicio.precio,
                duracion_minutos=servicio.duracion_minutos
            )

        return cita

    @staticmethod
    @transaction.atomic
    def cambiar_estado_cita(cita_id, nuevo_estado):
        try:
            cita = Cita.objects.select_for_update().get(id=cita_id)
        except Cita.DoesNotExist:
            raise ValidationError("La cita no existe.")

        estado_actual = cita.estado
        destinos_validos = TRANSICIONES_PERMITIDAS.get(estado_actual, set())
        if nuevo_estado not in destinos_validos:
            raise ValidationError(
                f"No se puede pasar una cita de '{cita.get_estado_display()}' a "
                f"'{EstadoCita(nuevo_estado).label}'."
            )

        cita.estado = nuevo_estado
        cita.save()
        return cita

    @staticmethod
    def confirmar_cita(cita_id):
        return CitaService.cambiar_estado_cita(cita_id, EstadoCita.CONFIRMADA)

    @staticmethod
    def cancelar_cita(cita_id):
        return CitaService.cambiar_estado_cita(cita_id, EstadoCita.CANCELADA)

    @staticmethod
    def marcar_no_asistio(cita_id):
        return CitaService.cambiar_estado_cita(cita_id, EstadoCita.NO_ASISTIO)

    @staticmethod
    @transaction.atomic
    def reprogramar_cita(cita_id, nueva_fecha, nueva_hora_inicio):
        cita = Cita.objects.select_for_update().get(id=cita_id)

        estados_no_reprogramables = {EstadoCita.FINALIZADA, EstadoCita.CANCELADA, EstadoCita.NO_ASISTIO}
        if cita.estado in estados_no_reprogramables:
            raise ValidationError(
                f"No se puede reprogramar una cita en estado '{cita.get_estado_display()}'."
            )

        duracion_total = sum(d.duracion_minutos for d in cita.detalles.all())
        hora_inicio_dt = _parse_hora(nueva_hora_inicio)
        hora_fin_dt = _sumar_minutos(hora_inicio_dt, duracion_total)

        CitaService._validar_sin_cruce_horario(
            cita.especialista, nueva_fecha, hora_inicio_dt, hora_fin_dt, excluir_cita_id=cita.id
        )

        cita.fecha = nueva_fecha
        cita.hora_inicio = hora_inicio_dt
        cita.hora_fin = hora_fin_dt
        cita.save()
        return cita

    @staticmethod
    def iniciar_cita(cita_id):
        return CitaService.cambiar_estado_cita(cita_id, EstadoCita.EN_PROCESO)

    @staticmethod
    def finalizar_cita(cita_id):
        return CitaService.cambiar_estado_cita(cita_id, EstadoCita.FINALIZADA)
