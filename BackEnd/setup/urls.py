"""
URL configuration for setup/installation endpoints.

All endpoints are under /api/setup/
"""
from django.urls import path
from . import views

app_name = 'setup'

urlpatterns = [
    path('status/', views.setup_status, name='setup-status'),
    path('db-check/', views.db_check, name='db-check'),
    path('run-migrations/', views.run_migrations, name='run-migrations'),
    path('create-admin/', views.create_admin, name='create-admin'),
    path('finalize/', views.finalize, name='finalize'),
]
