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
                if (response.isSuccessful) {
                    Log.d("FCM", "Token successfully registered on backend")
                } else {
                    Log.e("FCM", "Failed to register token: ${response.code()}")
                }
            } catch (e: Exception) {
                Log.e("FCM", "Error registering token", e)
            }
        }
    }

    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)
        // Handle incoming push notifications here
        Log.d("FCM", "Message received from: ${message.from}")
        if (message.notification != null) {
            Log.d("FCM", "Notification Body: ${message.notification?.body}")
        }
    }
}
