package com.agenda.movil.data.model

import com.google.gson.annotations.SerializedName

data class ApiResponse<T>(
    val success: Boolean,
    val message: String?,
    val data: T?,
    val error: ErrorDetail?
)

data class ErrorDetail(
    val message: String,
    val code: String?
)

data class LoginRequest(
    val email: String,
    val password: String
)

data class LoginResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("refresh_token") val refreshToken: String,
    @SerializedName("user") val user: User
)

data class RefreshResponse(
    @SerializedName("access_token") val accessToken: String
)

data class User(
    val id: Int,
    val email: String,
    @SerializedName("first_name") val firstName: String,
    @SerializedName("last_name") val lastName: String,
    val role: String
)

data class DeviceRegisterRequest(
    @SerializedName("device_token") val deviceToken: String,
    val platform: String = "android",
    @SerializedName("device_name") val deviceName: String = "Android Device",
    @SerializedName("app_version") val appVersion: String = "1.0.0"
)

data class MeetingResponse(
    val id: Int,
    val title: String,
    val objective: String,
    val date: String,
    @SerializedName("start_time") val startTime: String,
    @SerializedName("end_time") val endTime: String,
    val modality: String,
    val status: String,
    val room: Room?,
    @SerializedName("invitation_status") val invitationStatus: String?,
    @SerializedName("attendance_status") val attendanceStatus: String?
)

data class Room(
    val id: Int,
    val name: String,
    val location: String?
)

data class ActionRequest(
    val comment: String? = null
)

data class GenericResponse(
    val msg: String
)
