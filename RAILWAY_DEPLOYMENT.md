# Railway Deployment Guide

This guide will help you deploy the Django Auth Service to Railway with PostgreSQL and Redis.

## 🚀 Quick Deployment Steps

### 1. Prepare Your Repository

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Ensure these files are in your repository:**
   - `requirements.txt`
   - `Procfile`
   - `railway.json`
   - `manage.py`
   - `auth_service/` directory
   - `accounts/` directory

### 2. Deploy to Railway

1. **Go to [Railway.app](https://railway.app)**
2. **Sign in with GitHub**
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your repository**
6. **Railway will automatically detect it's a Python project**

### 3. Add PostgreSQL Database

1. **In your Railway project dashboard:**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway will create a PostgreSQL database

2. **Copy the PostgreSQL connection string:**
   - Go to the PostgreSQL service
   - Click "Connect" → "PostgreSQL"
   - Copy the connection string (looks like: `postgresql://user:password@host:port/database`)

### 4. Add Redis Cache

1. **In your Railway project dashboard:**
   - Click "New" → "Database" → "Redis"
   - Railway will create a Redis instance

2. **Copy the Redis connection string:**
   - Go to the Redis service
   - Click "Connect" → "Redis"
   - Copy the connection string (looks like: `redis://user:password@host:port/database`)

### 5. Configure Environment Variables

In your main Django service, go to "Variables" and add these environment variables:

#### Required Environment Variables

```env
# Django Settings
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
DEBUG=False
ALLOWED_HOSTS=your-app-name.railway.app,localhost,127.0.0.1

# Database (from PostgreSQL service)
DATABASE_URL=postgresql://user:password@host:port/database

# Redis (from Redis service)
REDIS_URL=redis://user:password@host:port/database

# Optional: Custom domain (if you have one)
# ALLOWED_HOSTS=your-custom-domain.com,your-app-name.railway.app
```

#### Environment Variable Details

| Variable | Value | Source |
|----------|-------|--------|
| `SECRET_KEY` | Generate a random string | Generate using: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | `False` | Set to False for production |
| `ALLOWED_HOSTS` | Your Railway app domain | Railway provides this automatically |
| `DATABASE_URL` | PostgreSQL connection string | From PostgreSQL service in Railway |
| `REDIS_URL` | Redis connection string | From Redis service in Railway |

### 6. Deploy and Test

1. **Railway will automatically deploy when you push to GitHub**
2. **Check the deployment logs for any errors**
3. **Test your API endpoints:**
   - `https://your-app-name.railway.app/api/accounts/`
   - `https://your-app-name.railway.app/swagger/`
   - `https://your-app-name.railway.app/admin/`

## 🔧 Railway Configuration Files

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn auth_service.wsgi:application --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/api/accounts/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Procfile
```
web: python manage.py migrate && gunicorn auth_service.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## 🛠️ Troubleshooting

### Common Issues

1. **Build Fails:**
   - Check that `requirements.txt` is in the root directory
   - Ensure all dependencies are listed in requirements.txt
   - Check Railway build logs for specific errors

2. **Database Connection Issues:**
   - Verify `DATABASE_URL` is correctly set
   - Ensure PostgreSQL service is running
   - Check that the database user has proper permissions

3. **Redis Connection Issues:**
   - Verify `REDIS_URL` is correctly set
   - Ensure Redis service is running
   - Check Redis connection string format

4. **Static Files Not Loading:**
   - Add `python manage.py collectstatic --noinput` to your Procfile
   - Configure static file serving in Django settings

5. **Rate Limiting Not Working:**
   - Verify `REDIS_URL` is correctly configured
   - Check Redis service is accessible
   - Test Redis connection in Railway logs

### Debugging Commands

You can run these commands in Railway's shell:

```bash
# Check environment variables
env | grep -E "(DATABASE_URL|REDIS_URL|SECRET_KEY)"

# Test database connection
python manage.py dbshell

# Test Redis connection
python -c "import redis; r = redis.from_url('$REDIS_URL'); print(r.ping())"

# Check Django configuration
python manage.py check --deploy

# Run migrations manually
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 📊 Monitoring

### Railway Dashboard
- **Deployments**: Monitor deployment status and logs
- **Metrics**: CPU, memory, and network usage
- **Logs**: Real-time application logs
- **Health Checks**: Automatic health monitoring

### Health Check Endpoint
Your app includes a health check at `/api/accounts/` that Railway uses to monitor the application.

## 🔒 Security Considerations

1. **SECRET_KEY**: Use a strong, random secret key
2. **DEBUG**: Always set to `False` in production
3. **ALLOWED_HOSTS**: Only include your Railway domain and any custom domains
4. **HTTPS**: Railway automatically provides HTTPS
5. **Database**: Railway PostgreSQL is secure by default
6. **Redis**: Railway Redis is secure by default

## 🚀 Post-Deployment

### 1. Create Superuser
```bash
# In Railway shell
python manage.py createsuperuser
```

### 2. Test API Endpoints
```bash
# Test registration
curl -X POST https://your-app-name.railway.app/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Test User", "email": "test@example.com", "password": "testpass123", "password_confirm": "testpass123"}'

# Test login
curl -X POST https://your-app-name.railway.app/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'
```

### 3. Monitor Logs
- Check Railway logs for any errors
- Monitor rate limiting functionality
- Verify database and Redis connections

## 📈 Scaling

Railway automatically scales your application based on traffic. You can also:

1. **Manual Scaling**: Adjust resources in Railway dashboard
2. **Auto-scaling**: Configure automatic scaling rules
3. **Database Scaling**: Upgrade PostgreSQL plan as needed
4. **Redis Scaling**: Upgrade Redis plan as needed

## 💰 Cost Optimization

1. **Development**: Use Railway's free tier for development
2. **Production**: Start with the smallest paid plan
3. **Database**: Choose appropriate PostgreSQL plan
4. **Redis**: Choose appropriate Redis plan
5. **Monitoring**: Use Railway's built-in monitoring tools

## 🔄 Continuous Deployment

Railway automatically deploys when you push to your main branch. To set up:

1. **Connect GitHub repository**
2. **Configure branch for auto-deploy**
3. **Set up environment variables**
4. **Test deployment process**

Your Django Auth Service is now ready for production deployment on Railway!
