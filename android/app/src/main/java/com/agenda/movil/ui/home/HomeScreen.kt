package com.agenda.movil.ui.home

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ExitToApp
import androidx.compose.material.icons.filled.AddCircle
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Email
import androidx.compose.material.icons.filled.Event
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.QrCodeScanner
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.agenda.movil.data.api.ApiClient
import com.agenda.movil.data.local.AuthTokenManager
import com.agenda.movil.data.model.MeetingResponse
import com.agenda.movil.ui.components.EmptyState
import com.agenda.movil.ui.components.LoadingState
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigateToDetail: (Int) -> Unit,
    onLogout: () -> Unit,
    onNavigateToQrScanner: () -> Unit,
    onNavigateToNewMeeting: () -> Unit
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()
    // 0: Agenda, 1: Invitations, 2: Notifications, 3: Profile
    var selectedScreen by remember { mutableStateOf(0) }
    var meetings by remember { mutableStateOf<List<MeetingResponse>>(emptyList()) }
    var invitations by remember { mutableStateOf<List<MeetingResponse>>(emptyList()) }
    var notifications by remember { mutableStateOf<List<com.agenda.movil.data.model.NotificationResponse>>(emptyList()) }
    var isLoading by remember { mutableStateOf(true) }

    // Polling effect every 15 seconds
    LaunchedEffect(selectedScreen) {
        isLoading = true
        while (isActive) {
            try {
                val api = ApiClient.create(context)
                when (selectedScreen) {
                    0 -> {
                        val response = api.getMeetings()
                        if (response.isSuccessful) meetings = response.body()?.data ?: emptyList()
                    }
                    1 -> {
                        val response = api.getInvitations()
                        if (response.isSuccessful) invitations = response.body()?.data ?: emptyList()
                    }
                    2 -> {
                        val response = api.getNotifications()
                        if (response.isSuccessful) notifications = response.body()?.data ?: emptyList()
                    }
                }
            } catch (e: Exception) {
                // Ignore silent background failures
            } finally {
                isLoading = false
            }
            delay(15000)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Text(
                        "Agenda Ecuamatriz", 
                        style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
                        color = MaterialTheme.colorScheme.primary
                    ) 
                },
                actions = {
                    IconButton(onClick = { selectedScreen = 2 }) {
                        BadgedBox(
                            badge = {
                                val unreadCount = notifications.count { !it.isRead }
                                if (unreadCount > 0) {
                                    Badge(containerColor = MaterialTheme.colorScheme.error) { Text("$unreadCount") }
                                }
                            }
                        ) {
                            Icon(Icons.Default.Notifications, contentDescription = "Notificaciones", tint = if (selectedScreen == 2) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.primary
                )
            )
        },
        bottomBar = {
            NavigationBar(
                containerColor = MaterialTheme.colorScheme.surface,
                tonalElevation = 8.dp
            ) {
                NavigationBarItem(
                    selected = selectedScreen == 0,
                    onClick = { selectedScreen = 0 },
                    icon = { Icon(Icons.Default.Event, contentDescription = "Agenda") },
                    label = { Text("Agenda") },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = MaterialTheme.colorScheme.primary,
                        unselectedIconColor = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                )
                NavigationBarItem(
                    selected = selectedScreen == 1,
                    onClick = { selectedScreen = 1 },
                    icon = { Icon(Icons.Default.Email, contentDescription = "Invitaciones") },
                    label = { Text("Invitaciones") }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateToNewMeeting,
                    icon = { Icon(Icons.Default.AddCircle, contentDescription = "Nueva") },
                    label = { Text("Nueva") }
                )
                NavigationBarItem(
                    selected = false,
                    onClick = onNavigateToQrScanner,
                    icon = { Icon(Icons.Default.QrCodeScanner, contentDescription = "Escanear") },
                    label = { Text("Escanear") }
                )
                NavigationBarItem(
                    selected = selectedScreen == 3,
                    onClick = { selectedScreen = 3 },
                    icon = { Icon(Icons.Default.Person, contentDescription = "Perfil") },
                    label = { Text("Perfil") }
                )
            }
        },
        containerColor = MaterialTheme.colorScheme.background
    ) { padding ->
        Column(modifier = Modifier.padding(padding).fillMaxSize()) {
            if (isLoading && meetings.isEmpty() && notifications.isEmpty() && invitations.isEmpty()) {
                LoadingState()
            } else {
                when (selectedScreen) {
                    0 -> AgendaContent(meetings, onNavigateToDetail)
                    1 -> InvitationsContent(invitations, onNavigateToDetail)
                    2 -> NotificationsContent(notifications)
                    3 -> ProfileContent(onLogout = {
                        coroutineScope.launch {
                            try { ApiClient.create(context).logout() } catch (e: Exception) {}
                            AuthTokenManager(context).clearTokens()
                            onLogout()
                        }
                    })
                }
            }
        }
    }
}

