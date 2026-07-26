from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from datetime import date
from .models import CustomUser, DoctorProfile, PatientProfile, TimeSlot, Appointment, Review
from .forms import SignupForm, DoctorProfileForm, PatientProfileForm, AppointmentForm, ReviewForm, ContactForm


# ============================================================
# AUTHENTICATION VIEWS
# ============================================================

def signup_view(request):
    """Handle user registration for both patients and doctors."""
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Check if email already exists
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'An account with this email already exists.')
                return render(request, 'signup.html', {'form': form})

            # Create the user
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data['phone'],
                user_type=form.cleaned_data['user_type'],
            )

            # Create the appropriate profile
            if user.user_type == 'doctor':
                DoctorProfile.objects.create(user=user)
            else:
                PatientProfile.objects.create(
                    user=user,
                    blood_group=form.cleaned_data.get('blood_group', ''),
                    address=form.cleaned_data.get('address', ''),
                    allergies=form.cleaned_data.get('allergies', '')
                )

            # Log the user in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # Redirect based on user type
            if user.user_type == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


def login_view(request):
    """Handle user login with email and password."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            if user.user_type == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'login.html')


def logout_view(request):
    """Log the user out and redirect to login page."""
    logout(request)
    return redirect('login')


def google_login_callback(request):
    """
    Callback after Google OAuth login via django-allauth.
    Creates a patient profile if this is the user's first social login
    and the profile doesn't exist yet, then redirects to the dashboard.
    """
    user = request.user
    if not user.is_authenticated:
        return redirect('login')

    # If user logged in via Google but has no profile, create one
    if not user.user_type:
        user.user_type = 'patient'
        user.save()

    if user.user_type == 'patient':
        PatientProfile.objects.get_or_create(user=user)
        return redirect('patient_dashboard')
    elif user.user_type == 'doctor':
        DoctorProfile.objects.get_or_create(user=user)
        return redirect('doctor_dashboard')

    return redirect('home')


# ============================================================
# PUBLIC VIEWS
# ============================================================

def home_view(request):
    """Home page showing top rated doctors."""
    doctors = DoctorProfile.objects.all()

    # Calculate average rating for each doctor
    doctor_ratings = []
    for doctor in doctors:
        reviews = doctor.reviews.all()
        if reviews:
            avg_rating = sum([r.rating for r in reviews]) / len(reviews)
        else:
            avg_rating = 0
        doctor_ratings.append({'doctor': doctor, 'avg_rating': round(avg_rating, 1)})

    # Sort by average rating and get top 3
    doctor_ratings.sort(key=lambda x: x['avg_rating'], reverse=True)
    top_doctors = doctor_ratings[:3]

    total_doctors = DoctorProfile.objects.count()
    total_patients = PatientProfile.objects.count()
    total_appointments = Appointment.objects.count()

    return render(request, 'home.html', {
        'top_doctors': top_doctors,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
    })


def doctors_view(request):
    """List all doctors with search and filter functionality."""
    doctors = DoctorProfile.objects.all()

    # Filter by specialization
    specialization = request.GET.get('specialization')
    if specialization:
        doctors = doctors.filter(specialization__icontains=specialization)

    # Search by name
    search = request.GET.get('search')
    if search:
        doctors = doctors.filter(
            user__first_name__icontains=search
        ) | doctors.filter(
            user__last_name__icontains=search
        )

    # Get unique specializations for filter dropdown
    specializations = DoctorProfile.objects.values_list('specialization', flat=True).distinct()
    specializations = [s for s in specializations if s]

    return render(request, 'doctors.html', {
        'doctors': doctors,
        'specializations': specializations,
    })


def doctor_detail_view(request, doctor_id):
    """Show detailed information about a specific doctor."""
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    time_slots = doctor.time_slots.all()
    reviews = doctor.reviews.all()

    # Calculate average rating
    avg_rating = 0
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)

    return render(request, 'doctor_detail.html', {
        'doctor': doctor,
        'time_slots': time_slots,
        'reviews': reviews,
        'avg_rating': avg_rating,
    })


def contact_view(request):
    """Handle contact form submissions."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Message sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


# ============================================================
# PATIENT VIEWS
# ============================================================

def patient_dashboard(request):
    """Dashboard for patient users showing upcoming appointments."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.user_type != 'patient':
        return redirect('home')

    profile = get_object_or_404(PatientProfile, user=request.user)
    upcoming_appointments = Appointment.objects.filter(
        patient=profile,
        status__in=['pending', 'confirmed']
    ).order_by('appointment_date')

    past_appointments = Appointment.objects.filter(
        patient=profile,
        status__in=['cancelled', 'declined']
    ).order_by('-appointment_date')[:5]

    total_appointments = Appointment.objects.filter(patient=profile).count()

    return render(request, 'patient_dashboard.html', {
        'profile': profile,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'total_appointments': total_appointments,
    })


def patient_profile(request):
    """View and edit patient profile information."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.user_type != 'patient':
        return redirect('home')

    profile = get_object_or_404(PatientProfile, user=request.user)

    # Handle profile image removal
    if request.method == 'POST' and 'remove_image' in request.POST:
        if request.user.profile_image:
            request.user.profile_image.delete(save=True)
            messages.success(request, 'Profile image removed.')
        return redirect('patient_profile')

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('patient_profile')
    else:
        form = PatientProfileForm(instance=profile)

    return render(request, 'patient_profile.html', {'form': form, 'profile': profile})


