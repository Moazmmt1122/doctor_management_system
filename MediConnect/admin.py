from django.contrib import admin
from django.utils.html import format_html
from .models import CustomUser, DoctorProfile, PatientProfile, TimeSlot, Appointment, Review


# ============================================================
# Admin Site Configuration — Professional Branding
# ============================================================
admin.site.site_header = "MediConnect Administration"
admin.site.site_title = "MediConnect Admin"
admin.site.index_title = "Management Dashboard"


# ============================================================
# Inline: TimeSlot inside DoctorProfile
# ============================================================
class TimeSlotInline(admin.TabularInline):
    model = TimeSlot
    extra = 1
    min_num = 0
    verbose_name = "Available Time Slot"
    verbose_name_plural = "Available Time Slots"


# ============================================================
# Inline: Review inside DoctorProfile
# ============================================================
class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['patient', 'rating', 'comment', 'created_at']
    can_delete = False
    verbose_name = "Patient Review"
    verbose_name_plural = "Patient Reviews"
    fk_name = 'doctor'


# ============================================================
# Inline: Appointment inside PatientProfile
# ============================================================
class AppointmentInlinePatient(admin.TabularInline):
    model = Appointment
    extra = 0
    readonly_fields = ['doctor', 'appointment_date', 'time_slot', 'status', 'fee', 'created_at']
    can_delete = False
    verbose_name = "Appointment"
    verbose_name_plural = "Appointment History"
    fk_name = 'patient'


# ============================================================
# CustomUser Admin — Full-Featured
# ============================================================
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email', 'full_name', 'user_type_badge', 'phone', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    list_per_page = 25
    readonly_fields = ['date_joined', 'last_login']

    fieldsets = (
        ('Account Information', {
            'fields': ('email', 'username', 'password'),
        }),
        ('Personal Details', {
            'fields': ('first_name', 'last_name', 'phone', 'user_type', 'profile_image'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Activity', {
            'fields': ('date_joined', 'last_login'),
        }),
    )

    def full_name(self, obj):
        prefix = "Dr. " if obj.user_type == 'doctor' else ""
        return f"{prefix}{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'

    def user_type_badge(self, obj):
        colors = {'doctor': '#2a9d8f', 'patient': '#4361ee'}
        icons = {'doctor': '🩺', 'patient': '🧑'}
        color = colors.get(obj.user_type, '#6c757d')
        icon = icons.get(obj.user_type, '👤')
        return format_html(
            '<span style="background:{}; color:#fff; padding:3px 10px; border-radius:12px; font-size:0.8rem;">{} {}</span>',
            color, icon, obj.get_user_type_display()
        )
    user_type_badge.short_description = 'Type'


# ============================================================
# DoctorProfile Admin — With Inline Slots & Reviews
# ============================================================
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'specialization_badge', 'experience_years', 'fee_display', 'clinic_name', 'slot_count', 'avg_rating_display']
    list_filter = ['specialization', 'experience_years']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'specialization', 'clinic_name']
    ordering = ['-experience_years']
    list_per_page = 20
    inlines = [TimeSlotInline, ReviewInline]

    def get_name(self, obj):
        return f"Dr. {obj.user.first_name} {obj.user.last_name}"
    get_name.short_description = 'Doctor Name'
    get_name.admin_order_field = 'user__first_name'

    def specialization_badge(self, obj):
        if obj.specialization:
            return format_html(
                '<span style="background:#e8f4fd; color:#0d6efd; padding:3px 10px; border-radius:12px; font-size:0.8rem;">{}</span>',
                obj.specialization
            )
        return format_html('<span style="color:#adb5bd;">—</span>')
    specialization_badge.short_description = 'Specialization'

    def fee_display(self, obj):
        return format_html(
            '<span style="color:#2a9d8f; font-weight:600;">Rs. {}</span>', obj.consultation_fee
        )
    fee_display.short_description = 'Fee'

    def slot_count(self, obj):
        count = obj.time_slots.count()
        color = '#2a9d8f' if count > 0 else '#dc3545'
        return format_html(
            '<span style="background:{}; color:#fff; padding:2px 8px; border-radius:10px; font-size:0.8rem;">{}</span>',
            color, count
        )
    slot_count.short_description = 'Slots'

    def avg_rating_display(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            avg = round(sum(r.rating for r in reviews) / len(reviews), 1)
            color = '#f4a261' if avg >= 3 else '#ef476f'
            return format_html(
                '<span style="color:{}; font-weight:600;">⭐ {} / 5</span>', color, avg
            )
        return format_html('<span style="color:#adb5bd;">No reviews</span>')
    avg_rating_display.short_description = 'Rating'


# ============================================================
# PatientProfile Admin — With Appointment History
# ============================================================
@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'blood_group_badge', 'address', 'allergies_display', 'appointment_count']
    list_filter = ['blood_group']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'address']
    ordering = ['user__first_name']
    list_per_page = 25
    inlines = [AppointmentInlinePatient]

    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_name.short_description = 'Patient Name'
    get_name.admin_order_field = 'user__first_name'

    def blood_group_badge(self, obj):
        if obj.blood_group:
            return format_html(
                '<span style="background:#fef2f2; color:#ef476f; padding:3px 10px; border-radius:12px; font-size:0.8rem; font-weight:600;">🩸 {}</span>',
                obj.blood_group
            )
        return format_html('<span style="color:#adb5bd;">—</span>')
    blood_group_badge.short_description = 'Blood Group'

    def allergies_display(self, obj):
        if obj.allergies:
            return format_html(
                '<span style="background:#fff3cd; color:#856404; padding:3px 10px; border-radius:12px; font-size:0.8rem;">⚠️ {}</span>',
                obj.allergies[:50]
            )
        return format_html('<span style="color:#adb5bd;">None</span>')
    allergies_display.short_description = 'Allergies'

    def appointment_count(self, obj):
        count = obj.appointments.count()
        return format_html(
            '<span style="background:#e8f4fd; color:#0d6efd; padding:2px 8px; border-radius:10px; font-size:0.8rem;">{}</span>',
            count
        )
    appointment_count.short_description = 'Appointments'


