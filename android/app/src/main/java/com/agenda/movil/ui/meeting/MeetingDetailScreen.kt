package com.agenda.movil.ui.meeting

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.agenda.movil.data.api.ApiClient
import com.agenda.movil.data.model.ActionRequest
import com.agenda.movil.data.model.MeetingResponse
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MeetingDetailScreen(meetingId: Int, onBack: () -> Unit) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    
    var meeting by remember { mutableStateOf<MeetingResponse?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    var showRejectDialog by remember { mutableStateOf(false) }
    var rejectComment by remember { mutableStateOf("") }
    var actionError by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(meetingId) {
        try {
            val response = ApiClient.create(context).getMeetingDetail(meetingId)
            if (response.isSuccessful) {
                meeting = response.body()?.data
            }
        } finally {
            isLoading = false
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Detalle de Reunión") },
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
        if (isLoading) {
            CircularProgressIndicator(modifier = Modifier.padding(padding))
            return@Scaffold
        }
        
        val currentMeeting = meeting
        if (currentMeeting == null) {
            Text("No se pudo cargar la reunión", modifier = Modifier.padding(padding))
            return@Scaffold
        }

        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text(text = currentMeeting.title, style = MaterialTheme.typography.headlineSmall)
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = "Objetivo: ${currentMeeting.objective}")
            Text(text = "Fecha: ${currentMeeting.date}")
            Text(text = "Horario: ${currentMeeting.startTime} - ${currentMeeting.endTime}")
            Text(text = "Estado: ${currentMeeting.status}")
            
            if (currentMeeting.room != null) {
                Text(text = "Sala: ${currentMeeting.room.name} (${currentMeeting.room.location})")
            } else {
                Text(text = "Modalidad: ${currentMeeting.modality}")
            }

            Spacer(modifier = Modifier.height(16.dp))
            
            if (currentMeeting.roleInMeeting == "creator") {
                Text(text = "Rol: Organizador")
                if (currentMeeting.canShowQr == true) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = "El código QR puede generarse en la Web.")
                }
            } else {
                Text(text = "Mi Invitación: ${currentMeeting.myInvitationStatus ?: "N/A"}")
                Text(text = "Mi Asistencia: ${currentMeeting.myAttendanceStatus ?: "N/A"}")
            }

            Spacer(modifier = Modifier.height(24.dp))

            if (currentMeeting.canAccept == true || currentMeeting.canReject == true) {
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    if (currentMeeting.canAccept == true) {
                        Button(onClick = {
                            coroutineScope.launch {
                                val response = ApiClient.create(context).acceptInvitation(meetingId)
                                if (response.isSuccessful && response.body()?.success == true) onBack() else actionError = "Error al aceptar"
                            }
                        }) {
                            Text("Aceptar")
                        }
                    }
                    if (currentMeeting.canReject == true) {
                        OutlinedButton(onClick = { showRejectDialog = true }) {
                            Text("Rechazar")
                        }
                    }
                }
            }

            if (actionError != null) {
                Text(text = actionError!!, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp))
            }
        }

        if (showRejectDialog) {
            AlertDialog(
                onDismissRequest = { showRejectDialog = false },
                title = { Text("Rechazar Invitación") },
                text = {
                    Column {
                        Text("Ingrese un comentario obligatorio:")
                        OutlinedTextField(
                            value = rejectComment,
                            onValueChange = { rejectComment = it },
                            modifier = Modifier.fillMaxWidth()
                        )
                    }
                },
                confirmButton = {
                    Button(onClick = {
                        if (rejectComment.isNotBlank()) {
                            coroutineScope.launch {
                                val response = ApiClient.create(context).rejectInvitation(
                                    meetingId, ActionRequest(comment = rejectComment)
                                )
                                if (response.isSuccessful && response.body()?.success == true) {
                                    showRejectDialog = false
                                    onBack()
                                } else {
                                    actionError = "Error al rechazar"
                                }
                            }
                        }
                    }) {
                        Text("Confirmar")
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showRejectDialog = false }) {
                        Text("Cancelar")
                    }
                }
            )
        }
    }
}
