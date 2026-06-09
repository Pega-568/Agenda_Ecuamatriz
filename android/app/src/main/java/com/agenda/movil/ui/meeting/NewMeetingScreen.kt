package com.agenda.movil.ui.meeting

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.agenda.movil.data.api.ApiClient
import com.agenda.movil.data.model.CreateMeetingRequest
import com.agenda.movil.data.model.RoomOption
import com.agenda.movil.data.model.UserOption
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
                title = { Text("Nueva Reunión") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Volver")
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
        if (isLoadingOptions) {
            Box(modifier = Modifier.padding(padding).fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
            return@Scaffold
        }

        LazyColumn(
            modifier = Modifier
                .padding(padding)
                .fillMaxSize()
                .padding(16.dp)
        ) {
            item {
                OutlinedTextField(
                    value = title,
                    onValueChange = { title = it },
                    label = { Text("Título *") },
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(
                    value = objective,
                    onValueChange = { objective = it },
                    label = { Text("Objetivo *") },
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(
                    value = description,
                    onValueChange = { description = it },
                    label = { Text("Descripción") },
                    modifier = Modifier.fillMaxWidth()
                )
                Spacer(modifier = Modifier.height(8.dp))
                OutlinedTextField(
                    value = agendaItems,
                    onValueChange = { agendaItems = it },
                    label = { Text("Puntos de agenda (separados por salto de línea)") },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 3
                )
                Spacer(modifier = Modifier.height(16.dp))

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    OutlinedButton(onClick = { datePickerDialog.show() }) {
                        Text(if (date.isEmpty()) "Seleccionar Fecha *" else "Fecha: $date")
                    }
                }
                Spacer(modifier = Modifier.height(8.dp))
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    OutlinedButton(onClick = { startTimePickerDialog.show() }) {
                        Text(if (startTime.isEmpty()) "Hora Inicio *" else "Inicio: $startTime")
                    }
                    OutlinedButton(onClick = { endTimePickerDialog.show() }) {
                        Text(if (endTime.isEmpty()) "Hora Fin *" else "Fin: $endTime")
                    }
                }
                Spacer(modifier = Modifier.height(16.dp))

                Text("Modalidad", style = MaterialTheme.typography.titleMedium)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    RadioButton(
                        selected = modality == "presencial",
                        onClick = { modality = "presencial" }
                    )
                    Text("Presencial")
                    Spacer(modifier = Modifier.width(16.dp))
                    RadioButton(
                        selected = modality == "virtual",
                        onClick = { modality = "virtual" }
                    )
                    Text("Virtual")
                }

                if (modality == "presencial") {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Sala", style = MaterialTheme.typography.titleMedium)
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
                                onClick = { selectedRoomId = room.id }
                            )
                            Text("${room.name} (${room.location ?: "Sin ubicación"})")
                        }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))
                Text("Participantes *", style = MaterialTheme.typography.titleMedium)
                if (users.isEmpty()) {
                    Text("No hay usuarios disponibles.", color = MaterialTheme.colorScheme.error)
                }
            }

            items(users) { user ->
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            selectedParticipantIds = if (selectedParticipantIds.contains(user.id)) {
                                selectedParticipantIds - user.id
                            } else {
                                selectedParticipantIds + user.id
                            }
                        }
                        .padding(vertical = 4.dp)
                ) {
                    Checkbox(
                        checked = selectedParticipantIds.contains(user.id),
                        onCheckedChange = { checked ->
                            selectedParticipantIds = if (checked) {
                                selectedParticipantIds + user.id
                            } else {
                                selectedParticipantIds - user.id
                            }
                        }
                    )
                    Column {
                        Text(user.name)
                        Text(user.email, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.secondary)
                    }
                }
            }

            item {
                Spacer(modifier = Modifier.height(24.dp))
                if (errorMessage != null) {
                    Text(text = errorMessage!!, color = MaterialTheme.colorScheme.error)
                    Spacer(modifier = Modifier.height(8.dp))
                }

                if (isSubmitting) {
                    Box(modifier = Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator()
                    }
                } else {
                    Button(
                        onClick = {
                            if (title.isBlank() || objective.isBlank() || date.isBlank() || startTime.isBlank() || endTime.isBlank()) {
                                errorMessage = "Complete los campos obligatorios."
                                return@Button
                            }
                            if (selectedParticipantIds.isEmpty()) {
                                errorMessage = "Debe seleccionar al menos un participante."
                                return@Button
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
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Crear Reunión")
                    }
                }
                Spacer(modifier = Modifier.height(32.dp))
            }
        }
    }
}
