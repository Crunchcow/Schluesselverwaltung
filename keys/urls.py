from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('vergeben/<int:type_id>/', views.assign_key, name='assign_key'),
    path('vergabe/<int:assignment_id>/zurueck/', views.return_key, name='return_key'),
    path('historie/', views.history, name='history'),
    # Verwaltung
    path('verwalten/', views.manage, name='manage'),
    path('verwalten/typ/neu/', views.keytype_create, name='keytype_create'),
    path('verwalten/typ/<int:type_id>/bearbeiten/', views.keytype_edit, name='keytype_edit'),
    path('verwalten/typ/<int:type_id>/loeschen/', views.keytype_delete, name='keytype_delete'),
    # Personen
    path('verwalten/person/neu/', views.person_create, name='person_create'),
    path('verwalten/person/<int:person_id>/bearbeiten/', views.person_edit, name='person_edit'),
    path('verwalten/person/<int:person_id>/loeschen/', views.person_delete, name='person_delete'),
]
