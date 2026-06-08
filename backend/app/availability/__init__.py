"""
app/availability/__init__.py
Módulo de disponibilidad — integrado al flujo de nueva reunión.

REGLA CLAVE: No existe pantalla independiente de disponibilidad.
La disponibilidad se consulta dentro del flujo "Nueva reunión".

Responsabilidades:
- Calcular disponibilidad de participantes para una fecha/hora.
- Calcular disponibilidad de salas.
- Detectar conflictos:
  - disponible
  - ocupado (confirmado)
  - pendiente en otra reunión
  - conflicto parcial
  - fuera de horario laboral
  - día no laborable
  - sala ocupada

Fase de implementación: Fase 2
"""
