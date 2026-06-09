package com.agenda.movil.ui.auth

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.agenda.movil.data.api.ApiClient
import com.agenda.movil.data.local.AuthTokenManager
import kotlinx.coroutines.launch

@Composable
fun LoginScreen(onLoginSuccess: () -> Unit) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "Agenda Ecuamatriz",
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.primary
        )
        Spacer(modifier = Modifier.height(32.dp))
        
        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Correo Electrónico") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )
        Spacer(modifier = Modifier.height(16.dp))
        
        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Contraseña") },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )
        Spacer(modifier = Modifier.height(24.dp))
        
        if (isLoading) {
            CircularProgressIndicator()
        } else {
            Button(
                onClick = {
                    if (email.isBlank() || password.isBlank()) {
                        errorMessage = "Llene todos los campos"
                        return@Button
                    }
                    isLoading = true
                    errorMessage = null
                    
                    coroutineScope.launch {
                        try {
                            val api = ApiClient.create(context)
                            val response = api.login(com.agenda.movil.data.model.LoginRequest(email, password))
                            if (response.isSuccessful && response.body()?.success == true && response.body()?.data != null) {
                                val data = response.body()!!.data!!
                                AuthTokenManager(context).saveTokens(data.accessToken, data.refreshToken)
                                onLoginSuccess()
                            } else {
                                val code = response.code()
                                val errorStr = response.errorBody()?.string() ?: response.message()
                                val parsedError = try {
                                    if (errorStr.contains("message")) {
                                        // Simple regex or substring to find message, or use Gson if available
                                        errorStr
                                    } else {
                                        errorStr
                                    }
                                } catch (e: Exception) { errorStr }
                                errorMessage = "Fallo (HTTP $code): $parsedError"
                            }
                        } catch (e: java.io.IOException) {
                            errorMessage = "Error de red: verifica tu conexión e IP."
                        } catch (e: Exception) {
                            errorMessage = "Error de parsing o interno: ${e.message}"
                        } finally {
                            isLoading = false
                        }
                    }
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Iniciar Sesión")
            }
        }
        
        if (errorMessage != null) {
            Spacer(modifier = Modifier.height(16.dp))
            Text(text = errorMessage!!, color = MaterialTheme.colorScheme.error)
        }
    }
}
