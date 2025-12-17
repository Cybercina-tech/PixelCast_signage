from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserViewSet,
    login_view,
    logout_view,
    roles_view,
    create_role
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Router URLs (includes /api/users/ for ViewSet)
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/login/', login_view, name='auth-login'),
    path('auth/logout/', logout_view, name='auth-logout'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Role management endpoints
    path('roles/', roles_view, name='roles-list'),
    path('roles/create/', create_role, name='roles-create'),
]
