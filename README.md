# Django Auth Service

A comprehensive Django authentication system with JWT tokens, password reset functionality, and PostgreSQL/Redis integration. Built for modern web applications requiring secure user authentication.

##  Live Demo

**Deployment Link:** [Coming Soon - Deploy to Railway/Render]

##  Features

-  **JWT Authentication** - Secure token-based authentication
-  **Custom User Model** - Email-based authentication with full name
-  **Password Reset** - Redis-based token system with 10-minute expiry
-  **PostgreSQL Database** - Robust data storage
-  **Redis Caching** - Fast token storage and session management
-  **Auto API Documentation** - Swagger/OpenAPI integration
-  **Production Ready** - Configured for Railway/Render deployment
-  **Docker Support** - Complete development environment
-  **Rate Limiting** - Protection against brute force attacks
-  **Security First** - Environment variables, password validation, secure tokens

##  Tech Stack

- **Backend**: Django 5.2.5 + Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Authentication**: JWT (Simple JWT)
- **Documentation**: Swagger/OpenAPI (drf-yasg)
- **Deployment**: Gunicorn + Railway/Render
- **Containerization**: Docker + Docker Compose
- **Environment**: python-decouple

##  Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Git
- Docker & Docker Compose (for containerized development)
##  Quick Start

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

3. **Access the Application**
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
   - **ReDoc**: http://localhost:8000/redoc/

##  Docker Development

### Docker Services

The `docker-compose.yml` file sets up three services:

- **web**: Django application
- **db**: PostgreSQL database
- **redis**: Redis cache

### Docker Commands

```bash
# Start all services
docker-compose up

# Start services in background
docker-compose up -d

# Rebuild and start services
docker-compose up --build

# Stop all services
docker-compose down

# View logs
docker-compose logs

# View logs for specific service
docker-compose logs web

# Run Django management commands
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Access database
docker-compose exec db psql -U auth_user -d auth_service

# Access Redis CLI
docker-compose exec redis redis-cli
```

### Docker Environment

The Docker setup uses `env.docker` file with the following configuration:

```env
SECRET_KEY=django-insecure-docker-development-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=auth_service
DB_USER=auth_user
DB_PASSWORD=auth_pass
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/1
```

## 🔧 Environment Variables

Create a `.env` file in the root directory with the following variables:

### Development Configuration

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_NAME=auth_service
DB_USER=auth_user
DB_PASSWORD=auth_pass
DB_HOST=localhost
DB_PORT=5432

# Redis Settings
REDIS_URL=redis://127.0.0.1:6379/1
```

### Production Configuration

```env
# Django Settings
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app,your-app.onrender.com

# Database Settings (Production)
DATABASE_URL=postgresql://user:password@host:port/database

# Redis Settings (Production)
REDIS_URL=redis://user:password@host:port/database
```

### Environment Variables Explanation

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Django secret key for security | Yes | - |
| `DEBUG` | Debug mode (True/False) | Yes | True |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts | Yes | localhost,127.0.0.1 |
| `DATABASE_URL` | PostgreSQL connection string (production) | No* | - |
| `DB_NAME` | Database name (development) | No* | auth_service |
| `DB_USER` | Database user (development) | No* | auth_user |
| `DB_PASSWORD` | Database password (development) | No* | auth_pass |
| `DB_HOST` | Database host (development) | No* | localhost |
| `DB_PORT` | Database port (development) | No* | 5432 |
| `REDIS_URL` | Redis connection string | Yes | redis://127.0.0.1:6379/1 |

*Either `DATABASE_URL` (production) or individual DB variables (development) are required.

##  Rate Limiting

The application implements rate limiting to protect against brute force attacks:

### Rate Limits

- **Login Attempts**: 5 per minute per IP address
- **Password Reset Requests**: 3 per hour per email address
- **General API**: 100 requests per hour for anonymous users, 1000 per hour for authenticated users

### Rate Limit Error Responses

**429 Too Many Requests:**
```json
{
    "error": "Too many login attempts",
    "message": "You have exceeded the limit of 5 login attempts per minute. Please try again later.",
    "retry_after": 60
}
```

**Password Reset Rate Limit:**
```json
{
    "error": "Too many password reset requests",
    "message": "You have exceeded the limit of 3 password reset requests per hour. Please try again later.",
    "retry_after": 3600
}
```

### Rate Limiting Implementation

- **Redis-based**: Uses Redis for fast, distributed rate limiting
- **IP-based**: Login limits are based on IP address
- **Email-based**: Password reset limits are based on email address (hashed for security)
- **Custom Error Messages**: User-friendly error messages with retry information

##  API Documentation

### Base URL
```
http://localhost:8000/api/accounts/
```

### Authentication Endpoints

#### 1. User Registration

**Endpoint:** `POST /api/accounts/register/`

**Request:**
```json
{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123"
}
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### 2. User Login

