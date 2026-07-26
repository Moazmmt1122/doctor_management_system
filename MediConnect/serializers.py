"""
REST API serializers for the MediConnect application.
"""
from rest_framework import serializers
from .models import CustomUser, DoctorProfile, PatientProfile, TimeSlot, Appointment, Review


# ============================================================
# Serializer 1 — UserSerializer
# ============================================================
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the CustomUser model."""

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'user_type']
        read_only_fields = ['id', 'email']


# ============================================================
# Serializer 2 — DoctorProfileSerializer
# ============================================================
class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for the DoctorProfile model with nested user data."""

    user = UserSerializer(read_only=True)
    avg_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = ['id', 'user', 'specialization', 'experience_years',
                  'consultation_fee', 'clinic_name', 'bio', 'avg_rating', 'total_reviews']

    def get_avg_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return round(sum(r.rating for r in reviews) / len(reviews), 1)
        return 0

    def get_total_reviews(self, obj):
        return obj.reviews.count()


# ============================================================
# Serializer 3 — PatientProfileSerializer
# ============================================================
class PatientProfileSerializer(serializers.ModelSerializer):
    """Serializer for the PatientProfile model with nested user data."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = PatientProfile
        fields = ['id', 'user', 'date_of_birth', 'blood_group', 'address', 'allergies']


# ============================================================
# Serializer 4 — TimeSlotSerializer
# ============================================================
class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for the TimeSlot model."""

    class Meta:
        model = TimeSlot
        fields = ['id', 'doctor', 'start_time', 'end_time']
        read_only_fields = ['id']


# ============================================================
# Serializer 5 — AppointmentSerializer
# ============================================================
class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for the Appointment model with nested references."""

    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'patient_name', 'doctor_name',
                  'appointment_date', 'time_slot', 'status', 'reason', 'fee', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}"

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.first_name} {obj.doctor.user.last_name}"


# ============================================================
# Serializer 6 — ReviewSerializer
# ============================================================
class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for the Review model."""

    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'patient', 'doctor', 'patient_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}"
