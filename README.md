[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

# PSTU Enrollment Automation System (Experimental)

A comprehensive web-based enrollment and result management system built with Django for Patuakhali Science and Technology University (PSTU). This system automates the entire student enrollment process, course management, result generation, and payment processing.

## 🌐 Live Demo

**🚀 Application URL:** [https://pstuenrollment.pythonanywhere.com](https://pstuenrollment.pythonanywhere.com)

The system is live and ready to explore! Jump to [Demo Accounts](#-live-demo--test-accounts) section for login credentials.

---

## 📋 Table of Contents

- [Live Demo](#-live-demo)
- [Overview](#-overview)
- [Features](#-features)
- [System Architecture](#️-system-architecture)
- [Technology Stack](#️-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [Live Demo & Test Accounts](#-live-demo--test-accounts)
- [Project Structure](#-project-structure)
- [Key Models](#-key-models)
- [Security Features](#-security-features)
- [Common Issues and Solutions](#-common-issues-and-solutions)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)
- [Contact](#-contact)

---

## 🎯 Overview

The PSTU Enrollment Automation System is designed to streamline the academic operations of university faculties. It provides separate interfaces for Faculty Administrators, Teachers, and Students, enabling efficient management of courses, enrollments, examinations, and results.

---

## ✨ Features

### 🏛️ Faculty Admin Portal
- **User Management**
  - Add/delete students, teachers, and departments
  - Manage faculty controller accounts
  
- **Course Management**
  - Create and manage courses for different semesters
  - Assign courses to teachers
  - Handle special course assignments for repeat/improvement exams
  
- **Result Management**
  - Calculate semester results automatically
  - Generate result PDFs for all students
  - Create conditional pass and special exam lists
  - Generate merit lists
  
- **Semester Operations**
  - Update exam periods (Regular/F-Removal)
  - Promote students to next semester
  - Manage enrollment fees and costs
  
- **Document Generation**
  - Automated PDF generation for results
  - Merit list reports
  - Special/repeat exam reports

### 👨‍🏫 Teacher Portal
- **Profile Management**
  - Update personal information and profile picture
  - View assigned courses
  
- **Course Management**
  - View regular and special course assignments
  - Enter marks for attendance, assignments, mid-term, and final exams
  
- **Mark Entry**
  - Comprehensive mark entry system
  - Generate course-wise mark sheets in PDF format
  - Handle special/repeat exam marks separately

### 🎓 Student Portal
- **Profile Management**
  - Update personal information and profile picture
  - View academic status and current semester
  
- **Enrollment System**
  - Semester-wise course enrollment
  - View enrolled courses and total credits
  - Real-time cost calculation
  
- **Payment Integration**
  - Integrated SSLCOMMERZ payment gateway
  - Secure online payment processing
  - Payment history tracking
  - Invoice download functionality
  
- **Result Viewing**
  - View semester-wise results
  - Check GPA and CGPA
  - Download result PDFs

---

## 🏗️ System Architecture

The system follows Django's MVT (Model-View-Template) architecture with four main applications:

1. **FacultyApp** - Faculty administration and management
2. **TeacherApp** - Teacher dashboard and mark entry
3. **StudentApp** - Student enrollment and payments
4. **ResultApp** - Result calculation and generation

---

## 🛠️ Technology Stack

- **Backend Framework:** Django 5.1.2
- **Database:** MySQL (via mysqlclient 2.2.4)
- **Frontend:** HTML, CSS, JavaScript (Django Templates)
- **Payment Gateway:** SSLCOMMERZ
- **PDF Generation:** ReportLab 4.2.5
- **Environment Management:** python-dotenv
- **Email:** SMTP (Gmail)
- **Additional Libraries:**
  - Pillow 10.4.0 (Image processing)
  - pytz 2024.2 (Timezone management)
  - requests 2.32.3 (HTTP library)

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- MySQL Server (or XAMPP with MariaDB)
- pip (Python package manager)
- Virtual environment (recommended)
- Git

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Mehedi-Hasan-Rabbi/PSTU-Enrollment-Automation-Experimental.git
cd PSTU-Enrollment-Automation-Experimental
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements. txt
```

### 4. Set Up Database

**Using XAMPP:**
1. Start Apache and MySQL from XAMPP Control Panel
2. Open phpMyAdmin (http://localhost/phpmyadmin)
3. Create a new database named `pstu_enrollment`

**Using MySQL Command Line:**
```sql
CREATE DATABASE pstu_enrollment CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
There is an SQL file in `Document` folder that can be use for demo purposes only.

### 5. Environment Configuration

Create a `.env` file in the root directory by copying `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Security
SECRET_KEY=your-secret-key-here
DEBUG=True    # False for production

# Hosts
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=

# Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=pstu_enrollment
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com

# SSLCOMMERZ Settings
SSLCOMMERZ_STORE_ID=your_store_id
SSLCOMMERZ_PASSWORD=your_password
SSLCOMMERZ_IS_SANDBOX=True
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 8. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

---

## ⚙️ Configuration

### Email Setup (Gmail)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password: 
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
   - Use this password in `EMAIL_HOST_PASSWORD`

### SSLCOMMERZ Setup

1. Register at [SSLCOMMERZ](https://www.sslcommerz.com/)
2. Get your Store ID and Password
3. Set `SSLCOMMERZ_IS_SANDBOX=True` for testing
4. Update credentials in `.env` file

### Database Configuration

The system supports both SQLite (development) and MySQL (production). To switch: 

**For SQLite (Development):**
```python
DATABASES = {
    'default':  {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**For MySQL (Production):** Already configured via `.env` file

---

## 📖 Usage

### Admin Panel

Access the Django admin panel at `http://127.0.0.1:8000/admin/`

- Manage all database models
- Clear cache at `/admin/clearcache/`

### Faculty Admin Portal

URL: `http://127.0.0.1:8000/faculty_admin/login/`

1. Login with Faculty Controller credentials
2. Manage students, teachers, courses, and departments
3. Assign courses to teachers
4. Update exam periods
5. Generate results and reports

### Teacher Portal

URL: `http://127.0.0.1:8000/teacher/login/`

1. Login with teacher credentials
2. View assigned courses
3. Enter student marks
4. Generate mark sheets

### Student Portal

URL: `http://127.0.0.1:8000/student/login/`

1. Login with student credentials
2. Enroll in semester courses
3. Make payments via SSLCOMMERZ
4. View results and download transcripts

---

## 🎮 Live Demo & Test Accounts

**🌐 Live Application:** [https://pstuenrollment.pythonanywhere.com](https://pstuenrollment.pythonanywhere.com)

Experience the full system with these demo accounts: 

| Role | Login URL | Username | Password |
|------|-----------|----------|----------|
| **🔧 Super Admin** | [Admin Panel](https://pstuenrollment.pythonanywhere.com/admin/) | `admin` | `admin` |
| **🏛️ Faculty Admin** | [Faculty Portal](https://pstuenrollment.pythonanywhere.com/faculty_admin/login/) | `cseadmin` | `facultyofcse` |
| **👨‍🏫 Teacher** | [Teacher Portal](https://pstuenrollment.pythonanywhere.com/teacher/login/) | `mahbubur.csit` | `deptofcsit` |
| **🎓 Student** | [Student Portal](https://pstuenrollment.pythonanywhere.com/student/login/) | `mehedi.cse.16` | `studentofcse` |

### 📋 What You Can Test

✅ **Faculty Admin Features:**
- Add/manage courses, teachers, and students
- Assign courses to teachers
- Generate semester results and PDFs
- Promote students to next semester
- Manage enrollment fees

✅ **Teacher Features:**
- View assigned courses
- Enter marks (attendance, assignment, mid-term, final)
- Generate and download mark sheets
- Handle special/repeat exams

✅ **Student Features:**
- Enroll in semester courses
- Make online payments (sandbox mode)
- View payment history and download invoices
- Check results and CGPA
- Download result transcripts

✅ **Payment Testing:**
- Payment gateway is in **sandbox/test mode**
- Use test card: `4111 1111 1111 1111`
- Expiry: Any future date
- CVV: Any 3 digits
- No real money will be charged

### ⚠️ Demo System Notice

> **This is a demonstration environment with sample data.**
>
> - 🔒 Please be respectful and do not delete critical data
> - 💳 All payments are in test mode (no real transactions)
> - 🔄 Database may be reset periodically for maintenance
> - 📧 Email notifications are functional (test emails may be sent)

---

## 📁 Project Structure

```
PSTU-Enrollment-Automation-Experimental/
├── FacultyApp/              # Faculty administration app
│   ├── models.py            # Faculty, Department, Course, Cost models
│   ├── views. py             # Admin dashboard and operations
│   ├── urls.py              # URL routing
│   └── templates/           # Faculty templates
│
├── TeacherApp/              # Teacher portal app
│   ├── models.py            # Teacher, Course_Instructor models
│   ├── views. py             # Teacher dashboard and mark entry
│   ├── urls.py              # URL routing
│   └── templates/           # Teacher templates
│
├── StudentApp/              # Student portal app
│   ├── models.py            # Student, Transaction models
│   ├── views. py             # Student dashboard, enrollment, payment
│   ├── urls. py              # URL routing
│   └── templates/           # Student templates
│
├── ResultApp/               # Result management app
│   ├── models.py            # Course_Mark, Semester_Result models
│   └── views.py             # Result calculation logic
│
├── PSTU_Enrollment/         # Main project directory
│   ├── settings. py          # Project settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi. py              # WSGI configuration
│
├── media/                   # User uploaded files
│   ├── students_profile_pics/
│   └── teachers_profile_pics/
│
├── Documents/               # Project documentation
├── . env. example             # Environment variables template
├── . gitignore               # Git ignore file
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🎯 Key Models

### FacultyApp Models
- `Faculty` - Faculty information
- `FacultyController` - Admin users for faculties
- `Semester` - Semester definitions (1-15)
- `Department` - Department information
- `Course` - Course catalog
- `Cost` - Fee structure

### TeacherApp Models
- `Teacher` - Teacher profiles
- `Course_Instructor` - Regular course assignments
- `Special_Course_Instructor` - Special exam course assignments

### StudentApp Models
- `Student` - Student profiles and enrollment status
- `Student_Transaction` - Payment records

### ResultApp Models
- `Course_Mark` - Individual course marks
- `Semester_Result` - Semester-wise GPA/CGPA
- `Exam_Period` - Exam period configuration
- `Special_Repeat` - Special exam settings

---

## 🔒 Security Features

- Environment-based configuration
- CSRF protection enabled
- Session-based authentication
- Password hashing
- Login required decorators
- Cache control for sensitive pages
- Secure payment gateway integration

---

## 🐛 Common Issues and Solutions

### Issue:  Database Connection Error
**Solution:** Ensure MySQL is running and credentials in `.env` are correct

### Issue: Static Files Not Loading
**Solution:** Run `python manage.py collectstatic` for production

### Issue: Payment Gateway Not Working
**Solution:** Verify SSLCOMMERZ credentials and ensure sandbox mode is set correctly

### Issue: Email Not Sending
**Solution:** Check Gmail app password and enable "Less secure app access"

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Patuakhali Science and Technology University (PSTU)
- Django Documentation
- SSLCOMMERZ Payment Gateway
- All contributors to this project

---

## 👥 Contact

**Mehedi Hasan Rabbi**

- 📧 Email: mehedi.saiyan@gmail.com
- 💼 LinkedIn: [ultr4-instinct](https://www.linkedin.com/in/ultr4-instinct/)
- 🐙 GitHub: [@Mehedi-Hasan-Rabbi](https://github.com/Mehedi-Hasan-Rabbi)

**Project Link:** [https://github.com/Mehedi-Hasan-Rabbi/PSTU-Enrollment-Automation-Experimental](https://github.com/Mehedi-Hasan-Rabbi/PSTU-Enrollment-Automation-Experimental)

---

<div align="center">

⭐ **If you find this project helpful, please consider giving it a star! ** ⭐

Made with ❤️ for PSTU

</div>

---

[contributors-shield]: https://img.shields.io/github/contributors/Mehedi-Hasan-Rabbi/PSTU-Enrollment-Automation-Experimental.svg?style=for-the-badge
[contributors-url]: https://github.com/Mehedi-Hasan-Rabbi/PSTU-Enrollment-Automation-Experimental/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Mehedi-Hasan-Rabbi/PSTU-Enrollment-Automation-Experimental.svg?style=for-the-badge
[forks-url]: https://github.com/Mehedi-Hasan-Rabbi/PSTU-Enrollment-Automation-Experimental/network/members
[stars-shield]: https://img.shields.io/github/stars/Mehedi-Hasan-Rabbi/PSTU-Enrollment-Automation-Experimental.svg?style=for-the-badge
[stars-url]: https://github.com/Mehedi-Hasan-Rabbi/PSTU-Enrollment-Automation-Experimental/stargazers
[issues-shield]: https://img.shields.io/github/issues/Mehedi-Hasan-Rabbi/PSTU-Enrollment-Automation-Experimental.svg?style=for-the-badge
[issues-url]: https://github.com/Mehedi-Hasan-Rabbi/PSTU-Enrollment-Automation-Experimental/issues
[license-shield]: https://img.shields.io/github/license/Mehedi-Hasan-Rabbi/PSTU-Enrollment-Automation-Experimental.svg?style=for-the-badge
[license-url]: https://github.com/Mehedi-Hasan-Rabbi/PSTU-Enrollment-Automation-Experimental/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/ultr4-instinct/