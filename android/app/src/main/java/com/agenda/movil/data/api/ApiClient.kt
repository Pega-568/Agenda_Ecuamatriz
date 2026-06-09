package com.agenda.movil.data.api

import android.content.Context
import com.agenda.movil.data.local.AuthTokenManager
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import org.json.JSONObject

object ApiClient {

    fun create(context: Context): AgendaApiService {
        val authTokenManager = AuthTokenManager(context)

        val authInterceptor = Interceptor { chain ->
            val requestBuilder = chain.request().newBuilder()
            val path = chain.request().url.encodedPath
            
            // Adjuntar token si la ruta no es login/refresh
            if (!path.contains("/login") && !path.contains("/refresh")) {
                val currentToken = runBlocking { authTokenManager.accessToken.firstOrNull() }
                if (!currentToken.isNullOrEmpty()) {
                    requestBuilder.addHeader("Authorization", "Bearer $currentToken")
                }
            }
            
            chain.proceed(requestBuilder.build())
        }

        val authenticator = okhttp3.Authenticator { _, response ->
            val path = response.request.url.encodedPath
            if (path.contains("/refresh") || path.contains("/login")) {
                return@Authenticator null
            }
            
            if (response.priorResponse != null) {
                return@Authenticator null
            }

            val refreshToken = runBlocking { authTokenManager.refreshToken.firstOrNull() }
            if (refreshToken.isNullOrEmpty()) {
                runBlocking { authTokenManager.emitSessionExpired() }
                return@Authenticator null
            }

            val refreshRequest = okhttp3.Request.Builder()
                .url("${NetworkConfig.BASE_URL}/api/auth/refresh")
                .post("".toRequestBody(null))
                .addHeader("Authorization", "Bearer $refreshToken")
                .build()
                
            val cleanClient = OkHttpClient()
            try {
                val refreshResponse = cleanClient.newCall(refreshRequest).execute()
                if (refreshResponse.isSuccessful) {
                    val bodyString = refreshResponse.body?.string()
                    if (!bodyString.isNullOrEmpty()) {
                        val jsonObject = JSONObject(bodyString)
                        val dataObject = if (jsonObject.has("data")) jsonObject.getJSONObject("data") else jsonObject
                        val newAccessToken = dataObject.getString("access_token")
                        // En backend de Flask, puede o no venir el refresh_token de vuelta.
                        // Asumimos que si no viene, reusamos el mismo.
                        val newRefreshToken = if (dataObject.has("refresh_token")) dataObject.getString("refresh_token") else refreshToken
                        
                        runBlocking { authTokenManager.saveTokens(newAccessToken, newRefreshToken) }
                        
                        return@Authenticator response.request.newBuilder()
                            .header("Authorization", "Bearer $newAccessToken")
                            .build()
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
            
            // Refresh failed
            runBlocking { 
                authTokenManager.clearTokens()
                authTokenManager.emitSessionExpired() 
            }
            null
        }

        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY // Nota: consider cambiar a NONE en prod para no imprimir tokens
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .authenticator(authenticator)
            .addInterceptor(loggingInterceptor)
            .build()

        return Retrofit.Builder()
            .baseUrl(NetworkConfig.BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(AgendaApiService::class.java)
    }
}
