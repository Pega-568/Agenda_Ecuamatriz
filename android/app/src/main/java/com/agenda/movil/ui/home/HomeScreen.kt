package com.agenda.movil.ui.home

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ExitToApp
import androidx.compose.material.icons.filled.QrCodeScanner
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.agenda.movil.data.api.ApiClient
import com.agenda.movil.data.local.AuthTokenManager
import com.agenda.movil.data.model.MeetingResponse
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigateToDetail: (Int) -> Unit,
    onLogout: () -> Unit,
    onNavigateToQrScanner: () -> Unit
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    var selectedTabIndex by remember { mutableStateOf(0) }
    var meetings by remember { mutableStateOf<List<MeetingResponse>>(emptyList()) }
    var isLoading by remember { mutableStateOf(true) }

    val tabs = listOf("Hoy", "Próximas", "Invitaciones")

    LaunchedEffect(selectedTabIndex) {
        isLoading = true
        try {
            val api = ApiClient.create(context)
            val response = when (selectedTabIndex) {
                0 -> api.getMeetingsToday()
                1 -> api.getMeetingsUpcoming()
                2 -> api.getInvitations()
                else -> api.getMeetingsToday()
            }
            if (response.isSuccessful) {
                meetings = response.body() ?: emptyList()
            }
        } catch (e: Exception) {
            meetings = emptyList()
        } finally {
            isLoading = false
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Mi Agenda") },
                actions = {
                    IconButton(onClick = onNavigateToQrScanner) {
                        Icon(Icons.Default.QrCodeScanner, contentDescription = "Escanear QR")
                    }
                    IconButton(onClick = {
                        coroutineScope.launch {
                            try {
                                ApiClient.create(context).logout()
                            } catch (e: Exception) {
                                // Ignore
                            }
                            AuthTokenManager(context).clearTokens()
                            onLogout()
                        }
                    }) {
                        Icon(Icons.Default.ExitToApp, contentDescription = "Cerrar sesión")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary,
                    actionIconContentColor = MaterialTheme.colorScheme.onPrimary
                )
            )
        }
    ) { padding ->
        Column(modifier = Modifier.padding(padding)) {
            TabRow(selectedTabIndex = selectedTabIndex) {
                tabs.forEachIndexed { index, title ->
                    Tab(
                        selected = selectedTabIndex == index,
                        onClick = { selectedTabIndex = index },
                        text = { Text(title) }
                    )
                }
            }

            if (isLoading) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            } else if (meetings.isEmpty()) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text("No hay reuniones")
                }
            } else {
                LazyColumn(modifier = Modifier.fillMaxSize()) {
                    items(meetings) { meeting ->
                        MeetingCard(meeting, onClick = { onNavigateToDetail(meeting.id) })
                    }
                }
            }
        }
    }
}

@Composable
fun MeetingCard(meeting: MeetingResponse, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
            .clickable { onClick() },
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = meeting.title, style = MaterialTheme.typography.titleMedium)
            Spacer(modifier = Modifier.height(4.dp))
            Text(text = "${meeting.date} | ${meeting.startTime} - ${meeting.endTime}", style = MaterialTheme.typography.bodyMedium)
            if (meeting.room != null) {
                Text(text = "Sala: ${meeting.room.name}", style = MaterialTheme.typography.bodySmall)
            } else {
                Text(text = "Modalidad: ${meeting.modality}", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}
