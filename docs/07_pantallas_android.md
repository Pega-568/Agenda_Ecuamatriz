# 07 — Pantallas Android

> **Estado**: Fase 7 — Pendiente de implementación.
> El backend y la web deben estar estabilizados antes de iniciar la app Android.

## Stack técnico

| Tecnología         | Uso                                              |
|--------------------|--------------------------------------------------|
| Kotlin             | Lenguaje principal                               |
| Jetpack Compose    | UI declarativa                                   |
| Retrofit / OkHttp  | Cliente HTTP para consumir la API Flask          |
| Room               | Caché local (datos de sesión, reuniones offline) |
| Firebase Messaging | Notificaciones push                              |
| CameraX + ML Kit   | Escaneo QR de asistencia                         |
| DataStore          | Configuración de servidor y sesión               |

---

## Estructura de carpetas planificada

```
android/app/src/main/java/com/ecuamatriz/agenda/
  api/
    ApiClient.kt         — Configuración Retrofit
    ApiService.kt        — Interfaces de endpoints
    interceptors/        — Auth, logging, error
  dto/
    UserDto.kt
    MeetingDto.kt
    NotificationDto.kt
    ...
  repository/
    AuthRepository.kt
    MeetingRepository.kt
    NotificationRepository.kt
    ...
  local/
    AppDatabase.kt
    dao/
    entities/
  viewmodel/
    LoginViewModel.kt
    MeetingViewModel.kt
    ...
  screens/
    auth/
    home/
    meetings/
    invitations/
    qr/
    technical_sheet/
    notifications/
    profile/
    settings/
  components/
    MeetingCard.kt
    ParticipantChip.kt
    AvailabilityIndicator.kt
    NotificationItem.kt
    ...
  navigation/
    AppNavGraph.kt
    Routes.kt
  utils/
    DateUtils.kt
    QrUtils.kt
    ...
```

---

## Pantallas de Usuario (Android)

| Pantalla                 | Descripción                                           |
|--------------------------|-------------------------------------------------------|
| Configuración servidor   | URL del servidor. Editable. No hardcoded.             |
| Login                    | Email + contraseña. JWT guardado en DataStore.        |
| Inicio / Dashboard       | Próximas reuniones, invitaciones pendientes, accesos rápidos. |
| Nueva reunión            | Flujo de creación de reunión (mismo flujo que web).   |
| Mis reuniones            | Lista de reuniones propias.                           |
| Invitaciones pendientes  | Lista con acciones Aceptar / Rechazar.               |
| Detalle de reunión       | Datos completos, estado de participantes.             |
| Escanear QR              | Cámara + CameraX para escanear y marcar asistencia.  |
| Mostrar QR               | Si el usuario es creador, muestra el QR de la reunión.|
| Grabación (Fase 8)       | Iniciar grabación de audio si soy creador.           |
| Ficha técnica pendiente  | Completar/editar ficha técnica.                      |
| Notificaciones           | Lista de notificaciones con acciones.                |
| Perfil                   | Datos personales, cambio de contraseña.              |

---

## Pantallas de Secretaría (Android)

| Pantalla           | Descripción                              |
|--------------------|------------------------------------------|
| Inicio             | Resumen de reuniones del día.            |
| Registros básicos  | Lista de reuniones recientes.            |
| Detalle reunión    | Asistencia y ficha técnica.              |
| Notificaciones     | Centro de notificaciones.                |
| Perfil             | Datos personales.                        |

> Admin **no tendrá app móvil** en la primera versión.

---

## Reglas de implementación Android

1. **No hardcodear la URL del servidor.** Configurable desde pantalla de configuración.
2. **No `MainActivity` gigante.** Separar por pantallas y ViewModels.
3. **Manejar estados claramente**: Loading → Success / Empty / Error / Offline.
4. **Caché local con Room** para sesión y datos críticos offline.
5. **Tokens JWT** guardados en DataStore (no SharedPreferences sin cifrado).
6. **FCM token** actualizado al servidor en cada login.
7. **Notificaciones push** deben llevar a la pantalla correspondiente al tocar.
8. **QR Scanner** solo disponible para usuarios autenticados.
   Solo marca asistencia de la reunión del token escaneado.

---

*Pantallas Android — Fase 0 — Agenda Ecuamatriz*
