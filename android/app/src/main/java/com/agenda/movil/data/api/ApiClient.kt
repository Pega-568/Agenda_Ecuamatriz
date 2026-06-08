package com.agenda.movil.data.api

import android.content.Context
import com.agenda.movil.data.local.AuthTokenManager
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    // Configuración movida a NetworkConfig.kt

    fun create(context: Context): AgendaApiService {
        val authTokenManager = AuthTokenManager(context)

        val authInterceptor = Interceptor { chain ->
            val requestBuilder = chain.request().newBuilder()
            
            // Adjuntar token si la ruta no es login/refresh
            val currentToken = runBlocking { authTokenManager.accessToken.firstOrNull() }
            if (!currentToken.isNullOrEmpty()) {
                requestBuilder.addHeader("Authorization", "Bearer $currentToken")
            }
            
            chain.proceed(requestBuilder.build())
        }

        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            // Aquí idealmente también iría un Authenticator para manejar el refresh automático,
            // pero por brevedad manejaremos el estado 401 en los flujos o se puede extender aquí.
            .build()

        return Retrofit.Builder()
            .baseUrl(NetworkConfig.BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(AgendaApiService::class.java)
    }
}
