package com.agenda.movil.data.api

object NetworkConfig {
    /**
     * URL Base del Backend.
     *
     * Entornos de prueba locales:
     * - Emulador Android: Usar "http://10.0.2.2:5000" para apuntar al localhost de la máquina host.
     * - Dispositivo físico (misma red WiFi): Reemplazar con la IP de tu PC, ej: "http://192.168.1.100:5000".
     *
     * Redes restrictivas o sin WiFi común:
     * - Usar ngrok (ej: "https://<id-aleatorio>.ngrok-free.app").
     * - Comando para exponer el backend local: `ngrok http 5000`.
     */
    const val BASE_URL = "http://192.168.0.139:5000/"
}
