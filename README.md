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

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
git clone https://github.com/Parag1337/HealthBridge.git
cd smart-healthcare-app
python setup.py
```

### Option 2: Manual Setup
```bash
git clone https://github.com/Parag1337/HealthBridge.git
cd smart-healthcare-app
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
# Configure .env file with database credentials
python reset_db.py
python create_test_accounts.py
python run.py
```

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
├── .env                     # Environment configuration
├── .gitignore              # Git ignore rules  
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── setup.py                # Automated setup script
├── create_test_accounts.py # Test account creation utility
├── migrate_db.py           # Database migration script
├── reset_db.py             # Database reset script
├── app/                    # Main application package
│   ├── __init__.py         # Flask app initialization
│   ├── config.py           # Configuration settings
│   ├── models/             # Database models
│   │   ├── __init__.py     # Models package init
│   │   ├── user.py         # User model (patients & doctors)
│   │   ├── appointment.py  # Appointment model
│   │   └── prescription.py # Prescription model
│   ├── routes/             # Route handlers
│   │   ├── __init__.py     # Routes package init
│   │   ├── main.py         # Main/home routes
│   │   ├── auth.py         # Authentication routes
│   │   ├── patient.py      # Patient dashboard routes
│   │   ├── doctor.py       # Doctor dashboard routes
│   │   └── admin.py        # Admin routes (future)
│   ├── static/             # Static assets
│   │   ├── css/            # Stylesheets
│   │   ├── js/             # JavaScript files
│   │   └── images/         # Image assets
│   └── templates/          # Jinja2 HTML templates
│       ├── base.html       # Base template
│       ├── index.html      # Home page
│       ├── about.html      # About page
│       ├── auth/           # Authentication templates
│       ├── patient/        # Patient dashboard templates
│       ├── doctor/         # Doctor dashboard templates
│       └── admin/          # Admin templates (future)
└── tests/                  # Unit tests
    ├── __init__.py         # Tests package init
    ├── test_models.py      # Model tests
    └── test_routes.py      # Route tests
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

## � Recent Updates & Improvements

### ✨ Latest Changes (September 2025)
- **🧹 Project Cleanup**: Removed all unused files and dependencies
- **📁 Optimized Structure**: Streamlined project organization
- **🔧 Fixed Dependencies**: Updated `requirements.txt` with only necessary packages
- **📝 Enhanced Documentation**: Comprehensive setup and usage instructions
- **🚀 Automated Setup**: Added `setup.py` for one-command installation
- **🔒 Security**: Added `.gitignore` to prevent sensitive files from being tracked
- **🐛 Bug Fixes**: Resolved template and import issues
- **✅ Stability**: Improved error handling and user experience

### 🗑️ Removed Unnecessary Files
- `theme/` directory (duplicate templates)
- `instance/` directory (SQLite files, project uses MySQL)
- `migrations` file (empty placeholder)
- `test_auth.py` (temporary testing script)
- `app/utils/` directory (unused utility files)
- `app/routes/appointment.py` and `prescription.py` (unused routes)
- All `__pycache__/` directories

## 🛠️ Development & Architecture

### 🏗️ Application Architecture
- **MVC Pattern**: Clear separation of models, views, and controllers
- **Blueprint System**: Modular route organization
- **Role-Based Access**: Patient/Doctor/Admin role segregation  
- **Database ORM**: SQLAlchemy for database operations
- **Template Engine**: Jinja2 for dynamic HTML generation
- **Authentication**: Flask-Login for session management

### 🔐 Security Features
- **Password Hashing**: Werkzeug security for password protection
- **Session Management**: Secure user sessions with Flask-Login
- **Role-Based Authorization**: Route protection based on user roles
- **CSRF Protection**: Built-in Flask security features
- **Input Validation**: Form validation and sanitization

## 🧪 Testing

### Run Unit Tests
```bash
python -m pytest tests/
```

### Manual Testing Checklist
1. **Registration Flow**: 
   - ✅ Patient registration with personal details
   - ✅ Doctor registration with professional credentials
2. **Authentication**: 
   - ✅ Login/logout functionality
   - ✅ Session persistence
   - ✅ Password validation
3. **Role-Based Access**: 
   - ✅ Patient dashboard access
   - ✅ Doctor dashboard access
   - ✅ Route protection
4. **Appointment Booking**: 
   - ✅ Doctor selection
   - ✅ Date/time booking
   - ✅ Appointment confirmation
5. **Prescription Management**: 
   - ✅ Prescription creation (doctors)
   - ✅ Prescription viewing (patients)

## �🐛 Troubleshooting

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

### Performance Optimizations
- **Database Indexing**: Optimized queries for large datasets
- **Static File Serving**: CDN integration for production
- **Caching**: Redis/Memcached for session storage
- **Load Balancing**: Multiple app instances for high availability

## 📊 Current Status

### ✅ Completed Features
- [x] User authentication and authorization
- [x] Patient registration and profile management
- [x] Doctor registration and profile management  
- [x] Role-based dashboard systems
- [x] Appointment booking system
- [x] Digital prescription management
- [x] Database schema and models
- [x] Responsive web interface
- [x] Security and session management

### 🚧 In Development
- [ ] Admin panel implementation
- [ ] Advanced search and filtering
- [ ] Email notifications
- [ ] Appointment reminders
- [ ] Prescription refill requests

### 🎯 Planned Features
- [ ] Mobile application
- [ ] Video consultation integration
- [ ] AI-powered health insights
- [ ] Pharmacy integration
- [ ] Insurance claim processing
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

## 📈 Project Statistics
- **Total Files**: ~25 core files (cleaned and optimized)
- **Lines of Code**: ~2,000+ (Python, HTML, CSS, JS)
- **Database Tables**: 3 (Users, Appointments, Prescriptions)
- **Routes**: 15+ endpoints
- **Templates**: 10+ responsive HTML templates
- **Test Coverage**: Unit tests for models and routes

---

**🏥 HealthBridge AI - Revolutionizing Healthcare Management**

*Made with ❤️ by developers who care about better healthcare accessibility*

## 🎉 Conclusion
HealthBridge AI represents a modern approach to healthcare management, combining cutting-edge web technologies with intuitive user experience design. The platform successfully bridges the gap between patients and healthcare providers, making medical care more accessible, efficient, and digitally integrated.

**Ready to transform healthcare? Start with HealthBridge AI today!** 🚀