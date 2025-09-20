# HealthBridge AI - Smart Healthcare Application

## 🏥 Introduction
HealthBridge AI is a comprehensive healthcare platform that bridges the gap between patients and doctors through intelligent automation. The platform provides seamless appointment booking, digital prescription management, and role-based dashboards for both patients and healthcare providers.

## ✨ Features

### 👥 User Management
- **Secure Authentication**: Role-based login system for patients and doctors
- **User Registration**: Separate registration flows with role-specific fields
- **Profile Management**: Complete user profiles with medical information

### 🗓️ Appointment System
- **Smart Booking**: Patients can book appointments with available doctors
- **Schedule Management**: Doctors can view and manage their appointment schedules
- **Real-time Updates**: Appointment status tracking and notifications

### 💊 Prescription Management
- **Digital Prescriptions**: Electronic prescription creation and management
- **Patient Access**: Patients can view their prescription history
- **Doctor Tools**: Comprehensive prescription management for healthcare providers

### 🎛️ Role-Based Dashboards
- **Patient Dashboard**: Appointments, prescriptions, and health overview
- **Doctor Dashboard**: Patient management, appointments, and prescription tools
- **Admin Panel**: User management and system administration

## 🛠️ Technology Stack
- **Backend**: Python 3.x, Flask Framework
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Flask-Login with password hashing
- **Styling**: Custom CSS with dark theme design

## 📋 Prerequisites

Before running this application, make sure you have the following installed:

- **Python 3.8+** (Download from [python.org](https://python.org))
- **MySQL 8.0+** (Download from [mysql.com](https://mysql.com))
- **Git** (Download from [git-scm.com](https://git-scm.com))

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Parag1337/HealthBridge.git
cd smart-healthcare-app
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### MySQL Configuration
1. **Create Database**:
   ```sql
   CREATE DATABASE healthbridge_db;
   ```

2. **Create `.env` file** in the project root:
   ```env
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=3306
   DB_USERNAME=your_mysql_username
   DB_PASSWORD=your_mysql_password
   DB_NAME=healthbridge_db
   
   # Flask Configuration
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=development
   ```

#### Initialize Database Schema
```bash
# Reset database with fresh schema (WARNING: This deletes existing data)
python reset_db.py

# Or migrate existing database
python migrate_db.py
```

### 5. Create Test Accounts (Optional)
```bash
python create_test_accounts.py
```

## 🏃‍♂️ Running the Application

### Start the Flask Server
```bash
python run.py
```

The application will be available at: **http://127.0.0.1:5000**

### Default Test Accounts
After running `create_test_accounts.py`, you can use these credentials:

| Role | Email | Password |
|------|-------|----------|
| Patient | `testpatient@demo.com` | `demo123` |
| Doctor | `testdoctor@demo.com` | `demo123` |
| Sample Doctor | `doctor@healthbridge.com` | `doctor123` |

## 📁 Project Structure
```
smart-healthcare-app/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── config.py            # Configuration settings
│   ├── models/              # Database models
│   │   ├── user.py          # User model (patients & doctors)
│   │   ├── appointment.py   # Appointment model
│   │   └── prescription.py  # Prescription model
│   ├── routes/              # Route handlers
│   │   ├── auth.py          # Authentication routes
│   │   ├── patient.py       # Patient-specific routes
│   │   ├── doctor.py        # Doctor-specific routes
│   │   └── main.py          # Main application routes
│   ├── static/              # Static files (CSS, JS, images)
│   └── templates/           # Jinja2 templates
├── migrations/              # Database migration files
├── tests/                   # Unit tests
├── requirements.txt         # Python dependencies
├── run.py                  # Application entry point
├── reset_db.py             # Database reset script
├── migrate_db.py           # Database migration script
└── create_test_accounts.py # Test account creation
```

## 🔧 Usage Guide

### For Patients
1. **Registration**: Navigate to `/auth/register` and select "Patient Registration"
2. **Login**: Use the patient login tab with your credentials
3. **Dashboard**: View appointments, prescriptions, and health overview
4. **Book Appointments**: Select doctors and available time slots
5. **View Prescriptions**: Access your digital prescription history

### For Doctors
1. **Registration**: Navigate to `/auth/register` and select "Doctor Registration"
2. **Login**: Use the doctor login tab with your credentials
3. **Dashboard**: Manage appointments and view patient statistics
4. **Patient Management**: View patient lists and appointment schedules
5. **Prescriptions**: Create and manage digital prescriptions

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Error
```
sqlalchemy.exc.OperationalError: (MySQLdb.OperationalError) (2003, "Can't connect to MySQL server")
```
**Solution**: 
- Verify MySQL is running
- Check database credentials in `.env` file
- Ensure database `healthbridge_db` exists

#### Missing Columns Error
```
sqlalchemy.exc.OperationalError: (1054, "Unknown column 'users.emergency_contact' in 'field list'")
```
**Solution**:
```bash
python reset_db.py  # WARNING: This will delete all data
```

#### Template Not Found Error
```
jinja2.exceptions.TemplateNotFound: 'patient/dashboard.html'
```
**Solution**: Ensure all template files exist in the correct directory structure

#### Permission Denied
```
Access denied. Patients only.
```
**Solution**: Make sure you're logged in with the correct user role

### Development Mode
```bash
# Enable debug mode for development
export FLASK_ENV=development  # Linux/macOS
set FLASK_ENV=development     # Windows
python run.py
```

## 🧪 Testing

### Run Unit Tests
```bash
python -m pytest tests/
```

### Manual Testing
1. **Registration Flow**: Test both patient and doctor registration
2. **Authentication**: Verify login/logout functionality
3. **Role-Based Access**: Ensure proper dashboard redirections
4. **Appointment Booking**: Test the complete booking workflow
5. **Prescription Management**: Test prescription creation and viewing

## 🚀 Deployment

### Production Considerations
1. **Environment Variables**: Set production values in `.env`
2. **Database**: Use production MySQL instance
3. **Secret Key**: Generate secure random secret key
4. **WSGI Server**: Use Gunicorn or uWSGI instead of Flask dev server

### Example Production Setup
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:8000 run:app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Support

For support and questions:
- **Email**: support@healthbridge.ai
- **Issues**: [GitHub Issues](https://github.com/Parag1337/HealthBridge/issues)
- **Documentation**: [Wiki](https://github.com/Parag1337/HealthBridge/wiki)

## 🎯 Future Enhancements
- Integration with wearable health devices for live monitoring
- Voice-based chatbot interaction
- Predictive analytics for disease risk based on medical history
- Mobile application development
- Telemedicine video consultation features
- AI-powered diagnosis assistance
- Integration with pharmacy systems
- Real-time notification system

---

**Made with ❤️ for better healthcare management**

## Conclusion
The Smart Doctor-Patient Appointment & Prescription Assistant aims to revolutionize patient care through intelligent automation, making healthcare more accessible, efficient, and personalized.