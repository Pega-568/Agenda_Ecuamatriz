package com.agenda.movil.ui.qr

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.agenda.movil.data.api.ApiClient
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QrScannerScreen(onBack: () -> Unit, onScanSuccess: (String) -> Unit) {
    var manualToken by remember { mutableStateOf("") }
    var resultMessage by remember { mutableStateOf<String?>(null) }
    var isLoading by remember { mutableStateOf(false) }
    
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Escanear Asistencia (Simulador)") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Volver")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary,
                    navigationIconContentColor = MaterialTheme.colorScheme.onPrimary
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier.padding(padding).fillMaxSize().padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text("Simulador de escáner QR", style = MaterialTheme.typography.titleLarge)
            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(
                value = manualToken,
                onValueChange = { manualToken = it },
                label = { Text("Token del QR") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(24.dp))
            
            if (isLoading) {
                CircularProgressIndicator()
            } else {
                Button(onClick = {
                    if (manualToken.isNotBlank()) {
                        isLoading = true
                        resultMessage = null
                        coroutineScope.launch {
                            try {
                                val response = ApiClient.create(context).markAttendanceQR(manualToken)
                                if (response.isSuccessful) {
                                    resultMessage = "¡Asistencia registrada correctamente!"
                                } else {
                                    resultMessage = "Error al registrar asistencia (código: ${response.code()})"
                                }
                            } catch (e: Exception) {
                                resultMessage = "Error de conexión"
                            } finally {
                                isLoading = false
                            }
                        }
                    }
                }) {
                    Text("Procesar Token")
                }
            }

            if (resultMessage != null) {
                Spacer(modifier = Modifier.height(24.dp))
                Text(text = resultMessage!!, style = MaterialTheme.typography.bodyLarge)
            }
        }
    }
}