@Composable
fun AgendaContent(meetings: List<MeetingResponse>, onNavigateToDetail: (Int) -> Unit) {
    if (meetings.isEmpty()) {
        EmptyState(message = "No tienes reuniones programadas.", icon = Icons.Default.Event)
    } else {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                Text(
                    text = "REUNIONES DE HOY Y PRÓXIMAS",
                    style = MaterialTheme.typography.labelMedium.copy(letterSpacing = 1.sp),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }
            items(meetings) { meeting ->
                MeetingCard(meeting, onClick = { onNavigateToDetail(meeting.id) })
            }
        }
    }
}

@Composable
fun InvitationsContent(invitations: List<MeetingResponse>, onNavigateToDetail: (Int) -> Unit) {
    if (invitations.isEmpty()) {
        EmptyState(message = "No tienes invitaciones pendientes.", icon = Icons.Default.Email)
    } else {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                Text(
                    text = "INVITACIONES PENDIENTES",
                    style = MaterialTheme.typography.labelMedium.copy(letterSpacing = 1.sp),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }
            items(invitations) { meeting ->
                MeetingCard(meeting, onClick = { onNavigateToDetail(meeting.id) }, isInvitation = true)
            }
        }
    }
}

@Composable
fun NotificationsContent(notifications: List<com.agenda.movil.data.model.NotificationResponse>) {
    if (notifications.isEmpty()) {
        EmptyState(message = "No tienes notificaciones.", icon = Icons.Default.Notifications)
    } else {
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            item {
                Text(
                    text = "NOTIFICACIONES RECIENTES",
                    style = MaterialTheme.typography.labelMedium.copy(letterSpacing = 1.sp),
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }
            items(notifications) { note ->
                NotificationCard(note)
            }
        }
    }
}

@Composable
fun ProfileContent(onLogout: () -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(24.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(
                modifier = Modifier.fillMaxWidth().padding(32.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Box(
                    modifier = Modifier.size(100.dp).background(MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.5f), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(Icons.Default.Person, contentDescription = null, modifier = Modifier.size(50.dp), tint = MaterialTheme.colorScheme.primary)
                }
                Spacer(modifier = Modifier.height(24.dp))
                Text("Mi Perfil", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                Spacer(modifier = Modifier.height(8.dp))
                Text("Sesión activa", style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.primary)
                
                Spacer(modifier = Modifier.height(48.dp))
                
                Button(
                    onClick = onLogout,
                    modifier = Modifier.fillMaxWidth().height(56.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer, 
                        contentColor = MaterialTheme.colorScheme.error
                    ),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(Icons.AutoMirrored.Filled.ExitToApp, contentDescription = null)
                    Spacer(modifier = Modifier.width(12.dp))
                    Text("Cerrar Sesión", fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

@Composable
fun MeetingCard(meeting: MeetingResponse, onClick: () -> Unit, isInvitation: Boolean = false) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() },
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Time Indicator Left
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier.width(70.dp).padding(end = 12.dp)
            ) {
                Text(
                    text = meeting.startTime.take(5),
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.primary,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = meeting.date.takeLast(5), // roughly MM-DD
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            // Divider
            Box(modifier = Modifier.width(1.dp).height(40.dp).background(MaterialTheme.colorScheme.outlineVariant))
            
            // Content Right
            Column(modifier = Modifier.weight(1f).padding(start = 12.dp)) {
                Text(
                    text = meeting.title,
                    style = MaterialTheme.typography.bodyLarge,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onSurface,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis
                )
                Spacer(modifier = Modifier.height(4.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    val info = if (meeting.room != null) meeting.room.name else meeting.modality
                    Text(
                        text = info,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis
                    )
                }
                
                if (isInvitation) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "Invitación pendiente",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.error,
                        modifier = Modifier.background(MaterialTheme.colorScheme.errorContainer, RoundedCornerShape(4.dp)).padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun NotificationCard(note: com.agenda.movil.data.model.NotificationResponse) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (note.isRead) MaterialTheme.colorScheme.surface else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        )
    ) {
        Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.Top) {
            Box(
                modifier = Modifier.size(40.dp).background(MaterialTheme.colorScheme.primaryContainer, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(Icons.Default.Notifications, contentDescription = null, tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column {
                Text(text = note.title, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold, color = MaterialTheme.colorScheme.onSurface)
                Spacer(modifier = Modifier.height(4.dp))
                Text(text = note.message, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                if (note.createdAt != null) {
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(text = note.createdAt.take(16).replace("T", " "), style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.outline)
                }
            }
        }
    }
}
