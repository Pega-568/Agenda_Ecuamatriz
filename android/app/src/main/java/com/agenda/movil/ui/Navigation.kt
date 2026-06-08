package com.agenda.movil.ui

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.agenda.movil.ui.auth.LoginScreen
import com.agenda.movil.ui.home.HomeScreen
import com.agenda.movil.ui.meeting.MeetingDetailScreen
import com.agenda.movil.ui.qr.QrScannerScreen

object NavRoutes {
    const val LOGIN = "login"
    const val HOME = "home"
    const val MEETING_DETAIL = "meeting_detail/{id}"
    const val QR_SCANNER = "qr_scanner"

    fun meetingDetail(id: Int) = "meeting_detail/$id"
}

@Composable
fun AgendaNavGraph(
    modifier: Modifier = Modifier,
    navController: NavHostController = rememberNavController(),
    startDestination: String = NavRoutes.LOGIN
) {
    NavHost(
        navController = navController,
        startDestination = startDestination,
        modifier = modifier
    ) {
        composable(NavRoutes.LOGIN) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(NavRoutes.HOME) {
                        popUpTo(NavRoutes.LOGIN) { inclusive = true }
                    }
                }
            )
        }
        composable(NavRoutes.HOME) {
            HomeScreen(
                onNavigateToDetail = { meetingId ->
                    navController.navigate(NavRoutes.meetingDetail(meetingId))
                },
                onLogout = {
                    navController.navigate(NavRoutes.LOGIN) {
                        popUpTo(NavRoutes.HOME) { inclusive = true }
                    }
                },
                onNavigateToQrScanner = {
                    navController.navigate(NavRoutes.QR_SCANNER)
                }
            )
        }
        composable(NavRoutes.MEETING_DETAIL) { backStackEntry ->
            val idStr = backStackEntry.arguments?.getString("id")
            val id = idStr?.toIntOrNull() ?: 0
            MeetingDetailScreen(
                meetingId = id,
                onBack = { navController.popBackStack() }
            )
        }
        composable(NavRoutes.QR_SCANNER) {
            QrScannerScreen(
                onBack = { navController.popBackStack() },
                onScanSuccess = { token ->
                    // Logic to handle token scan
                    navController.popBackStack()
                }
            )
        }
    }
}
