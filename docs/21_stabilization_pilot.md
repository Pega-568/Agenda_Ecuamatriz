# 21 — Estabilización y Piloto (Fase 9)

## Objetivo
Este documento sirve como certificación de que el sistema Agenda Ecuamatriz ha superado las validaciones integrales de la Fase 9 y se encuentra listo para iniciar pruebas piloto con usuarios reales en un entorno controlado.

## Resumen de Validaciones de Backend
Durante esta fase se certificó que:
- Los contenedores Docker (`db`, `pgadmin`) levantan correctamente.
- Las migraciones (`flask db upgrade`) se aplican secuencialmente sin conflictos.
- El script de población (`seed_all.py`) es **idempotente**, es decir, se puede ejecutar repetidas veces sin duplicar registros y recuperando configuraciones por defecto.
- La suite de pruebas de integración y unitarias (`pytest`) alcanza 100% de éxito (58 tests), validando las reglas de negocio (cruces de horarios, límites de participantes, auditoría).

## Consideraciones de Seguridad
- Se verificó la exclusión estricta de `.env` y de credenciales JSON de Firebase en el repositorio (`.gitignore`).
- La API intercepta adecuadamente accesos no autorizados (protección por roles mediante `@roles_accepted`).
- Los tokens de sesión y acceso se mantienen fuera de los registros logueados en producción.
- El `refresh_token` permite renovar sesiones de manera segura, cerrando sesión forzosamente si se compromete o expira.

## Despliegue en Entornos Físicos y Locales

La aplicación móvil se conecta al backend utilizando la ruta definida en `NetworkConfig.kt`. Existen tres escenarios principales:

1. **Emulador (Localhost Host)**:
   La URL por defecto es `http://10.0.2.2:5000`. No requiere configuración adicional.

2. **Dispositivo Físico en la misma Red WiFi**:
   Sustituir la URL base por la IP local de la computadora (Ej. `http://192.168.1.50:5000`). El backend debe correr escuchando a la red con el comando: `python run.py --host=0.0.0.0`.

3. **Redes Restrictivas o Pruebas Remotas (Recomendado para Piloto híbrido)**:
   Si el router de la oficina bloquea conexiones entrantes, se recomienda el uso de **ngrok**:
   ```bash
   ngrok http 5000
   ```
   Ngrok proveerá una URL pública (ej. `https://1234abcd.ngrok-free.app`). Se debe pegar esta URL exacta en `NetworkConfig.kt`, compilar el APK en modo Release o Debug e instalarlo en los dispositivos del piloto.

## Checklist Manual UAT (User Acceptance Testing)

Para certificar la versión final en el piloto, los usuarios designados deben ejecutar las siguientes pruebas de humo y funcionales:

### Portal Web
- [ ] Iniciar sesión exitosamente como Admin, Secretaría y Usuario general.
- [ ] Ver el Dashboard diferenciado según el rol.
- [ ] Intentar navegar a `/admin` como Usuario normal y comprobar que el acceso es denegado.
- [ ] (Secretaría / Usuario) Crear una reunión exitosamente con asistentes e invitados.
- [ ] Generar código QR para una reunión existente.
- [ ] Marcar asistencia manual desde la vista de detalles.

### Aplicación Android
- [ ] Iniciar sesión utilizando credenciales de un Usuario con reuniones asignadas.
- [ ] Navegar entre la pestaña "Hoy" y "Próximas".
- [ ] Ver detalles de una reunión pendiente y aceptar la invitación.
- [ ] (Si se está en dispositivo físico): Tocar "Escanear Asistencia", permitir cámara y escanear el QR mostrado en la web.
- [ ] (Si se está en emulador sin cámara inyectada): Utilizar el "Modo Manual" e ingresar el código alfanumérico visible en la URL del QR.
- [ ] Validar que el resultado sea "¡Asistencia registrada correctamente!".
- [ ] Forzar la simulación de expiración de token y constatar que la aplicación redirige al Login y borra el caché (Validación del `OkHttp Authenticator`).

## Limitaciones Vigentes
No forman parte de esta fase piloto las siguientes funcionalidades avanzadas:
- Reportes automáticos (PDF, Excel).
- Flujo de Actas o Fichas técnicas completadas pos-reunión.
- Grabación de Audio y posterior transcripción de la sesión.
- Panel administrativo completo dentro de la app móvil.
