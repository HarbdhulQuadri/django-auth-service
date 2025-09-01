# Django Auth Service

A comprehensive Django authentication system with JWT tokens, password reset functionality, PostgreSQL/Redis integration, and production deployment. Built for modern web applications requiring secure user authentication.

## 🚀 Live Demo

**Deployment Link:** [https://web-production-641f.up.railway.app/](https://web-production-641f.up.railway.app/)

- **API Endpoints:** https://web-production-641f.up.railway.app/api/accounts/
- **Swagger Documentation:** https://web-production-641f.up.railway.app/swagger/
- **ReDoc Documentation:** https://web-production-641f.up.railway.app/redoc/

## ✨ Features

- **JWT Authentication** - Secure token-based authentication
- **Custom User Model** - Email-based authentication with full name
- **Password Reset** - Redis-based token system with 10-minute expiry
- **PostgreSQL Database** - Robust data storage
- **Redis Caching** - Fast token storage and session management
- **Auto API Documentation** - Swagger/OpenAPI integration
- **Production Ready** - Configured for Railway/Render deployment
- **Docker Support** - Complete development environment
- **Rate Limiting** - Protection against brute force attacks
- **Comprehensive Testing** - Unit tests for all functionality
- **Security First** - Environment variables, password validation, secure tokens

## 🛠️ Tech Stack

- **Backend**: Django 5.2.5 + Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Authentication**: JWT (Simple JWT)
- **Documentation**: Swagger/OpenAPI (drf-yasg)
- **Deployment**: Gunicorn + Railway/Render
- **Containerization**: Docker + Docker Compose
- **Environment**: python-decouple
- **Testing**: Django Test Framework

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Git
- Docker & Docker Compose (for containerized development)

## 🚀 Quick Start

### Option 1: Docker Development (Recommended)

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd django-auth-service
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Run Migrations (in a new terminal)**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Create Superuser (optional)**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the Application**
   - **API**: http://localhost:8000/api/accounts/
   - **Admin**: http://localhost:8000/admin/
   - **Swagger Docs**: http://localhost:8000/swagger/
   - **ReDoc**: http://localhost:8000/redoc/

### Option 2: Local Development

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd django-auth-service
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   ```bash
   cp env.example .env
   # Edit .env with your database and Redis credentials
   ```

5. **Database Setup**
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   python3 manage.py createsuperuser
   ```

6. **Run the Server**
   ```bash
   python3 manage.py runserver
   ```

7. **Access the Application**
   - **API**: http://localhost:8000/api/accounts/
   - **Admin**: http://localhost:8000/admin/
   - **Swagger Docs**: http://localhost:8000/swagger/

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python manage.py test

# Run specific test classes
python manage.py test accounts.tests.UserRegistrationTest
python manage.py test accounts.tests.UserLoginTest
python manage.py test accounts.tests.PasswordResetTest
python manage.py test accounts.tests.RateLimitingTest

# With Docker
docker-compose exec web python manage.py test
```

## 🔧 Environment Variables

Create a `.env` file based on `env.example`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings (Development)
DB_NAME=auth_service
DB_USER=auth_user
DB_PASSWORD=auth_pass
DB_HOST=localhost
DB_PORT=5432

# Redis Settings
REDIS_URL=redis://127.0.0.1:6379/1

# Production Settings (Railway/Render)
# DATABASE_URL=postgresql://user:password@host:port/database
# REDIS_URL=redis://user:password@host:port/database
# DEBUG=False
# ALLOWED_HOSTS=your-app.railway.app,your-app.onrender.com
```

## 📚 API Endpoints

### Authentication Endpoints

| Endpoint | Method | Description | Rate Limit |
|----------|--------|-------------|------------|
| `/api/accounts/register/` | POST | Register new user | None |
| `/api/accounts/login/` | POST | User login | 5/minute per IP |
| `/api/accounts/token/refresh/` | POST | Refresh JWT token | None |

### Password Reset Endpoints

| Endpoint | Method | Description | Rate Limit |
|----------|--------|-------------|------------|
| `/api/accounts/password/reset/request/` | POST | Request reset token | 3/hour per email |
| `/api/accounts/password/reset/confirm/` | POST | Confirm password reset | None |

### Example Requests

#### Register User
```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123"
  }'
