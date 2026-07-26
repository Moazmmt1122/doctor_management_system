from django.db import models
from django.contrib.auth.models import AbstractUser


# ============================================================
# Model 1 — CustomUser (extends AbstractUser)
# ============================================================
class CustomUser(AbstractUser):
    """Custom user model that uses email for login instead of username."""

    USER_TYPE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='patient')
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ============================================================
# Model 2 — DoctorProfile
# ============================================================
class DoctorProfile(models.Model):
    """Profile for doctor users with specialization and fee info."""

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(default=0)
    consultation_fee = models.IntegerField(default=0)
    clinic_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"


# ============================================================
# Model 3 — PatientProfile
# ============================================================
class PatientProfile(models.Model):
    """Profile for patient users with medical info."""

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    address = models.CharField(max_length=200, blank=True)
    allergies = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


# ============================================================
# Model 4 — TimeSlot
# ============================================================
class TimeSlot(models.Model):
    """A time slot that belongs to a doctor."""

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='time_slots')
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


# ============================================================
# Model 5 — Appointment
# ============================================================
class Appointment(models.Model):
    """A booking between a patient and a doctor."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('declined', 'Declined'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=30)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True)
    fee = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-appointment_date']

    def __str__(self):
        return f"{self.patient.user.first_name} → Dr. {self.doctor.user.first_name} on {self.appointment_date}"


# ============================================================
# Model 6 — Review
# ============================================================
class Review(models.Model):
    """A patient's review for a doctor."""

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='reviews')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'doctor')

    def __str__(self):
        return f"{self.patient.user.first_name} → Dr. {self.doctor.user.first_name} ({self.rating}/5)"
