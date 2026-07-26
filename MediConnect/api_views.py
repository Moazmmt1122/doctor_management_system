"""
REST API views for the MediConnect application.
Provides CRUD endpoints for doctors, appointments, time slots, and reviews.
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import DoctorProfile, PatientProfile, TimeSlot, Appointment, Review
from .serializers import (
    DoctorProfileSerializer, PatientProfileSerializer,
    TimeSlotSerializer, AppointmentSerializer, ReviewSerializer,
)


# ============================================================
# API View 1 — Doctor List API
# ============================================================
class DoctorListAPI(generics.ListAPIView):
    """List all doctors. Supports search by specialization."""

    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = DoctorProfile.objects.all()
        specialization = self.request.query_params.get('specialization')
        search = self.request.query_params.get('search')
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)
        if search:
            queryset = queryset.filter(
                user__first_name__icontains=search
            ) | queryset.filter(
                user__last_name__icontains=search
            )
        return queryset


# ============================================================
# API View 2 — Doctor Detail API
# ============================================================
class DoctorDetailAPI(generics.RetrieveAPIView):
    """Retrieve a single doctor's profile."""

    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.AllowAny]


# ============================================================
# API View 3 — Time Slot List/Create API
# ============================================================
class TimeSlotListCreateAPI(generics.ListCreateAPIView):
    """List and create time slots for a doctor."""

    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        doctor_id = self.kwargs.get('doctor_id')
        if doctor_id:
            return TimeSlot.objects.filter(doctor_id=doctor_id)
        if hasattr(self.request.user, 'doctorprofile'):
            return TimeSlot.objects.filter(doctor=self.request.user.doctorprofile)
        return TimeSlot.objects.none()

    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user.doctorprofile)


# ============================================================
# API View 4 — Time Slot Delete API
# ============================================================
class TimeSlotDeleteAPI(generics.DestroyAPIView):
    """Delete a time slot."""

    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]


# ============================================================
# API View 5 — Appointment List/Create API
# ============================================================
class AppointmentListCreateAPI(generics.ListCreateAPIView):
    """List and create appointments."""

    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'doctor':
            return Appointment.objects.filter(doctor__user=user)
        elif user.user_type == 'patient':
            return Appointment.objects.filter(patient__user=user)
        return Appointment.objects.none()


# ============================================================
# API View 6 — Appointment Detail API
# ============================================================
class AppointmentDetailAPI(generics.RetrieveUpdateAPIView):
    """Retrieve or update an appointment (e.g. status change)."""

    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]


# ============================================================
# API View 7 — Review List/Create API
# ============================================================
class ReviewListCreateAPI(generics.ListCreateAPIView):
    """List and create reviews for a doctor."""

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        doctor_id = self.kwargs.get('doctor_id')
        if doctor_id:
            return Review.objects.filter(doctor_id=doctor_id)
        return Review.objects.all()


# ============================================================
# API View 8 — Dashboard Stats API
# ============================================================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats_api(request):
    """Return dashboard statistics for the current user."""

    user = request.user

    if user.user_type == 'doctor':
        from datetime import date
        doctor = DoctorProfile.objects.get(user=user)
        total = Appointment.objects.filter(doctor=doctor).count()
        today = Appointment.objects.filter(doctor=doctor, appointment_date=date.today()).count()
        pending = Appointment.objects.filter(doctor=doctor, status='pending').count()
        reviews = doctor.reviews.all()
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else 0

        return Response({
            'total_appointments': total,
            'todays_appointments': today,
            'pending_appointments': pending,
            'avg_rating': avg_rating,
            'total_reviews': len(reviews),
        })

    elif user.user_type == 'patient':
        patient = PatientProfile.objects.get(user=user)
        total = Appointment.objects.filter(patient=patient).count()
        upcoming = Appointment.objects.filter(
            patient=patient, status__in=['pending', 'confirmed']
        ).count()

        return Response({
            'total_appointments': total,
            'upcoming_appointments': upcoming,
        })

    return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)
