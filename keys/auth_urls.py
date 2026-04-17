from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.oidc_login, name='oidc_login'),
    path('callback/', views.oidc_callback, name='oidc_callback'),
    path('logout/', views.oidc_logout, name='oidc_logout'),
]
