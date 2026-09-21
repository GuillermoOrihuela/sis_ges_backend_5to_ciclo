from apps.auditoria.models import RegistroAuditoria

def registrar_auditoria(accion, modulo, descripcion, usuario=None, ip_origen=None):
    """
    Registra una acción crítica en el sistema según el Contrato Técnico.
    Acciones obligatorias de auditar: Cancelación de citas, anulación de ventas, 
    movimientos manuales de inventario, cambios de comisiones, pagos de comisiones, 
    cambios de permisos y modificación de horarios.
    """
    return RegistroAuditoria.objects.create(
        usuario=usuario,
        accion=accion,
        modulo=modulo,
        descripcion=descripcion,
        ip_origen=ip_origen
    )