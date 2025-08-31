# Railway Deployment Checklist

## ✅ Pre-Deployment Checklist

### Repository Files
- [x] `requirements.txt` - All dependencies listed
- [x] `Procfile` - Railway deployment configuration
- [x] `railway.json` - Railway-specific settings
- [x] `manage.py` - Django management script
- [x] `auth_service/` - Django project settings
- [x] `accounts/` - Django app with authentication
- [x] `.gitignore` - Excludes unnecessary files
- [x] `env.example` - Environment variables template
- [x] `README.md` - Project documentation

### Removed Files (Not needed for deployment)
- [x] `test_rate_limiting.py` - Testing script
- [x] `RATE_LIMITING_DEMO.md` - Demo documentation
- [x] `env.docker` - Docker environment file
- [x] `docker-compose.yml` - Docker Compose file
- [x] `Dockerfile` - Docker configuration
- [x] `.dockerignore` - Docker ignore file
- [x] `.env` - Local environment file
- [x] `venv/` - Virtual environment directory

## 🚀 Railway Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Create Railway Project
1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository

### 3. Add PostgreSQL Database
1. In Railway dashboard: "New" → "Database" → "PostgreSQL"
2. Copy the connection string from the PostgreSQL service

### 4. Add Redis Cache
1. In Railway dashboard: "New" → "Database" → "Redis"
2. Copy the connection string from the Redis service

### 5. Configure Environment Variables
In your Django service, add these variables:

```env
# Django Settings
SECRET_KEY=uZ_jAU-I0304dydvuI3rgWqxL5sDAu1UKxA5pVEhag6fpF5KqkJKD9xzD8hK-ii_K8Y
DEBUG=False
ALLOWED_HOSTS=your-app-name.railway.app,localhost,127.0.0.1

# Database (from PostgreSQL service)
DATABASE_URL=postgresql://user:password@host:port/database

# Redis (from Redis service)
REDIS_URL=redis://user:password@host:port/database
```

### 6. Deploy and Test
1. Railway will auto-deploy from GitHub
2. Check deployment logs for errors
3. Test API endpoints:
   - `https://your-app-name.railway.app/api/accounts/`
   - `https://your-app-name.railway.app/swagger/`
   - `https://your-app-name.railway.app/admin/`

## 🔧 Post-Deployment Tasks

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
- Verify database and Redis connections
- Test rate limiting functionality

## 🛠️ Troubleshooting

### Common Issues
1. **Build fails**: Check `requirements.txt` and Railway logs
2. **Database connection**: Verify `DATABASE_URL` is correct
3. **Redis connection**: Verify `REDIS_URL` is correct
4. **Static files**: Add `collectstatic` to Procfile if needed
5. **Rate limiting**: Check Redis service is running

### Debug Commands
```bash
# Check environment variables
env | grep -E "(DATABASE_URL|REDIS_URL|SECRET_KEY)"

# Test database connection
python manage.py dbshell

# Test Redis connection
python -c "import redis; r = redis.from_url('$REDIS_URL'); print(r.ping())"

# Check Django configuration
python manage.py check --deploy
```

## 📊 Monitoring

### Railway Dashboard
- Monitor deployment status
- Check CPU/memory usage
- View real-time logs
- Monitor health checks

### Health Check
Your app includes a health check at `/api/accounts/` that Railway uses for monitoring.

## 🔒 Security Notes

- ✅ SECRET_KEY is secure and random
- ✅ DEBUG is set to False
- ✅ ALLOWED_HOSTS is configured
- ✅ HTTPS is automatically provided by Railway
- ✅ Database and Redis are secure by default

## 🎯 Success Criteria

Your deployment is successful when:
- [ ] App deploys without errors
- [ ] Database migrations run successfully
- [ ] API endpoints respond correctly
- [ ] Rate limiting works as expected
- [ ] Admin interface is accessible
- [ ] Swagger documentation loads
- [ ] Health checks pass

## 📞 Support

If you encounter issues:
1. Check Railway deployment logs
2. Verify environment variables
3. Test database and Redis connections
4. Review the `RAILWAY_DEPLOYMENT.md` guide
5. Check Railway documentation

Your Django Auth Service is now ready for production deployment! 🚀
