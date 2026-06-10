package com.agenda.movil.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val LightColorScheme = lightColorScheme(
    primary = EcuamatrizPrimary,
    secondary = EcuamatrizSecondary,
    tertiary = EcuamatrizSecondary,
    background = EcuamatrizBackground,
    surface = EcuamatrizSurface,
    onPrimary = EcuamatrizSurface,
    onSecondary = EcuamatrizSurface,
    onTertiary = EcuamatrizSurface,
    onBackground = EcuamatrizTextPrimary,
    onSurface = EcuamatrizTextPrimary,
    error = EcuamatrizError,
    outline = EcuamatrizBorder,
    surfaceVariant = EcuamatrizBackground,
    onSurfaceVariant = EcuamatrizTextSecondary
)

@Composable
fun AgendaMovilTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    // Forcing light theme color scheme to maintain corporate identity strictly
    val colorScheme = LightColorScheme

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}
