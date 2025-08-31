# Railway Deployment Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. Healthcheck Failing

**Problem**: Healthcheck fails with "service unavailable"

**Solutions**:
1. **Check Environment Variables**:
   ```bash
   # In Railway shell, verify these are set:
   echo $SECRET_KEY
   echo $DATABASE_URL
   echo $REDIS_URL
   echo $DEBUG
   echo $ALLOWED_HOSTS
   ```

2. **Required Environment Variables**:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.railway.app,localhost,127.0.0.1
   DATABASE_URL=postgresql://user:password@host:port/database
   REDIS_URL=redis://user:password@host:port/database
   ```

3. **Check Application Logs**:
   - Go to Railway dashboard
   - Click on your Django service
   - Check "Deployments" tab for error logs

### 2. Database Connection Issues

**Problem**: Cannot connect to PostgreSQL

**Solutions**:
1. **Verify DATABASE_URL**:
   - Go to PostgreSQL service in Railway
   - Copy the connection string from "Connect" → "PostgreSQL"
   - Ensure it's set in your Django service environment variables

2. **Test Database Connection**:
   ```bash
   # In Railway shell
   python manage.py dbshell
   ```

3. **Check Database Service**:
   - Ensure PostgreSQL service is running
   - Check if database is accessible

### 3. Redis Connection Issues

**Problem**: Cannot connect to Redis

**Solutions**:
1. **Verify REDIS_URL**:
   - Go to Redis service in Railway
   - Copy the connection string from "Connect" → "Redis"
   - Ensure it's set in your Django service environment variables

2. **Test Redis Connection**:
   ```bash
   # In Railway shell
   python -c "import redis; r = redis.from_url('$REDIS_URL'); print(r.ping())"
   ```

### 4. Build Failures

**Problem**: Build fails during deployment

**Solutions**:
1. **Check requirements.txt**:
   - Ensure all dependencies are listed
   - Check for version conflicts

2. **Check Python Version**:
   - Railway should auto-detect Python 3.11
   - Add `runtime.txt` if needed:
     ```
     python-3.11.5
     ```

3. **Check File Structure**:
   - Ensure `manage.py` is in root directory
   - Ensure `auth_service/` and `accounts/` directories exist

### 5. Static Files Issues

**Problem**: Static files not loading

**Solutions**:
1. **Check whitenoise configuration**:
   - Ensure `whitenoise` is in `requirements.txt`
   - Ensure `WhiteNoiseMiddleware` is in `MIDDLEWARE`

2. **Collect static files**:
   ```bash
   # In Railway shell
   python manage.py collectstatic --noinput
   ```

### 6. Rate Limiting Not Working

**Problem**: Rate limiting doesn't work

**Solutions**:
1. **Check Redis connection**:
   ```bash
   # Test Redis
   python -c "import redis; r = redis.from_url('$REDIS_URL'); print(r.ping())"
   ```

2. **Check Redis service**:
   - Ensure Redis service is running
   - Verify REDIS_URL is correct

### 7. JWT Authentication Issues

**Problem**: JWT tokens not working

**Solutions**:
1. **Check SECRET_KEY**:
   - Ensure SECRET_KEY is set and secure
   - Generate new one if needed:
     ```bash
     python -c "import secrets; print(secrets.token_urlsafe(50))"
     ```

2. **Check JWT settings**:
   - Verify `djangorestframework-simplejwt` is installed
   - Check JWT configuration in settings.py

## 🔧 Debugging Commands

### Railway Shell Commands

```bash
# Check environment variables
env | grep -E "(DATABASE_URL|REDIS_URL|SECRET_KEY|DEBUG|ALLOWED_HOSTS)"

# Test Django configuration
python manage.py check --deploy

# Test database connection
python manage.py dbshell

# Test Redis connection
python -c "import redis; r = redis.from_url('$REDIS_URL'); print(r.ping())"

# Check Django apps
python manage.py check

# Run migrations manually
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Test static files
python manage.py collectstatic --noinput

# Check logs
tail -f /var/log/django.log
```

### Manual Testing

```bash
# Test health check endpoint
curl https://your-app-name.railway.app/

# Test API endpoints
curl https://your-app-name.railway.app/api/accounts/

# Test Swagger documentation
curl https://your-app-name.railway.app/swagger/
```

## 📊 Monitoring and Logs

### Railway Dashboard
1. **Deployments Tab**: Check deployment status and logs
2. **Metrics Tab**: Monitor CPU, memory, and network usage
3. **Logs Tab**: View real-time application logs
4. **Variables Tab**: Check environment variables

### Common Log Messages

**Successful Startup**:
```
Starting Django Auth Service...
Checking database connection...
Running database migrations...
Collecting static files...
Starting Gunicorn server...
```

**Database Connection Error**:
```
django.db.utils.OperationalError: could not connect to server
```

**Redis Connection Error**:
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Missing Environment Variable**:
```
decouple.UndefinedValueError: SECRET_KEY not found
```

## 🚀 Deployment Checklist

Before deploying, ensure:

- [ ] All environment variables are set
- [ ] PostgreSQL service is running
- [ ] Redis service is running
- [ ] `requirements.txt` is up to date
- [ ] `manage.py` is in root directory
- [ ] `auth_service/` and `accounts/` directories exist
- [ ] `Procfile` is configured correctly
- [ ] `railway.json` is configured correctly

## 🔄 Redeployment Steps

If you need to redeploy:

1. **Push changes to GitHub**:
   ```bash
   git add .
   git commit -m "Fix deployment issues"
   git push origin main
   ```

2. **Railway will auto-deploy**

3. **Check deployment logs**:
   - Go to Railway dashboard
   - Check deployment status
   - Review logs for errors

4. **Test endpoints**:
   - Health check: `https://your-app-name.railway.app/`
   - API: `https://your-app-name.railway.app/api/accounts/`
   - Swagger: `https://your-app-name.railway.app/swagger/`

## 📞 Getting Help

If issues persist:

1. **Check Railway Documentation**: https://docs.railway.app/
2. **Review Django Deployment Guide**: https://docs.djangoproject.com/en/5.2/howto/deployment/
3. **Check Railway Community**: https://community.railway.app/
4. **Review this troubleshooting guide**
5. **Check application logs for specific error messages**

## 🎯 Success Indicators

Your deployment is successful when:

- [ ] Health check passes (`/` endpoint returns 200)
- [ ] Database migrations run successfully
- [ ] Redis connection works
- [ ] API endpoints respond correctly
- [ ] Rate limiting functions properly
- [ ] Static files load correctly
- [ ] Swagger documentation is accessible
- [ ] Admin interface works (after creating superuser)
