"""
app/audit/__init__.py
Módulo de auditoría del sistema.

Responsabilidades:
- Registrar toda acción importante del sistema.
- Consultar logs de auditoría (solo Admin/Secretaría).

Entidad: AuditLog

Campos registrados por acción:
- actor_user_id: Quién ejecutó la acción.
- action: Nombre de la acción (ej: "meeting.create", "user.deactivate").
- entity_type: Tipo de entidad afectada (ej: "Meeting", "User").
- entity_id: ID del recurso afectado.
- metadata: JSON con detalles adicionales del contexto.
- created_at: Timestamp de la acción.

Acciones auditables mínimas:
- Creación, modificación, cancelación de reuniones.
- Aceptación/rechazo de invitaciones.
- Marcado de asistencia.
- Creación/edición de usuarios.
- Cambios en configuración del sistema.
- Generación de reportes.
- Finalización de fichas técnicas.

Fase de implementación: Fase 1 (estructura), integrado desde Fase 2
"""
