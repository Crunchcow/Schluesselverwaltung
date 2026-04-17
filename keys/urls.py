from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('schluessel/', views.key_list, name='key_list'),
    path('schluessel/typ/<int:type_id>/', views.key_list, name='key_list_by_type'),
    path('schluessel/<int:key_id>/vergeben/', views.assign_key, name='assign_key'),
    path('vergabe/<int:assignment_id>/zurueck/', views.return_key, name='return_key'),
    path('historie/', views.history, name='history'),
    # Verwaltung
    path('verwalten/', views.manage, name='manage'),
    path('verwalten/typ/neu/', views.keytype_create, name='keytype_create'),
    path('verwalten/typ/<int:type_id>/bearbeiten/', views.keytype_edit, name='keytype_edit'),
    path('verwalten/typ/<int:type_id>/loeschen/', views.keytype_delete, name='keytype_delete'),
    path('verwalten/schluessel/neu/', views.key_create, name='key_create'),
    path('verwalten/schluessel/<int:key_id>/bearbeiten/', views.key_edit, name='key_edit'),
    path('verwalten/schluessel/<int:key_id>/loeschen/', views.key_delete, name='key_delete'),
    # Personen
    path('verwalten/person/neu/', views.person_create, name='person_create'),
    path('verwalten/person/<int:person_id>/bearbeiten/', views.person_edit, name='person_edit'),
    path('verwalten/person/<int:person_id>/loeschen/', views.person_delete, name='person_delete'),
]
