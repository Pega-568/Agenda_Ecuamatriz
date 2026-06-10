package com.agenda.movil.ui.qr

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.agenda.movil.data.api.ApiClient
import com.agenda.movil.ui.components.ErrorState
import com.agenda.movil.ui.components.LoadingState
import com.agenda.movil.ui.components.PrimaryButton
import com.agenda.movil.ui.components.SecondaryButton
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.util.concurrent.Executors

fun extractToken(input: String): String {
    val regex = "/attendance/qr/([^/?]+)".toRegex()
    val match = regex.find(input)
    if (match != null) {
        return match.groupValues[1]
    }
    return input.trim()
}

@Composable
fun CameraPreview(
    onBarcodeDetected: (String) -> Unit
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }

    AndroidView(
        factory = { ctx ->
            val previewView = PreviewView(ctx)
            val executor = ContextCompat.getMainExecutor(ctx)
            
            cameraProviderFuture.addListener({
                val cameraProvider = cameraProviderFuture.get()
                val preview = Preview.Builder().build().also {
                    it.setSurfaceProvider(previewView.surfaceProvider)
                }
                
                val imageAnalysis = ImageAnalysis.Builder()
                    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                    .build()
                    .also {
                        it.setAnalyzer(
                            Executors.newSingleThreadExecutor(),
                            BarcodeAnalyzer { barcode ->
                                onBarcodeDetected(barcode)
                            }
                        )
                    }

                val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
                
                try {
                    cameraProvider.unbindAll()
                    cameraProvider.bindToLifecycle(
                        lifecycleOwner,
                        cameraSelector,
                        preview,
                        imageAnalysis
                    )
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }, executor)
            previewView
        },
        modifier = Modifier.fillMaxSize()
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QrScannerScreen(onBack: () -> Unit, onScanSuccess: (String) -> Unit) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    
    var hasCameraPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED
        )
    }
    
    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
        onResult = { granted -> hasCameraPermission = granted }
    )

    LaunchedEffect(Unit) {
        if (!hasCameraPermission) {
            permissionLauncher.launch(Manifest.permission.CAMERA)
        }
    }

    var manualMode by remember { mutableStateOf(false) }
    var manualToken by remember { mutableStateOf("") }
    var resultMessage by remember { mutableStateOf<String?>(null) }
    var isLoading by remember { mutableStateOf(false) }
    var isSuccess by remember { mutableStateOf(false) }

    val processToken: (String) -> Unit = { rawInput ->
        if (!isLoading) {
            isLoading = true
            resultMessage = null
            isSuccess = false
            val token = extractToken(rawInput)
            coroutineScope.launch {
                try {
                    val response = ApiClient.create(context).markAttendanceQR(token)
                    if (response.isSuccessful && response.body()?.success == true) {
                        isSuccess = true
                        resultMessage = "¡Asistencia registrada correctamente!"
                    } else {
                        val errorBody = response.errorBody()?.string()
                        val msg = try {
                            val jsonObj = JSONObject(errorBody ?: "")
                            if (jsonObj.has("error") && jsonObj.get("error") is JSONObject) {
                                jsonObj.getJSONObject("error").getString("message")
                            } else if (jsonObj.has("error")) {
                                jsonObj.getString("error")
                            } else {
                                "Código HTTP ${response.code()}"
                            }
                        } catch (e: Exception) {
                            "Código HTTP ${response.code()}"
                        }
                        resultMessage = "Error: $msg"
                    }
                } catch (e: Exception) {
                    resultMessage = "Error de conexión"
                } finally {
                    isLoading = false
                }
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Escanear QR", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold)) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Volver")
                    }
                },
                actions = {
                    IconButton(onClick = { manualMode = !manualMode }) {
                        Icon(
                            if (manualMode) Icons.Default.CameraAlt else Icons.Default.Edit,
                            contentDescription = "Cambiar modo"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.primary,
                    navigationIconContentColor = MaterialTheme.colorScheme.onSurfaceVariant,
                    actionIconContentColor = MaterialTheme.colorScheme.primary
                )
            )
        },
        containerColor = if (manualMode) MaterialTheme.colorScheme.background else Color.Black
    ) { padding ->
        Box(modifier = Modifier.padding(padding).fillMaxSize()) {
            if (manualMode) {
                Column(
                    modifier = Modifier.fillMaxSize().padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(16.dp),
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(24.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text("Ingreso Manual (Debug)", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                            Spacer(modifier = Modifier.height(8.dp))
                            Text("Pega aquí la URL o token del código QR para probar.", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
                            Spacer(modifier = Modifier.height(24.dp))
                            
                            OutlinedTextField(
                                value = manualToken,
                                onValueChange = { manualToken = it },
                                label = { Text("Token o URL del QR") },
                                modifier = Modifier.fillMaxWidth(),
                                colors = OutlinedTextFieldDefaults.colors(
                                    unfocusedContainerColor = Color.Transparent,
                                    focusedContainerColor = Color.Transparent,
                                    unfocusedBorderColor = MaterialTheme.colorScheme.outlineVariant,
                                    focusedBorderColor = MaterialTheme.colorScheme.primary
                                )
                            )
                            Spacer(modifier = Modifier.height(24.dp))
                            
                            if (isLoading) {
                                CircularProgressIndicator(color = MaterialTheme.colorScheme.primary)
                            } else {
                                PrimaryButton(
                                    text = "Procesar Token",
                                    onClick = {
                                        if (manualToken.isNotBlank()) {
                                            processToken(manualToken)
                                        }
                                    },
                                    modifier = Modifier.fillMaxWidth()
                                )
                            }
                        }
                    }
                }
            } else {
                if (hasCameraPermission) {
                    CameraPreview(onBarcodeDetected = { barcode ->
                        if (!isLoading && resultMessage == null) {
                            processToken(barcode)
                        }
                    })
                    
                    // Scanner Overlay Box
                    Box(
                        modifier = Modifier
                            .align(Alignment.Center)
                            .size(250.dp)
                            .background(Color.Transparent)
                    ) {
                        // Just an empty box to show where the scanner is
                        // In a real app we'd draw an outline here
                    }

                    if (isLoading) {
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .background(Color.Black.copy(alpha = 0.5f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                CircularProgressIndicator(color = Color.White)
                                Spacer(modifier = Modifier.height(16.dp))
                                Text("Registrando asistencia...", color = Color.White, style = MaterialTheme.typography.titleMedium)
                            }
                        }
                    }
                } else {
                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(MaterialTheme.colorScheme.background)
                            .padding(24.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        ErrorState(message = "Se requiere permiso de cámara para escanear el QR.")
                        Spacer(modifier = Modifier.height(24.dp))
                        PrimaryButton(
                            text = "Solicitar Permiso",
                            onClick = { permissionLauncher.launch(Manifest.permission.CAMERA) },
                            icon = Icons.Default.CameraAlt
                        )
                    }
                }
            }

            if (resultMessage != null) {
                val cardColor = if (isSuccess) Color(0xFF2E7D61) else MaterialTheme.colorScheme.error
                Card(
                    modifier = Modifier
                        .align(Alignment.BottomCenter)
                        .padding(24.dp)
                        .fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = cardColor),
                    elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(24.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = resultMessage!!,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = Color.White,
                            textAlign = androidx.compose.ui.text.style.TextAlign.Center
                        )
                        Spacer(modifier = Modifier.height(24.dp))
                        
                        Button(
                            onClick = {
                                resultMessage = null
                                if (isSuccess) {
                                    onScanSuccess(manualToken)
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Color.White, contentColor = cardColor),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(if (isSuccess) "Continuar" else "Intentar de nuevo", fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}
