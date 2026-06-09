# 22 — Despliegue Local y Pruebas Reales

Este documento registra los comandos, configuraciones y resultados del despliegue en red local para pruebas reales de la aplicación Android interactuando con el backend.

## Configuración y Entorno

- **IP Local usada (LAN)**: `192.168.0.139`
- **Comando para levantar Docker**: `docker compose up -d`
- **Comando para preparar base de datos y correr tests**: 
  ```bash
  flask db upgrade
  python scripts/seed_all.py
  python -m pytest
  ```
- **Comando para levantar Flask en toda la red local**:
  ```bash
  python run.py --host=0.0.0.0 --port=5000
  ```
- **URL Web Local desde laptop**: `http://127.0.0.1:5000` o `http://192.168.0.139:5000`
- **BASE_URL usada en Android**: `http://192.168.0.139:5000/`
- **Permiso HTTP en Android**: `android:usesCleartextTraffic="true"` habilitado en `AndroidManifest.xml`.
- **Ruta del APK generada**: `android/app/build/outputs/apk/debug/app-debug.apk`

*(Nota: En este entorno de prueba controlado estrictamente bajo red local **NO** se usaron servicios externos como Cloudflare Tunnel o ngrok)*.

## Resultados de Compilación y Backend
- **pytest**: OK (Pruebas unitarias completas aprobadas).
- **assembleDebug**: OK (Build exitoso tras inyectar la IP local en NetworkConfig).

## Plan de Pruebas UAT en Dispositivos

A continuación, la lista de validaciones que deben ejecutarse manualmente:

### Navegador del Teléfono
- [ ] Entrar a `http://192.168.0.139:5000/health` y recibir un mensaje de sistema activo. Esto valida que la laptop y el móvil están en la misma red sin bloqueos de firewall.
- [ ] Entrar a `http://192.168.0.139:5000/` y comprobar la renderización del login web responsive.

### Aplicación Android (app-debug.apk)
- [ ] Instalación correcta permitiendo orígenes desconocidos.
- [ ] **Login**: Conexión al backend local confirmada tras inicio de sesión exitoso.
- [ ] **Dashboard de Reuniones**: Carga de pestaña "Hoy" y "Próximas" con datos servidos por PostgreSQL local.
- [ ] **Invitaciones**: Recepción de invitaciones (en la pestaña de invitaciones).
- [ ] **Acciones de Invitación**: Aceptar o rechazar, verificando actualización inmediata.
- [ ] **FCM Token**: Registro exitoso del token en la base de datos local al hacer login (en modo silence ya que FCM_ENABLED=false).
- [ ] **QR Escáner**: Prueba de `CameraX` capturando un código y consumiendo `http://192.168.0.139:5000/api/mobile/attendance/qr/...`.
- [ ] **Modo Manual**: Funcionamiento correcto al tipear URL/Token si se carece de QR.
- [ ] **Refresh JWT**: Deslogueo forzado con mensaje de caducidad superada, o renovación imperceptible en el background.

### Web (Admin/Secretaría/Usuario)
- [ ] **Login Web**: OK.
- [ ] **Roles Restringidos**: Admin sin acceso a creación de reuniones; Usuario sin acceso al portal Admin.
- [ ] **Creación de Reunión**: OK.
- [ ] **Consulta y Generación QR**: Generado dinámicamente desde el detalle de la reunión.
- [ ] **Asistencia Manual**: Ingreso manual habilitado para secretaría si la configuración local lo permite.

## Ajustes y Correcciones Post-Prueba (Fase 9.1)
- **Token CSRF**: Se corrigió el problema visual en los formularios de la interfaz Admin donde el token CSRF se mostraba como texto en lugar de inyectarse como un campo `<input type="hidden">`.
- **Navegación Sidebar**: Se corrigió el archivo `sidebar.html` asegurando que las URLs redirijan correctamente mediante `url_for` en lugar de anclas muertas (`href="#"`). Se corrigió el mapeo de roles ("secretaria" y "usuario" en lugar de sus versiones en inglés).
- **Conectividad Firewall**: Si la app de Android arroja un error de conexión, se documentó que es necesario abrir el puerto `5000` (TCP de entrada) en el Firewall local de Windows.
