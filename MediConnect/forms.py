from django import forms
from .models import DoctorProfile, PatientProfile, Appointment, Review


# ============================================================
# Form 1 — SignupForm
# ============================================================
class SignupForm(forms.Form):
    """Registration form for new users (patient or doctor)."""

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    user_type = forms.ChoiceField(
        choices=[('patient', 'Patient'), ('doctor', 'Doctor')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    blood_group = forms.CharField(max_length=5, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Blood Group (Optional)'}))
    address = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address (Optional)'}))
    allergies = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Allergies (Optional)'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


# ============================================================
# Form 2 — DoctorProfileForm
# ============================================================
class DoctorProfileForm(forms.ModelForm):
    """Form for editing doctor profile information."""
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'd-none', 'id': 'profileImageInput', 'accept': 'image/*'}))

    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'experience_years', 'consultation_fee', 'clinic_name', 'bio']
        widgets = {
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'clinic_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['phone'].initial = self.instance.user.phone

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', user.first_name)
        user.last_name = self.cleaned_data.get('last_name', user.last_name)
        user.phone = self.cleaned_data.get('phone', user.phone)
        if self.cleaned_data.get('profile_image'):
            user.profile_image = self.cleaned_data['profile_image']
        if commit:
            user.save()
            profile.save()
        return profile


# ============================================================
# Form 3 — PatientProfileForm
# ============================================================
class PatientProfileForm(forms.ModelForm):
    """Form for editing patient profile information."""
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'd-none', 'id': 'profileImageInput', 'accept': 'image/*'}))

    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'blood_group', 'address', 'allergies']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'allergies': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['phone'].initial = self.instance.user.phone

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', user.first_name)
        user.last_name = self.cleaned_data.get('last_name', user.last_name)
        user.phone = self.cleaned_data.get('phone', user.phone)
        if self.cleaned_data.get('profile_image'):
            user.profile_image = self.cleaned_data['profile_image']
        if commit:
            user.save()
            profile.save()
        return profile


# ============================================================
# Form 4 — AppointmentForm
# ============================================================
class AppointmentForm(forms.ModelForm):
    """Form for booking an appointment."""

    class Meta:
        model = Appointment
        fields = ['appointment_date', 'time_slot', 'reason']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_slot': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 09:00 - 09:30'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for visit'}),
        }


# ============================================================
# Form 5 — ReviewForm
# ============================================================
class ReviewForm(forms.ModelForm):
    """Form for submitting a review for a doctor."""

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')],
                attrs={'class': 'form-select'}
            ),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your review...'}),
        }


# ============================================================
# Form 6 — ContactForm
# ============================================================
class ContactForm(forms.Form):
    """Contact form for general inquiries."""

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'})
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Your Message'})
    )