# ============================================================
# TimeSlot Admin
# ============================================================
@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['get_doctor_name', 'time_range', 'duration_display']
    list_filter = ['doctor__specialization']
    search_fields = ['doctor__user__first_name', 'doctor__user__last_name']
    ordering = ['start_time']
    list_per_page = 30

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.first_name} {obj.doctor.user.last_name}"
    get_doctor_name.short_description = 'Doctor'
    get_doctor_name.admin_order_field = 'doctor__user__first_name'

    def time_range(self, obj):
        return format_html(
            '<span style="background:#f0f9ff; color:#0369a1; padding:4px 12px; border-radius:8px; font-weight:500;">🕐 {} — {}</span>',
            obj.start_time.strftime('%H:%M'), obj.end_time.strftime('%H:%M')
        )
    time_range.short_description = 'Time Range'

    def duration_display(self, obj):
        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), obj.start_time)
        end = datetime.combine(datetime.today(), obj.end_time)
        diff = end - start
        mins = int(diff.total_seconds() / 60)
        return format_html(
            '<span style="color:#6c757d;">{} min</span>', mins
        )
    duration_display.short_description = 'Duration'


# ============================================================
# Appointment Admin — Fully Featured
# ============================================================
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_name', 'doctor_name', 'appointment_date', 'time_slot', 'status', 'fee_display', 'created_at']
    list_filter = ['status', 'appointment_date', 'doctor__specialization']
    search_fields = ['patient__user__first_name', 'patient__user__last_name',
                     'doctor__user__first_name', 'doctor__user__last_name', 'reason']
    date_hierarchy = 'appointment_date'
    ordering = ['-appointment_date', '-created_at']
    list_per_page = 25
    list_editable = ['status']
    readonly_fields = ['created_at']

    def patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}"
    patient_name.short_description = 'Patient'
    patient_name.admin_order_field = 'patient__user__first_name'

    def doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.first_name} {obj.doctor.user.last_name}"
    doctor_name.short_description = 'Doctor'
    doctor_name.admin_order_field = 'doctor__user__first_name'

    def status_badge(self, obj):
        colors = {
            'pending': ('#fff3cd', '#856404', '⏳'),
            'confirmed': ('#d1e7dd', '#0f5132', '✅'),
            'cancelled': ('#e2e3e5', '#41464b', '❌'),
            'declined': ('#f8d7da', '#842029', '🚫'),
        }
        bg, fg, icon = colors.get(obj.status, ('#e2e3e5', '#41464b', '❓'))
        return format_html(
            '<span style="background:{}; color:{}; padding:4px 12px; border-radius:12px; font-size:0.8rem; font-weight:500;">{} {}</span>',
            bg, fg, icon, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def fee_display(self, obj):
        return format_html(
            '<span style="color:#2a9d8f; font-weight:600;">Rs. {}</span>', obj.fee
        )
    fee_display.short_description = 'Fee'


# ============================================================
# Review Admin
# ============================================================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'doctor_name', 'rating_stars', 'comment_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['patient__user__first_name', 'patient__user__last_name',
                     'doctor__user__first_name', 'doctor__user__last_name', 'comment']
    ordering = ['-created_at']
    list_per_page = 25
    readonly_fields = ['created_at']

    def patient_name(self, obj):
        return f"{obj.patient.user.first_name} {obj.patient.user.last_name}"
    patient_name.short_description = 'Patient'

    def doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.first_name} {obj.doctor.user.last_name}"
    doctor_name.short_description = 'Doctor'

    def rating_stars(self, obj):
        filled = '⭐' * obj.rating
        empty = '☆' * (5 - obj.rating)
        return format_html(
            '<span style="letter-spacing:2px;">{}{}</span>', filled, empty
        )
    rating_stars.short_description = 'Rating'

    def comment_preview(self, obj):
        if obj.comment:
            text = obj.comment[:60] + '...' if len(obj.comment) > 60 else obj.comment
            return format_html('<span style="color:#6c757d; font-style:italic;">"{}"</span>', text)
        return format_html('<span style="color:#adb5bd;">No comment</span>')
    comment_preview.short_description = 'Comment'
