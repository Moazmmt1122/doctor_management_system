# MediConnect - Doctor Management System

MediConnect is a comprehensive web application built with Django that helps patients and doctors connect easily. It provides a simple and clean interface for booking appointments, managing schedules, and keeping track of medical histories.

## Features

### For Patients
* **Find Doctors:** Search for doctors by their specialty.
* **Book Appointments:** Pick a convenient time slot and book visits instantly.
* **Health Profile:** Keep your medical information, like blood group and allergies, in one place.
* **Track Visits:** See your upcoming and past appointments easily.
* **Leave Reviews:** Share your experience by leaving reviews for doctors.

### For Doctors
* **Manage Schedule:** Add or remove available time slots for appointments.
* **Dashboard:** See your daily schedule and upcoming visits at a glance.
* **Manage Appointments:** Accept or decline booking requests from patients.
* **Professional Profile:** Showcase your experience, fees, and clinic details.

### Admin Panel
* A fully customized and beautiful admin dashboard to manage users, appointments, and system data easily.

## Technology Stack
* **Backend:** Python and Django
* **Frontend:** HTML, CSS, Bootstrap 5, and JavaScript
* **Database:** SQLite (default)
* **Authentication:** Google OAuth (Login with Google) and standard email login
* **API:** Django REST Framework

## How to Run the Project Locally

1. **Activate Virtual Environment:**
   Make sure your virtual environment is active.
   ```bash
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   Ensure all required packages are installed. (You may need to install `django`, `pillow`, `django-allauth`, `djangorestframework`, `requests`, `PyJWT`, `cryptography` if not already installed).

3. **Run Migrations:**
   Set up the database.
   ```bash
   python manage.py migrate
   ```

4. **Create a Superuser (Optional):**
   To access the admin panel, create an admin account.
   ```bash
   python manage.py shell -c "from MediConnect.models import CustomUser; CustomUser.objects.create_superuser(username='admin', email='administrator@mediconnect.com', password='admin', first_name='Admin', last_name='User')"
   ```

5. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the Application:**
   * Website: `http://127.0.0.1:8000/`
   * Admin Panel: `http://127.0.0.1:8000/admin/`

## Setting up Google Login

To make the "Sign in with Google" button work:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and set up OAuth consent.
3. Create OAuth client ID credentials.
4. Add these two URLs to the **Authorized redirect URIs**:
   * `http://127.0.0.1:8000/accounts/google/login/callback/`
   * `http://localhost:8000/accounts/google/login/callback/`
5. Copy your Client ID and Client Secret into `MyWebsite/settings.py` under `SOCIALACCOUNT_PROVIDERS`.
