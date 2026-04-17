from django.contrib import admin
from .models import KeyType, KeyAssignment, Person


@admin.register(KeyType)
class KeyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'total_count', 'assigned_count', 'available_count', 'color', 'order')
    ordering = ('order', 'name')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'email', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'role', 'email')


@admin.register(KeyAssignment)
class KeyAssignmentAdmin(admin.ModelAdmin):
    list_display = ('key_type', 'person', 'key_number', 'issued_date', 'return_date', 'is_active')
    list_filter = ('key_type', 'return_date')
    search_fields = ('person__name', 'key_number')
    date_hierarchy = 'issued_date'

    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = 'Noch vergeben'
