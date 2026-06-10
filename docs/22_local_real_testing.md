# Pruebas Reales Locales (Fase 9 - Estabilización Piloto)

Esta bitácora documenta las pruebas reales de conectividad entre el backend levantado localmente y la aplicación de Android instalada en un dispositivo físico.

## Contexto de la Red

- **IP Local usada:** `192.168.0.139` (Asignada a la laptop ejecutando Flask)
- **Puerto:** `5000`
- **Condiciones:** Dispositivo móvil y laptop en la misma red Wi-Fi, sin proxy ni túneles como ngrok o Cloudflare.

## Credenciales Demo Usadas (Seed)

Las credenciales reales sembradas por `seed_all.py` para realizar las pruebas de login son:

- **Rol Administrador:**
  - Email: `admin@ecuamatriz.com`
  - Password: `Test1234!`
- **Rol Secretaría:**
  - Email: `secretaria@ecuamatriz.com`
  - Password: `Test1234!`
- **Rol Usuario (Recomendado para la App Móvil):**
  - Email: `usuario1@ecuamatriz.com`
  - Password: `Test1234!`

## Resultado de Prueba de Login Externa (HTTP Client)

Se ejecutó un login manual mediante HTTP Client apuntando a `http://192.168.0.139:5000/api/auth/login`.

- **Cuerpo de la petición:**
```json
{
  "email": "usuario1@ecuamatriz.com",
  "password": "Test1234!"
}
```
- **Respuesta esperada y validada:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "user": {
      "id": 3,
      "email": "usuario1@ecuamatriz.com",
      "first_name": "Usuario",
      "last_name": "Demo 1",
      "role": "usuario"
    }
  }
}
```

## Problema Detectado en Login Android

Al analizar el código Android se encontró el motivo por el cual el login fallaba internamente en la aplicación:

### Causas encontradas:
1. **Formato de Petición:** El backend (`/api/auth/login`) esperaba recibir los datos del login como un Payload JSON (`@Body request: LoginRequest`), pero Android estaba usando Retrofit con el modificador `@FormUrlEncoded` y enviando `email` y `password` como form-data.
2. **Parsing de Respuesta:** El backend envolvía la respuesta exitosa bajo un modelo uniforme `{"success": true, "data": {...}}`. Sin embargo, Android intentaba deserializar directamente los atributos de `LoginResponse` (es decir, `access_token`, `refresh_token`, y `user`) asumiendo que estaban en la raíz del JSON, resultando en nulos o crash interno por parsing.

### Correcciones aplicadas:
- Se implementó un contenedor estandarizado **`ApiResponse<T>`** en los modelos de Retrofit de Android para mapear correctamente las respuestas anidadas dentro del objeto `data`.
- Se reemplazó `@FormUrlEncoded` por `@Body request: LoginRequest` en el endpoint `login` del `AgendaApiService.kt`.
- Se aplicó esta corrección en todos los endpoints que usan Retrofit (`getMeetingsToday()`, `acceptInvitation()`, `markAttendanceQR()`, etc.), asegurando coherencia en el parseo global.
- Se mejoró sustancialmente el manejo de excepciones en `LoginScreen.kt`, diferenciando entre errores de parsing, código de estado HTTP o excepciones de I/O de red para ofrecer retroalimentación útil en pantalla.

## Resultados Finales

- La aplicación Android ahora procesa exitosamente el inicio de sesión.
- Navegación asegurada en Home, visualizando los listados correctos protegidos con JWT.
- Renovación y validación de tokens corregidos gracias al envoltorio `ApiResponse<T>`.

## Validación de Endpoints y Notificaciones (Actualización Piloto)

1. **Test unitarios pasados (Pytest)**: Se resolvieron problemas de concurrencia y permisos en base de datos al inicializar los esquemas de tests, garantizando validación al 100% de la suite.
7. **Tab de Notificaciones (Android)**: Integración correcta en el `HomeScreen` consultando al nuevo endpoint unificado `GET /api/mobile/notifications`.
8. **Flujo de Asistencia y QR**: Se ha comprobado que el sistema registra eventos de asistencia o fallos específicos (QR inválido, usuario no invitado) generando una notificación al usuario en lugar de colapsar silenciosamente.

## Validación Final de Interfaces (Fase 9.4)

Tras la refactorización de todas las interfaces (`dashboard.html`, `meeting_detail.html`, `create_meeting.html` y los fragmentos de Compose en Android) hacia el diseño oficial **Stitch**:
- Se ejecutó el flujo completo: `Login` -> `Agendar` -> `Invitación Recibida` -> `Aceptar` -> `Escanear QR` -> `Asistencia Registrada` sin interrupciones.
- Se certifica la ausencia de regresiones. Ninguna ruta base de Flask ni endpoint móvil fue alterado en este proceso.
- Las variables de entorno para prueba en LAN (`192.168.0.139`) siguen vigentes y operativas.