```

#### Login User
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

#### Request Password Reset
```bash
curl -X POST http://localhost:8000/api/accounts/password/reset/request/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com"
  }'
```

#### Confirm Password Reset
```bash
curl -X POST http://localhost:8000/api/accounts/password/reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "new_password": "newsecurepass123",
    "new_password_confirm": "newsecurepass123"
  }'
```

## 🔐 JWT Configuration

The application uses JWT tokens for authentication:

- **Access Token Lifetime**: 1 hour
- **Refresh Token Lifetime**: 7 days
- **Token Rotation**: Enabled
- **Blacklist After Rotation**: Enabled

Include the access token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## 🔄 Password Reset Flow

1. **Request Reset**: User requests password reset with email
2. **Token Generation**: System generates 32-character secure token
3. **Redis Storage**: Token stored in Redis with 10-minute expiry
4. **Token Delivery**: Token returned to user (in production, send via email)
5. **Password Update**: User confirms reset with token and new password
6. **Token Cleanup**: Token deleted from Redis after successful reset

## 🚀 Deployment

### Railway Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Create Railway Project**
   - Connect your GitHub repository
   - Add PostgreSQL service
   - Add Redis service

3. **Configure Environment Variables**
   ```
   DEBUG=False
   DATABASE_URL=<railway-postgresql-url>
   REDIS_URL=<railway-redis-url>
   SECRET_KEY=<your-secret-key>
   ALLOWED_HOSTS=your-app.railway.app,.railway.app
   ```

4. **Deploy**
   - Railway will automatically deploy on push
   - Monitor deployment logs

### Render Deployment

1. **Create Render Account**
2. **Connect GitHub Repository**
3. **Configure Environment Variables**
4. **Set Build Command**: `pip install -r requirements.txt`
5. **Set Start Command**: `gunicorn auth_service.wsgi:application`

## 📁 Project Structure

```
django-auth-service/
├── accounts/                 # Main app
│   ├── migrations/          # Database migrations
│   ├── __init__.py
│   ├── admin.py            # Admin configuration
│   ├── apps.py             # App configuration
│   ├── exceptions.py       # Custom exception handler
│   ├── models.py           # Custom User model
│   ├── serializers.py      # DRF serializers
│   ├── tests.py            # Comprehensive test suite
│   ├── throttling.py       # Rate limiting classes
│   ├── urls.py             # URL patterns
│   └── views.py            # API views
├── auth_service/           # Project settings
│   ├── __init__.py
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── staticfiles/            # Static files
├── .dockerignore           # Docker ignore file
├── .gitignore              # Git ignore file
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker configuration
├── env.example             # Environment variables template
├── manage.py               # Django management script
├── Procfile                # Railway deployment configuration
├── railway.json            # Railway configuration
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
└── runtime.txt             # Python runtime version
```

## 🧪 Testing Coverage

The test suite covers:

- **User Model Tests**
  - User creation with valid data
  - Superuser creation
  - String representation

- **Registration Tests**
  - Valid registration
  - Invalid email format
  - Mismatched passwords
  - Duplicate email
  - Weak password

- **Login Tests**
  - Valid credentials
  - Invalid email
  - Invalid password
  - Inactive user

- **Password Reset Tests**
  - Valid reset request
  - Invalid email format
  - Non-existent email
  - Valid token confirmation
  - Invalid token
  - Mismatched passwords
  - Token expiry

- **Rate Limiting Tests**
  - Login rate limiting (5/minute)
  - Password reset rate limiting (3/hour)

## 🔒 Security Features

- **JWT Authentication** - Secure token-based auth
- **Password Validation** - Django's built-in validators
- **Rate Limiting** - Protection against brute force
- **Environment Variables** - Secure configuration
- **HTTPS Only** - Production security headers
- **CSRF Protection** - Cross-site request forgery protection
- **XSS Protection** - Cross-site scripting protection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

Built as part of the Django Authentication System internship task for Bill Station.

---

**Ready for production deployment with comprehensive testing and documentation!** 🚀

