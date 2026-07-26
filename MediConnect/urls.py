from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('google/callback/', views.google_login_callback, name='google_login_callback'),

    # Public
    path('doctors/', views.doctors_view, name='doctors'),
    path('doctors/<int:doctor_id>/', views.doctor_detail_view, name='doctor_detail'),
    path('contact/', views.contact_view, name='contact'),

    # Patient
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/profile/', views.patient_profile, name='patient_profile'),
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path('patient/book/<int:doctor_id>/', views.book_appointment, name='book_appointment'),
    path('patient/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('patient/review/<int:doctor_id>/', views.submit_review, name='submit_review'),

    # Doctor
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/confirm/<int:appointment_id>/', views.confirm_appointment, name='confirm_appointment'),
    path('doctor/decline/<int:appointment_id>/', views.decline_appointment, name='decline_appointment'),
    path('doctor/slot/add/', views.add_time_slot, name='add_time_slot'),
    path('doctor/slot/delete/<int:slot_id>/', views.delete_time_slot, name='delete_time_slot'),
]