**Endpoint:** `POST /api/accounts/login/`

**Rate Limited:** 5 attempts per minute per IP

**Request:**
```json
{
    "email": "john@example.com",
    "password": "securepass123"
}
```

**Response (200 OK):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "full_name": "John Doe",
        "email": "john@example.com"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### 3. Token Refresh

**Endpoint:** `POST /api/accounts/token/refresh/`

**Request:**
```json
{
    "refresh": "your_refresh_token_here"
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Password Reset Endpoints

#### 4. Request Password Reset

**Endpoint:** `POST /api/accounts/password/reset/request/`

**Rate Limited:** 3 requests per hour per email

**Request:**
```json
{
    "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
    "message": "Password reset token generated successfully",
    "token": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
    "expires_in": "10 minutes"
}
```

#### 5. Confirm Password Reset

**Endpoint:** `POST /api/accounts/password/reset/confirm/`

**Request:**
```json
{
    "token": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
    "new_password": "newsecurepass123",
    "new_password_confirm": "newsecurepass123"
}
```

**Response (200 OK):**
```json
{
    "message": "Password reset successful"
}
```

### Error Responses

**400 Bad Request:**
```json
{
    "email": ["This field is required."],
    "password": ["This field is required."]
}
```

**401 Unauthorized:**
```json
{
    "detail": "Invalid credentials"
}
```

**429 Too Many Requests:**
```json
{
    "error": "Too many login attempts",
    "message": "You have exceeded the limit of 5 login attempts per minute. Please try again later.",
    "retry_after": 60
}
```

##  Authentication

### JWT Token Usage

Include the access token in the Authorization header:

```http
Authorization: Bearer <your_access_token>
```

### Token Configuration

- **Access Token Lifetime**: 1 hour
- **Refresh Token Lifetime**: 7 days
- **Algorithm**: HS256
- **Token Type**: Bearer

##  Deployment

### Railway Deployment

1. **Connect your GitHub repository to Railway**
2. **Set environment variables in Railway dashboard:**
   - `SECRET_KEY` - Your Django secret key
   - `DEBUG` - Set to `False` for production
   - `ALLOWED_HOSTS` - Your Railway app domain
   - `DATABASE_URL` - Railway PostgreSQL connection string
   - `REDIS_URL` - Railway Redis connection string

3. **Deploy automatically on push to main branch**

### Render Deployment

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service**
3. **Set environment variables:**
   - `SECRET_KEY` - Your Django secret key
   - `DEBUG` - Set to `False` for production
   - `ALLOWED_HOSTS` - Your Render app domain
   - `DATABASE_URL` - Render PostgreSQL connection string
   - `REDIS_URL` - Render Redis connection string

4. **Build Command:** `pip install -r requirements.txt && python3 manage.py migrate`
5. **Start Command:** `gunicorn auth_service.wsgi:application`

##  Project Structure

```
django-auth-service/
├── auth_service/              # Django project settings
│   ├── __init__.py
│   ├── settings.py           # Project settings with PostgreSQL & Redis config
│   ├── urls.py               # Main URL configuration with Swagger
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration
├── accounts/                 # Accounts app
│   ├── models.py             # Custom User model
│   ├── serializers.py        # User registration, login & password reset serializers
│   ├── views.py              # Registration, login & password reset views
│   ├── urls.py               # Account URLs
│   ├── admin.py              # Admin configuration
│   ├── throttling.py         # Rate limiting classes
│   └── exceptions.py         # Custom exception handler
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose services
├── .dockerignore            # Docker ignore file
├── env.example              # Environment variables template
├── env.docker               # Docker environment variables
├── Procfile                  # Production deployment configuration
└── README.md                # This file
```

##  Testing

Run the test suite:

```bash
# Local development
python3 manage.py test

# Docker development
docker-compose exec web python manage.py test
```

##  Security Features

- **JWT Authentication** with access and refresh tokens
- **Password Validation** using Django's built-in validators
- **Secure Token Generation** for password reset
- **Redis-based Token Storage** with automatic expiration
- **Rate Limiting** to prevent brute force attacks
- **Environment Variables** for sensitive configuration
- **HTTPS Ready** for production deployment

