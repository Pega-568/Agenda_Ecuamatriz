"""
app/technical_sheets/__init__.py
Módulo de fichas técnicas / actas de reunión.

Primera versión: Ficha manual/asistida.

Datos autocargados desde la reunión:
- Título, objetivo, fecha, hora, sala, creador.
- Lista de invitados.
- Asistentes (marcados por QR).
- Ausentes.
- Orden del día.

Campos editables por el creador/coordinador:
- temas_tratados: Temas efectivamente discutidos.
- resumen_ejecutivo: Síntesis de la reunión.
- acuerdos: Compromisos acordados.
- compromisos: Responsables y fechas.
- observaciones: Notas adicionales.

Estados de la ficha:
- draft: En edición.
- finalized: Finalizada y cerrada.

Versión futura (Fase 8):
- Integración con grabación/transcripción.
- Borrador generado desde transcripción (requiere revisión humana).

Entidad: TechnicalSheet
Fase de implementación: Fase 5
"""
