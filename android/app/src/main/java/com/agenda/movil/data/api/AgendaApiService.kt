package com.agenda.movil.data.api

import com.agenda.movil.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface AgendaApiService {
    
    @FormUrlEncoded
    @POST("/api/auth/login")
    suspend fun login(
        @Field("email") email: String,
        @Field("password") password: String
    ): Response<LoginResponse>

    @POST("/api/auth/refresh")
    suspend fun refresh(): Response<RefreshResponse>

    @POST("/api/auth/logout")
    suspend fun logout(): Response<GenericResponse>

    @POST("/api/auth/devices/register")
    suspend fun registerDevice(@Body request: DeviceRegisterRequest): Response<GenericResponse>

    @POST("/api/auth/devices/unregister")
    suspend fun unregisterDevice(@Body request: DeviceRegisterRequest): Response<GenericResponse>

    @GET("/api/mobile/meetings/today")
    suspend fun getMeetingsToday(): Response<List<MeetingResponse>>

    @GET("/api/mobile/meetings/upcoming")
    suspend fun getMeetingsUpcoming(): Response<List<MeetingResponse>>

    @GET("/api/mobile/meetings/invitations")
    suspend fun getInvitations(): Response<List<MeetingResponse>>

    @GET("/api/mobile/meetings/{id}")
    suspend fun getMeetingDetail(@Path("id") id: Int): Response<MeetingResponse>

    @POST("/api/mobile/meetings/{id}/accept")
    suspend fun acceptInvitation(@Path("id") id: Int): Response<GenericResponse>

    @POST("/api/mobile/meetings/{id}/reject")
    suspend fun rejectInvitation(
        @Path("id") id: Int,
        @Body request: ActionRequest
    ): Response<GenericResponse>

    @POST("/api/mobile/attendance/qr/{token}")
    suspend fun markAttendanceQR(@Path("token") token: String): Response<GenericResponse>
}
