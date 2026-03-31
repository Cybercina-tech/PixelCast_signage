from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserViewSet,
    login_view,
    logout_view,
    logout_all_view,
    sessions_view,
    signup_view,
    roles_view,
    create_role,
    SendVerificationEmail,
    VerifyEmail,
    sidebar_items_view
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Router URLs (includes /api/users/ for ViewSet)
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/signup/', signup_view, name='auth-signup'),
    path('auth/login/', login_view, name='auth-login'),
    path('auth/logout/', logout_view, name='auth-logout'),
    path('auth/logout-all/', logout_all_view, name='auth-logout-all'),
    path('auth/sessions/', sessions_view, name='auth-sessions'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Role management endpoints
    path('roles/', roles_view, name='roles-list'),
    path('roles/create/', create_role, name='roles-create'),
    
    # Email verification endpoints
    path('send-verification-email/', SendVerificationEmail.as_view(), name='send-verification-email'),
    path('verify-email/', VerifyEmail.as_view(), name='verify-email'),
    
    # Sidebar items endpoint
    path('sidebar-items/', sidebar_items_view, name='sidebar-items'),
]
