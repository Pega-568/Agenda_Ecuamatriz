package com.agenda.movil.data.api

import com.agenda.movil.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface AgendaApiService {
    
    @POST("/api/auth/login")
    suspend fun login(
        @Body request: LoginRequest
    ): Response<ApiResponse<LoginResponse>>

    @POST("/api/auth/refresh")
    suspend fun refresh(@Header("Authorization") refreshToken: String): Response<ApiResponse<RefreshResponse>>

    @POST("/api/auth/logout")
    suspend fun logout(): Response<ApiResponse<GenericResponse>>

    @POST("/api/auth/devices/register")
    suspend fun registerDevice(@Body request: DeviceRegisterRequest): Response<ApiResponse<GenericResponse>>

    @POST("/api/auth/devices/unregister")
    suspend fun unregisterDevice(@Body request: DeviceRegisterRequest): Response<ApiResponse<GenericResponse>>

    @GET("/api/mobile/meetings")
    suspend fun getMeetings(): Response<ApiResponse<List<MeetingResponse>>>

    @GET("/api/mobile/meetings/options")
    suspend fun getMeetingOptions(): Response<ApiResponse<MeetingOptionsResponse>>

    @POST("/api/mobile/meetings")
    suspend fun createMeeting(@Body request: CreateMeetingRequest): Response<ApiResponse<GenericResponse>>

    @GET("/api/mobile/meetings/today")
    suspend fun getMeetingsToday(): Response<ApiResponse<List<MeetingResponse>>>

    @GET("/api/mobile/meetings/upcoming")
    suspend fun getMeetingsUpcoming(): Response<ApiResponse<List<MeetingResponse>>>

    @GET("/api/mobile/meetings/invitations")
    suspend fun getInvitations(): Response<ApiResponse<List<MeetingResponse>>>

    @GET("/api/mobile/meetings/{id}")
    suspend fun getMeetingDetail(@Path("id") id: Int): Response<ApiResponse<MeetingResponse>>

    @POST("/api/mobile/meetings/{id}/accept")
    suspend fun acceptInvitation(@Path("id") id: Int): Response<ApiResponse<GenericResponse>>

    @POST("/api/mobile/meetings/{id}/reject")
    suspend fun rejectInvitation(
        @Path("id") id: Int,
        @Body request: ActionRequest
    ): Response<ApiResponse<GenericResponse>>

    @POST("/api/mobile/attendance/qr/{token}")
    suspend fun markAttendanceQR(@Path("token") token: String): Response<ApiResponse<GenericResponse>>
}
