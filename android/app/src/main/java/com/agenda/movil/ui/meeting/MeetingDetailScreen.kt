package com.agenda.movil.ui.meeting

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.QrCode
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.agenda.movil.data.api.ApiClient
import com.agenda.movil.data.model.ActionRequest
import com.agenda.movil.data.model.MeetingResponse
import com.agenda.movil.ui.components.ErrorState
import com.agenda.movil.ui.components.LoadingState
import com.agenda.movil.ui.components.PrimaryButton
import com.agenda.movil.ui.components.SecondaryButton
import com.agenda.movil.ui.components.StatusChip
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MeetingDetailScreen(
    meetingId: Int,
    onBack: () -> Unit,
    navigateToQrDisplay: (Int) -> Unit
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    
    var meeting by remember { mutableStateOf<MeetingResponse?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    var showRejectDialog by remember { mutableStateOf(false) }
    var rejectComment by remember { mutableStateOf("") }
    var actionError by remember { mutableStateOf<String?>(null) }
    var actionLoading by remember { mutableStateOf(false) }

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
                title = { Text("Detalle de Reunión", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold)) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Volver")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.primary,
                    navigationIconContentColor = MaterialTheme.colorScheme.onSurfaceVariant
                )
            )
        },
        containerColor = MaterialTheme.colorScheme.background
    ) { padding ->
        if (isLoading) {
            Box(modifier = Modifier.padding(padding).fillMaxSize()) { LoadingState() }
            return@Scaffold
        }
        
        val currentMeeting = meeting
        if (currentMeeting == null) {
            Box(modifier = Modifier.padding(padding).fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("No se pudo cargar la reunión", color = MaterialTheme.colorScheme.error)
            }
            return@Scaffold
        }

        Column(
            modifier = Modifier
                .padding(padding)
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Header Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(modifier = Modifier.padding(20.dp)) {
                    Text(text = currentMeeting.title, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.DateRange, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(text = "${currentMeeting.date} | ${currentMeeting.startTime} - ${currentMeeting.endTime}", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.LocationOn, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        val locationStr = if (currentMeeting.room != null) "${currentMeeting.room.name} (${currentMeeting.room.location})" else "Modalidad: ${currentMeeting.modality}"
                        Text(text = locationStr, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    val statusColor = when (currentMeeting.status) {
                        "scheduled" -> MaterialTheme.colorScheme.primary
                        "in_progress" -> Color(0xFFE67E22) // Warning/Orange
                        "completed" -> Color(0xFF2E7D61) // Success
                        "cancelled" -> MaterialTheme.colorScheme.error
                        else -> MaterialTheme.colorScheme.onSurfaceVariant
                    }
                    val statusBgColor = statusColor.copy(alpha = 0.1f)
                    
                    StatusChip(
                        text = currentMeeting.status.uppercase(),
                        color = statusColor,
                        backgroundColor = statusBgColor
                    )
                }
            }

            // Info Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(modifier = Modifier.padding(20.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Info, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(text = "Objetivo", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurface)
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = currentMeeting.objective, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }

            // Role and Actions Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
            ) {
                Column(modifier = Modifier.padding(20.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Person, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(text = "Mi Participación", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurface)
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    if (currentMeeting.roleInMeeting == "creator") {
                        Text(text = "Rol: Organizador", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
                        if (currentMeeting.canShowQr == true) {
                            Spacer(modifier = Modifier.height(16.dp))
                            PrimaryButton(
                                text = "Mostrar QR de Asistencia",
                                icon = Icons.Default.QrCode,
                                onClick = { navigateToQrDisplay(meetingId) }
                            )
                        }
                    } else {
                        Text(text = "Rol: Participante", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Medium)
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text(text = "Invitación:", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Text(text = currentMeeting.myInvitationStatus?.uppercase() ?: "N/A", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text(text = "Asistencia:", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Text(text = currentMeeting.myAttendanceStatus?.uppercase() ?: "N/A", style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                        }
                    }

                    if (currentMeeting.canAccept == true || currentMeeting.canReject == true) {
                        Spacer(modifier = Modifier.height(24.dp))
                        Divider(color = MaterialTheme.colorScheme.outlineVariant)
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                            if (currentMeeting.canReject == true) {
                                SecondaryButton(
                                    text = "Rechazar",
                                    onClick = { showRejectDialog = true },
                                    modifier = Modifier.weight(1f),
                                    enabled = !actionLoading
                                )
                            }
                            if (currentMeeting.canAccept == true) {
                                PrimaryButton(
                                    text = "Aceptar",
                                    onClick = {
                                        actionLoading = true
                                        actionError = null
                                        coroutineScope.launch {
                                            try {
                                                val response = ApiClient.create(context).acceptInvitation(meetingId)
                                                if (response.isSuccessful && response.body()?.success == true) onBack() else actionError = "Error al aceptar"
                                            } catch (e: Exception) {
                                                actionError = "Error de conexión"
                                            } finally {
                                                actionLoading = false
                                            }
                                        }
                                    },
                                    modifier = Modifier.weight(1f),
                                    enabled = !actionLoading
                                )
                            }
                        }
                    }

                    if (actionError != null) {
                        Spacer(modifier = Modifier.height(16.dp))
                        ErrorState(message = actionError!!)
                    }
                }
            }
            
            Spacer(modifier = Modifier.height(24.dp)) // bottom padding for scroll
        }

        if (showRejectDialog) {
            AlertDialog(
                onDismissRequest = { if (!actionLoading) showRejectDialog = false },
                title = { Text("Rechazar Invitación", fontWeight = FontWeight.Bold) },
                text = {
                    Column {
                        Text("Ingrese un motivo (obligatorio):", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Spacer(modifier = Modifier.height(8.dp))
                        OutlinedTextField(
                            value = rejectComment,
                            onValueChange = { rejectComment = it },
                            modifier = Modifier.fillMaxWidth(),
                            placeholder = { Text("Motivo de rechazo") }
                        )
                    }
                },
                confirmButton = {
                    Button(
                        onClick = {
                            if (rejectComment.isNotBlank()) {
                                actionLoading = true
                                coroutineScope.launch {
                                    try {
                                        val response = ApiClient.create(context).rejectInvitation(
                                            meetingId, ActionRequest(comment = rejectComment)
                                        )
                                        if (response.isSuccessful && response.body()?.success == true) {
                                            showRejectDialog = false
                                            onBack()
                                        } else {
                                            actionError = "Error al rechazar"
                                            showRejectDialog = false
                                        }
                                    } catch (e: Exception) {
                                        actionError = "Error de conexión"
                                        showRejectDialog = false
                                    } finally {
                                        actionLoading = false
                                    }
                                }
                            }
                        },
                        enabled = !actionLoading,
                        colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error)
                    ) {
                        Text(if (actionLoading) "Enviando..." else "Confirmar")
                    }
                },
                dismissButton = {
                    TextButton(
                        onClick = { showRejectDialog = false },
                        enabled = !actionLoading
                    ) {
                        Text("Cancelar", color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            )
        }
    }
}
