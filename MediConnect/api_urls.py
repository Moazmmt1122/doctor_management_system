"""
REST API URL routes for the MediConnect application.
All endpoints are prefixed with /api/ via the project-level urls.py.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    # Doctor endpoints
    path('doctors/', api_views.DoctorListAPI.as_view(), name='api_doctors'),
    path('doctors/<int:pk>/', api_views.DoctorDetailAPI.as_view(), name='api_doctor_detail'),

    # Time slot endpoints
    path('doctors/<int:doctor_id>/slots/', api_views.TimeSlotListCreateAPI.as_view(), name='api_time_slots'),
    path('slots/<int:pk>/', api_views.TimeSlotDeleteAPI.as_view(), name='api_slot_delete'),

    # Appointment endpoints
    path('appointments/', api_views.AppointmentListCreateAPI.as_view(), name='api_appointments'),
    path('appointments/<int:pk>/', api_views.AppointmentDetailAPI.as_view(), name='api_appointment_detail'),

    # Review endpoints
    path('doctors/<int:doctor_id>/reviews/', api_views.ReviewListCreateAPI.as_view(), name='api_reviews'),

    # Dashboard stats
    path('dashboard/stats/', api_views.dashboard_stats_api, name='api_dashboard_stats'),
]
