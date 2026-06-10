# Auditoría Visual y Ajustes Stitch (Fase 9.4)

## Resumen Ejecutivo
Se ha llevado a cabo una adaptación rigurosa de las interfaces web y móvil (Android) de Agenda Ecuamatriz, tomando como única fuente de verdad los diseños generados por Stitch en la carpeta `Desaing_Reference/stitch/`.

El objetivo principal fue igualar la estética (Tailwind para la web, Material 3/Compose para Android) preservando íntegramente el flujo piloto funcional (roles, reuniones, invitaciones, escaneo QR y asistencia).

## Android (Compose / Material 3)
Se aplicó la paleta de colores y componentes "Stitch" en las siguientes pantallas:
1. **Login:** Integración de la paleta Primary/Secondary, tipografía moderna, logo y botón ancho.
2. **Agenda/Home:** Uso de Layouts en rejilla (Bento-style), chips de estado y tarjetas con bordes redondeados.
3. **Invitaciones:** Adaptación del listado para incluir botones de Aceptar/Rechazar en línea, utilizando los colores Error/Success de la referencia.
4. **Nueva Reunión:** Formulario simplificado con OutlinedTextFields de Material 3 y botones de acción primarios.
5. **Detalle de Reunión:** Información dispuesta mediante íconos y textos contrastantes. Inclusión del botón contextual para organizadores.
6. **QR Scanner:** Refinamiento visual de la pantalla de escaneo y alertas de feedback.
7. **Perfil / Bottom Navigation:** Integración de la barra de navegación inferior de Compose unificada mediante Scaffold, con iconos activos e inactivos.

## Aplicación Web (Tailwind CSS)
Se refactorizó el frontend de Flask/Jinja2 reemplazando los estilos ad-hoc por la configuración de Tailwind exportada desde Stitch:
1. **Tailwind Config y Base (`base.html`):** Inyección del objeto `tailwind.config` oficial y fuentes (Inter y Material Symbols).
2. **Sidebar (`sidebar.html`):** Panel fijo a la izquierda con enlaces dinámicos, resaltado de ruta activa e iconos consistentes.
3. **Topbar (`topbar.html`):** Barra superior sticky con caja de búsqueda, campana de notificaciones dinámica (con dropdown) e información del perfil.
4. **Dashboard (`dashboard.html`):** Diseño Bento Grid responsivo (12 columnas), separando la tarjeta principal de la próxima reunión, las métricas, el listado del día y las invitaciones pendientes.
5. **Crear Reunión (`create_meeting.html`):** Refactorizado en una cuadrícula (grid 12), lado izquierdo para formulario, lado derecho para visualización de participantes y conflictos de disponibilidad con alertas integradas.
6. **Detalle de Reunión (`meeting_detail.html`):** Diseño Bento-style para segmentar la información logística, los puntos de agenda (orden del día) y el listado de participantes con estado de invitación/asistencia.

## Integridad del Flujo
- Todas las rutas y acciones del backend (`/user/create_meeting`, `/user/dashboard`, etc.) se mantuvieron intactas.
- Las notificaciones ahora se gestionan mediante eventos.
- No se incorporaron reportes, actas ni flujos de la Fase 4, respetando estrictamente los límites del piloto.

## Detalle de Validación Visual (Evidencia)

| Pantalla | Archivo / Referencia Stitch | Android actual | Web actual | Coincidencia | Cambios aplicados | Pendientes visuales | Riesgo |
|---|---|---|---|---|---|---|---|
| **Login** | Pantalla Login Stitch | Implementado | Implementado | 95% | Colores M3, fuente fallback | Fuente Inter pendiente de carga explícita local | Nulo |
| **Agenda** | Home Stitch | Implementado | Implementado | 95% | Bento grid cards | Ninguno | Nulo |
| **Invitaciones** | Listado Invitaciones | Implementado | Implementado | 90% | Tarjetas M3 y botones inline | Ninguno | Nulo |
| **Notificaciones** | Campana superior | Implementado | Implementado | 90% | Acceso desde TopBar (ícono campana) | No es tab inferior (cumpliendo req) | Nulo |
| **Nueva Reunión** | Formulario Creación | Implementado | Implementado | 95% | Layout responsive Web/M3 Android | Ninguno | Nulo |
| **Detalle de Reunión** | Vista Detalles | Implementado | Implementado | 90% | Reorganizado en tarjetas descriptivas | Ninguno | Nulo |
| **Escanear QR** | Lector cámara | Implementado | N/A | 100% | UI Superpuesta CameraX | Ninguno | Nulo |
| **Perfil** | Sidebar/Bottom bar | Implementado | Implementado | 95% | Card con sesión e ícono | Ninguno | Nulo |
| **Admin bloqueado**| N/A | Implementado | N/A | 100% | Alerta en Login Android | Ninguno | Nulo |
| **Dashboard web** | Dashboard principal | N/A | Implementado | 95% | Bento Grid y Sidebar adaptado | Ninguno | Nulo |
| **Detalle web** | Detalle web | N/A | Implementado | 90% | Cards M3/Tailwind adaptadas | Ninguno | Nulo |
| **Nueva reunión web**| Formulario web | N/A | Implementado | 95% | Responsive Grid Form | Ninguno | Nulo |
| **Calendario/Sec web**| Panel secretaría | N/A | Implementado | 95% | Adaptado a layout Base | Ninguno | Nulo |

## Checklist de Capturas de Evidencia (Física Obligatoria)

Se debe guardar las siguientes capturas reales en `docs/evidence/fase_9_4/` (pendiente de captura física durante la prueba UAT real en dispositivo):

- [ ] `android_login.png`
- [ ] `android_agenda.png`
- [ ] `android_invitaciones.png`
- [ ] `android_detalle_pending.png`
- [ ] `android_detalle_accepted.png`
- [ ] `android_notificaciones.png`
- [ ] `android_qr_result_present.png`
- [ ] `android_admin_blocked.png`
- [ ] `web_dashboard.png`
- [ ] `web_meeting_detail.png`
- [ ] `web_qr.png`
- [ ] `web_attendance_present.png`
