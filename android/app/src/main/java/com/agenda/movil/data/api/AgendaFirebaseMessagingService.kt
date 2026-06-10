package com.agenda.movil.data.api

import android.util.Log
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import com.agenda.movil.data.model.DeviceRegisterRequest

class AgendaFirebaseMessagingService : FirebaseMessagingService() {

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.d("FCM", "New token generated: $token")
        
        // Send token to backend
        val apiService = ApiClient.create(applicationContext)
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val request = DeviceRegisterRequest(deviceToken = token)
                val response = apiService.registerDevice(request)
                if (response.isSuccessful && response.body()?.success == true) {
                    Log.d("FCM", "Token successfully registered on backend")
                } else {
                    Log.e("FCM", "Failed to register token: ${response.code()} - ${response.errorBody()?.string() ?: response.message()}")
                }
            } catch (e: Exception) {
                Log.e("FCM", "Error registering token", e)
            }
        }
    }

    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)
        Log.d("FCM", "Message received from: ${message.from}")
        
        val notificationManager = getSystemService(android.content.Context.NOTIFICATION_SERVICE) as android.app.NotificationManager
        val channelId = "agenda_ecuamatriz_channel"
        
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            val channel = android.app.NotificationChannel(
                channelId,
                "Notificaciones de Agenda",
                android.app.NotificationManager.IMPORTANCE_HIGH
            )
            notificationManager.createNotificationChannel(channel)
        }
        
        val title = message.notification?.title ?: "Nueva Notificación"
        val body = message.notification?.body ?: "Tienes un nuevo mensaje"
        Log.d("FCM", "Notification Body: $body")
        
        val notificationBuilder = androidx.core.app.NotificationCompat.Builder(this, channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(androidx.core.app.NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            
        notificationManager.notify(System.currentTimeMillis().toInt(), notificationBuilder.build())
    }
}
