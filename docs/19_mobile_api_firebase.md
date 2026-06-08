# API Móvil y Firebase (Fase 6)

## Arquitectura de Autenticación
La API Móvil de Android se comunica de manera stateless a través de endpoints REST.
A diferencia de la aplicación web que usa `Flask-Login` (sesiones), la aplicación móvil usa JSON Web Tokens (JWT) mediante la extensión `Flask-JWT-Extended`.

### Rutas Base
Las rutas móviles se encuentran prefijadas bajo:
- `/api/auth/`: Para operaciones de autenticación (login, refresh, logout, devices, perfil)
- `/api/mobile/`: Rutas exclusivas del móvil (ej. `/api/mobile/meetings`, `/api/mobile/attendance`)

## Firebase Cloud Messaging (FCM)
El módulo `FirebaseService` (ubicado en `app/firebase/service.py`) se encarga de enviar notificaciones push a los dispositivos registrados del usuario.
*Funciona de manera silenciosa si `FCM_ENABLED=false` está en `.env`, simulando el envío localmente.*

### Modelo de Datos
Se implementó la entidad `MobileDeviceToken` en `app/users/models.py`.
- Un usuario puede registrar múltiples dispositivos (`user_id`).
- Un token único identifica a la aplicación en el dispositivo (`fcm_token`).

## Flujo de Notificaciones (Futuro)
Cuando se crea una reunión, el `MeetingService` y el `AttendanceService` notificarán usando `FirebaseService.send_push_to_user()` a aquellos involucrados. Este envío ocurrirá en segundo plano (vía Celery o asíncrono) para evitar bloqueos en el hilo HTTP.
