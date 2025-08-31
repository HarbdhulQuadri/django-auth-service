"""
URL configuration for auth_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Health check view
@csrf_exempt
def health_check(request):
    """Simple health check endpoint for Railway."""
    return JsonResponse({
        "status": "healthy",
        "message": "Django Auth Service is running",
        "version": "1.0.0"
    })

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="Django Auth Service API",
        default_version='v1',
        description="A comprehensive Django authentication system with JWT tokens, password reset functionality, and PostgreSQL/Redis integration.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Health check endpoint
    path('', health_check, name='health_check'),
    
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/accounts/', include('accounts.urls')),
    
    # Swagger documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
