from django.urls import path
from . import views

urlpatterns = [
    # PowerSync authentication endpoint - matches client expectation
    path('auth/token', views.get_powersync_token, name='auth_token'),
    
    # Legacy endpoint for backward compatibility
    path('get_powersync_token/', views.get_powersync_token,
         name='get_powersync_token'),
    
    # JWKS endpoint for PowerSync
    path('get_keys/', views.get_keys, name='get_keys'),
    
    # Session endpoint
    path('get_session/', views.get_session, name='get_session'),
    
    # User authentication endpoints
    path('auth/', views.auth, name='auth'),
    path('register/', views.register, name='register'),
    
    # Data upload endpoint - matches client expectation
    path('data', views.upload_data, name='upload_data'),
    
    # Legacy endpoint for backward compatibility
    path('upload_data/', views.upload_data, name='upload_data_legacy'),
]

