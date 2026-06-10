package com.agenda.movil.ui.meeting

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Description
import androidx.compose.material.icons.filled.Event
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Place
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material.icons.filled.Title
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.agenda.movil.data.api.ApiClient
import com.agenda.movil.data.model.AvailabilityCheckRequest
import com.agenda.movil.data.model.AvailabilityResponse
import com.agenda.movil.data.model.CreateMeetingRequest
import com.agenda.movil.data.model.RoomOption
import com.agenda.movil.data.model.UserOption
import com.agenda.movil.ui.components.ErrorState
import com.agenda.movil.ui.components.LoadingState
import com.agenda.movil.ui.components.PrimaryButton
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import java.util.Calendar

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NewMeetingScreen(onBack: () -> Unit, onMeetingCreated: () -> Unit) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    var title by remember { mutableStateOf("") }
    var objective by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }
    var agendaItems by remember { mutableStateOf("") }
    
    var date by remember { mutableStateOf("") }
    var startTime by remember { mutableStateOf("") }
    var endTime by remember { mutableStateOf("") }
    var modality by remember { mutableStateOf("presencial") }
    
    var rooms by remember { mutableStateOf<List<RoomOption>>(emptyList()) }
    var users by remember { mutableStateOf<List<UserOption>>(emptyList()) }
    var selectedRoomId by remember { mutableStateOf<Int?>(null) }
    var selectedParticipantIds by remember { mutableStateOf(setOf<Int>()) }

    var isLoadingOptions by remember { mutableStateOf(true) }
    var isSubmitting by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    
    var availability by remember { mutableStateOf<AvailabilityResponse?>(null) }
    var checkJob by remember { mutableStateOf<Job?>(null) }

    fun checkAvailability() {
        if (date.isBlank() || startTime.isBlank() || endTime.isBlank()) {
            availability = null
            return
        }
        checkJob?.cancel()
        checkJob = coroutineScope.launch {
            delay(500) // Debounce
            try {
                val req = AvailabilityCheckRequest(
                    date = date,
                    startTime = startTime,
                    endTime = endTime,
                    roomId = if (modality == "presencial") selectedRoomId else null,
                    participantIds = selectedParticipantIds.toList()
                )
                val res = ApiClient.create(context).checkAvailability(req)
                if (res.isSuccessful) {
                    availability = res.body()?.data
                }
            } catch (e: Exception) {
                // Ignore network errors for background check
            }
        }
    }

    LaunchedEffect(date, startTime, endTime, modality, selectedRoomId, selectedParticipantIds) {
        checkAvailability()
    }

    LaunchedEffect(Unit) {
        try {
            val response = ApiClient.create(context).getMeetingOptions()
            if (response.isSuccessful && response.body()?.success == true) {
                rooms = response.body()?.data?.rooms ?: emptyList()
                users = response.body()?.data?.users ?: emptyList()
                if (rooms.isNotEmpty()) {
                    selectedRoomId = rooms.first().id
                }
            } else {
                errorMessage = "No se pudieron cargar las opciones."
            }
        } catch (e: Exception) {
            errorMessage = "Error de red al cargar opciones."
        } finally {
            isLoadingOptions = false
        }
    }

    val calendar = Calendar.getInstance()
    val datePickerDialog = DatePickerDialog(
        context,
        { _, year, month, dayOfMonth ->
            date = String.format("%04d-%02d-%02d", year, month + 1, dayOfMonth)
        },
        calendar.get(Calendar.YEAR),
        calendar.get(Calendar.MONTH),
        calendar.get(Calendar.DAY_OF_MONTH)
    )

    val startTimePickerDialog = TimePickerDialog(
        context,
        { _, hourOfDay, minute ->
            startTime = String.format("%02d:%02d", hourOfDay, minute)
        },
        calendar.get(Calendar.HOUR_OF_DAY),
        calendar.get(Calendar.MINUTE),
        true
    )

    val endTimePickerDialog = TimePickerDialog(
        context,
        { _, hourOfDay, minute ->
            endTime = String.format("%02d:%02d", hourOfDay, minute)
        },
        calendar.get(Calendar.HOUR_OF_DAY),
        calendar.get(Calendar.MINUTE),
        true
    )

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Nueva Reunión", style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold)) },
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
        if (isLoadingOptions) {
            Box(modifier = Modifier.padding(padding).fillMaxSize()) { LoadingState() }
            return@Scaffold
        }

        LazyColumn(
            modifier = Modifier
                .padding(padding)
                .fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Title, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(text = "Datos Básicos", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurface)
                        }
                        Spacer(modifier = Modifier.height(16.dp))
                        OutlinedTextField(
                            value = title,
                            onValueChange = { title = it },
                            label = { Text("Título *") },
                            modifier = Modifier.fillMaxWidth(),
                            singleLine = true,
                            colors = OutlinedTextFieldDefaults.colors(
                                unfocusedContainerColor = Color.Transparent,
                                focusedContainerColor = Color.Transparent,
                                unfocusedBorderColor = MaterialTheme.colorScheme.outlineVariant,
                                focusedBorderColor = MaterialTheme.colorScheme.primary
                            )
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        OutlinedTextField(
                            value = objective,
                            onValueChange = { objective = it },
                            label = { Text("Objetivo *") },
                            modifier = Modifier.fillMaxWidth(),
                            colors = OutlinedTextFieldDefaults.colors(
                                unfocusedContainerColor = Color.Transparent,
                                focusedContainerColor = Color.Transparent,
                                unfocusedBorderColor = MaterialTheme.colorScheme.outlineVariant,
                                focusedBorderColor = MaterialTheme.colorScheme.primary
                            )
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        OutlinedTextField(
                            value = description,
                            onValueChange = { description = it },
                            label = { Text("Descripción") },
                            modifier = Modifier.fillMaxWidth(),
                            leadingIcon = { Icon(Icons.Default.Description, contentDescription = null) },
                            colors = OutlinedTextFieldDefaults.colors(
                                unfocusedContainerColor = Color.Transparent,
                                focusedContainerColor = Color.Transparent,
                                unfocusedBorderColor = MaterialTheme.colorScheme.outlineVariant,
                                focusedBorderColor = MaterialTheme.colorScheme.primary
                            )
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        OutlinedTextField(
                            value = agendaItems,
                            onValueChange = { agendaItems = it },
                            label = { Text("Puntos de agenda") },
                            modifier = Modifier.fillMaxWidth(),
                            minLines = 3,
                            leadingIcon = { Icon(Icons.Default.List, contentDescription = null) },
                            colors = OutlinedTextFieldDefaults.colors(
                                unfocusedContainerColor = Color.Transparent,
                                focusedContainerColor = Color.Transparent,
                                unfocusedBorderColor = MaterialTheme.colorScheme.outlineVariant,
                                focusedBorderColor = MaterialTheme.colorScheme.primary
                            )
                        )
                    }
                }
            }
            
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Event, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(text = "Fecha y Horario", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurface)
                        }
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        OutlinedButton(
                            onClick = { datePickerDialog.show() },
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(8.dp),
                            colors = ButtonDefaults.outlinedButtonColors(contentColor = MaterialTheme.colorScheme.onSurface)
                        ) {
                            Icon(Icons.Default.DateRange, contentDescription = null, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(if (date.isEmpty()) "Seleccionar Fecha *" else "Fecha: $date")
                        }
                        Spacer(modifier = Modifier.height(12.dp))
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                            OutlinedButton(
                                onClick = { startTimePickerDialog.show() },
                                modifier = Modifier.weight(1f),
                                shape = RoundedCornerShape(8.dp),
                                colors = ButtonDefaults.outlinedButtonColors(contentColor = MaterialTheme.colorScheme.onSurface)
                            ) {
                                Icon(Icons.Default.Schedule, contentDescription = null, modifier = Modifier.size(18.dp))
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(if (startTime.isEmpty()) "Inicio *" else startTime)
                            }
                            OutlinedButton(
                                onClick = { endTimePickerDialog.show() },
                                modifier = Modifier.weight(1f),
                                shape = RoundedCornerShape(8.dp),
                                colors = ButtonDefaults.outlinedButtonColors(contentColor = MaterialTheme.colorScheme.onSurface)
                            ) {
                                Icon(Icons.Default.Schedule, contentDescription = null, modifier = Modifier.size(18.dp))
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(if (endTime.isEmpty()) "Fin *" else endTime)
                            }
                        }
                    }
                }
            }
            
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                ) {
                    Column(modifier = Modifier.padding(20.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Place, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(text = "Ubicación", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurface)
                        }
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            RadioButton(
                                selected = modality == "presencial",
                                onClick = { modality = "presencial" },
                                colors = RadioButtonDefaults.colors(selectedColor = MaterialTheme.colorScheme.primary)
                            )
                            Text("Presencial", style = MaterialTheme.typography.bodyMedium)
                            Spacer(modifier = Modifier.width(16.dp))
                            RadioButton(
                                selected = modality == "virtual",
                                onClick = { modality = "virtual" },
                                colors = RadioButtonDefaults.colors(selectedColor = MaterialTheme.colorScheme.primary)
                            )
                            Text("Virtual", style = MaterialTheme.typography.bodyMedium)
                        }

                        if (modality == "presencial") {
                            Spacer(modifier = Modifier.height(12.dp))
                            Text("Seleccionar Sala", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Spacer(modifier = Modifier.height(8.dp))
                            rooms.forEach { room ->
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .clickable { selectedRoomId = room.id }
                                        .padding(vertical = 4.dp)
                                ) {
                                    RadioButton(
                                        selected = selectedRoomId == room.id,
                                        onClick = { selectedRoomId = room.id },
                                        colors = RadioButtonDefaults.colors(selectedColor = MaterialTheme.colorScheme.primary)
                                    )
                                    Text("${room.name} (${room.location ?: "Sin ubicación"})", style = MaterialTheme.typography.bodyMedium)
                                }
                            }
                        }
                    }
                }
            }

            item {
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
                            Text(text = "Participantes *", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurface)
                        }
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        if (users.isEmpty()) {
                            Text("No hay usuarios disponibles.", color = MaterialTheme.colorScheme.error)
                        }
                    }
                }
            }

            items(users) { user ->
                val participantStatus = availability?.participants?.find { it.id == user.id }
                Card(
                    modifier = Modifier.fillMaxWidth().clickable {
                        selectedParticipantIds = if (selectedParticipantIds.contains(user.id)) selectedParticipantIds - user.id else selectedParticipantIds + user.id
                    },
                    shape = RoundedCornerShape(12.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = if (selectedParticipantIds.contains(user.id)) MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f) else MaterialTheme.colorScheme.surface
                    ),
                    elevation = CardDefaults.cardElevation(defaultElevation = 0.dp) // Flat lists inside
                ) {
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp, vertical = 12.dp)
                    ) {
                        Checkbox(
                            checked = selectedParticipantIds.contains(user.id),
                            onCheckedChange = { checked ->
                                selectedParticipantIds = if (checked) selectedParticipantIds + user.id else selectedParticipantIds - user.id
                            },
                            colors = CheckboxDefaults.colors(checkedColor = MaterialTheme.colorScheme.primary)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(user.name, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold)
                                if (participantStatus != null) {
                                    val color = when(participantStatus.status) {
                                        "available" -> Color(0xFF2E7D61) // Status available
                                        "busy" -> Color(0xFFC0392B) // Status busy
                                        else -> Color(0xFFF2C94C) // Conflict
                                    }
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Box(
                                        modifier = Modifier
                                            .background(color, RoundedCornerShape(4.dp))
                                            .padding(horizontal = 6.dp, vertical = 2.dp)
                                    ) {
                                        Text(
                                            text = participantStatus.status.uppercase(),
                                            color = Color.White,
                                            style = MaterialTheme.typography.labelSmall.copy(fontSize = 10.sp, fontWeight = FontWeight.Bold)
                                        )
                                    }
                                }
                            }
                            Text(user.email, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }
                }
            }

            item {
                Spacer(modifier = Modifier.height(16.dp))
                
                if (availability != null && availability?.canCreate == false) {
                    ErrorState(message = "Existen conflictos de disponibilidad que bloquean la creación de la reunión. Revisa los horarios.")
                    Spacer(modifier = Modifier.height(16.dp))
                }
                
                if (errorMessage != null) {
                    ErrorState(message = errorMessage!!)
                    Spacer(modifier = Modifier.height(16.dp))
                }

                if (isSubmitting) {
                    Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator(color = MaterialTheme.colorScheme.primary)
                    }
                } else {
                    PrimaryButton(
                        text = "Crear Reunión",
                        icon = Icons.Default.Event,
                        onClick = {
                            if (title.isBlank() || objective.isBlank() || date.isBlank() || startTime.isBlank() || endTime.isBlank()) {
                                errorMessage = "Complete los campos obligatorios."
                                return@PrimaryButton
                            }
                            if (selectedParticipantIds.isEmpty()) {
                                errorMessage = "Debe seleccionar al menos un participante."
                                return@PrimaryButton
                            }
                            if (availability?.canCreate == false) {
                                errorMessage = "Resuelva los conflictos de disponibilidad antes de continuar."
                                return@PrimaryButton
                            }
                            
                            isSubmitting = true
                            errorMessage = null
                            coroutineScope.launch {
                                try {
                                    val request = CreateMeetingRequest(
                                        title = title,
                                        objective = objective,
                                        description = description.takeIf { it.isNotBlank() },
                                        agendaItems = agendaItems.split("\n").filter { it.isNotBlank() },
                                        date = date,
                                        startTime = startTime,
                                        endTime = endTime,
                                        modality = modality,
                                        roomId = if (modality == "presencial") selectedRoomId else null,
                                        participantIds = selectedParticipantIds.toList()
                                    )
                                    val response = ApiClient.create(context).createMeeting(request)
                                    if (response.isSuccessful && response.body()?.success == true) {
                                        onMeetingCreated()
                                    } else {
                                        val errorMsg = response.errorBody()?.string() ?: "Error al crear la reunión"
                                        errorMessage = "Error HTTP ${response.code()}: $errorMsg"
                                    }
                                } catch (e: Exception) {
                                    errorMessage = "Error de conexión: ${e.message}"
                                } finally {
                                    isSubmitting = false
                                }
                            }
                        },
                        enabled = availability == null || availability?.canCreate == true
                    )
                }
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}