def patient_appointments(request):
    """List all appointments for the logged-in patient."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.user_type != 'patient':
        return redirect('home')

    profile = get_object_or_404(PatientProfile, user=request.user)
    appointments = Appointment.objects.filter(patient=profile).order_by('-appointment_date')

    return render(request, 'patient_appointments.html', {'appointments': appointments})


def book_appointment(request, doctor_id):
    """Book an appointment with a specific doctor."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.user_type != 'patient':
        return redirect('home')

    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    patient = get_object_or_404(PatientProfile, user=request.user)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            appointment.doctor = doctor
            appointment.fee = doctor.consultation_fee
            appointment.status = 'pending'
            appointment.save()
            messages.success(request, 'Appointment booked successfully!')
            return redirect('patient_appointments')
    else:
        form = AppointmentForm()

    return render(request, 'book_appointment.html', {'form': form, 'doctor': doctor})


def cancel_appointment(request, appointment_id):
    """Cancel a patient's appointment."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.user_type != 'patient':
        return redirect('home')

    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'cancelled'
    appointment.save()

    return redirect('patient_appointments')


def submit_review(request, doctor_id):
    """Submit a review for a doctor."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.user_type != 'patient':
        return redirect('home')

    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    patient = get_object_or_404(PatientProfile, user=request.user)

    # Check if already reviewed
    if Review.objects.filter(patient=patient, doctor=doctor).exists():
        messages.error(request, 'You have already reviewed this doctor.')
        return redirect('doctor_detail', doctor_id=doctor.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.patient = patient
            review.doctor = doctor
            review.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('doctor_detail', doctor_id=doctor.id)
    else:
        form = ReviewForm()

    return render(request, 'submit_review.html', {'form': form, 'doctor': doctor})


# ============================================================
# DOCTOR VIEWS
# ============================================================

def doctor_dashboard(request):
    """Dashboard for doctor users showing today's appointments and stats."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.user_type != 'doctor':
        return redirect('home')

    doctor = get_object_or_404(DoctorProfile, user=request.user)
    todays_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=date.today()
    )

    # Calculate average rating
    reviews = doctor.reviews.all()
    if reviews:
        avg_rating = round(sum([r.rating for r in reviews]) / len(reviews), 1)
    else:
        avg_rating = 0

    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    pending_count = Appointment.objects.filter(doctor=doctor, status='pending').count()
    total_patients = Appointment.objects.filter(doctor=doctor).values('patient').distinct().count()

    return render(request, 'doctor_dashboard.html', {
        'doctor': doctor,
        'todays_appointments': todays_appointments,
        'avg_rating': avg_rating,
        'total_appointments': total_appointments,
        'pending_count': pending_count,
        'total_patients': total_patients,
    })


def doctor_profile(request):
    """View and edit doctor profile information."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.user_type != 'doctor':
        return redirect('home')

    doctor = get_object_or_404(DoctorProfile, user=request.user)
    time_slots = doctor.time_slots.all()

    # Handle profile image removal
    if request.method == 'POST' and 'remove_image' in request.POST:
        if request.user.profile_image:
            request.user.profile_image.delete(save=True)
            messages.success(request, 'Profile image removed.')
        return redirect('doctor_profile')

    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('doctor_profile')
    else:
        form = DoctorProfileForm(instance=doctor)

    return render(request, 'doctor_profile.html', {'form': form, 'doctor': doctor, 'time_slots': time_slots})


def doctor_appointments(request):
    """List all appointments for the logged-in doctor."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.user_type != 'doctor':
        return redirect('home')

    doctor = get_object_or_404(DoctorProfile, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date')

    return render(request, 'doctor_appointments.html', {'appointments': appointments})


def confirm_appointment(request, appointment_id):
    """Confirm a pending appointment (doctor action)."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.user_type != 'doctor':
        return redirect('home')

    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'confirmed'
    appointment.save()

    return redirect('doctor_appointments')


def decline_appointment(request, appointment_id):
    """Decline a pending appointment (doctor action)."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.user_type != 'doctor':
        return redirect('home')

    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'declined'
    appointment.save()

    return redirect('doctor_appointments')


def add_time_slot(request):
    """Add a new time slot for the doctor."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.user_type != 'doctor':
        return redirect('home')

    doctor = get_object_or_404(DoctorProfile, user=request.user)

    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        TimeSlot.objects.create(doctor=doctor, start_time=start_time, end_time=end_time)
        messages.success(request, 'Time slot added.')

    return redirect('doctor_profile')


def delete_time_slot(request, slot_id):
    """Delete a time slot."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.user_type != 'doctor':
        return redirect('home')

    slot = get_object_or_404(TimeSlot, id=slot_id)
    slot.delete()

    return redirect('doctor_profile')
