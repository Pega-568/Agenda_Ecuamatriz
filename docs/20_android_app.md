# 20 — Aplicación Android Nativa (Fase 7)

## Tecnologías Utilizadas
- **Kotlin**: Lenguaje de programación principal.
- **Jetpack Compose**: Framework declarativo para la construcción de la interfaz de usuario (UI).
- **Retrofit & OkHttp**: Clientes para el consumo de la API REST del backend.
- **DataStore**: Almacenamiento local seguro para tokens de autenticación JWT.
- **Firebase Cloud Messaging (FCM)**: Recepción de notificaciones push de eventos de la agenda.

## Configuración y Entorno

### Base URL del Backend
El endpoint al cual se conecta la app se define en `ApiClient.kt`.
- **Emulador Local**: Utiliza `http://10.0.2.2:5000` para apuntar al localhost de la máquina de desarrollo.
- **Dispositivo Físico Local**: Debe configurarse con la IP local de la computadora (ej. `http://192.168.1.XX:5000`) y asegurarse de que tanto el dispositivo como la computadora estén en la misma red Wi-Fi.
- **Producción**: Reemplazar con el dominio oficial del servidor (ej. `https://api.agenda.ecuamatriz.com`).

### Configuración de Firebase (`google-services.json`)
Para que la app pueda recibir notificaciones y utilizar los servicios de Firebase:
1. Crear un proyecto en la consola de Firebase.
2. Agregar una aplicación Android con el Application ID `com.agenda.movil`.
3. Descargar el archivo `google-services.json` proporcionado por la consola.
4. Ubicar el archivo en la ruta `android/app/google-services.json`.

> [!NOTE]
> Por motivos de seguridad, `google-services.json` está excluido del control de versiones mediante `.gitignore`. Si el repositorio es clonado en un nuevo entorno, será necesario volver a colocar este archivo para poder compilar. Se ha provisto un archivo dummy que permite compilar pero que debe ser reemplazado para conectarse al backend real.

## Arquitectura y Funcionalidad
La app sigue una arquitectura moderna dividida por paquetes lógicos:
- `ui`: Contiene las pantallas (`LoginScreen`, `HomeScreen`, `MeetingDetailScreen`, `QrScannerScreen`) y la configuración de navegación (`Navigation.kt`).
- `data/api`: Modelos de petición/respuesta (DTOs) y configuración de Retrofit.
- `data/local`: Gestión del almacenamiento de tokens mediante Jetpack DataStore.
- `theme`: Configuración de la paleta de colores corporativos Ecuamatriz (Primary `#003091`, Secondary `#0057FF`, Accent `#48C9E3`).

## Pruebas y Validación Local
1. Levantar el backend y base de datos con Docker.
2. Ejecutar las migraciones y el seeder.
3. Compilar e instalar la app Android en un emulador o dispositivo físico.
4. Iniciar sesión usando las credenciales predeterminadas del seeder.
5. El token será almacenado en DataStore y se adjuntará automáticamente como cabecera `Bearer` en cada petición posterior gracias al interceptor de OkHttp.
