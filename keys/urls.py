from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('schluessel/', views.key_list, name='key_list'),
    path('schluessel/typ/<int:type_id>/', views.key_list, name='key_list_by_type'),
    path('schluessel/<int:key_id>/vergeben/', views.assign_key, name='assign_key'),
    path('vergabe/<int:assignment_id>/zurueck/', views.return_key, name='return_key'),
    path('historie/', views.history, name='history'),
]
