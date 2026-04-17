from django.contrib import admin
from .models import KeyType, Key, KeyAssignment


@admin.register(KeyType)
class KeyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'color', 'order')
    ordering = ('order', 'name')


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ('key_type', 'number', 'notes', 'is_assigned')
    list_filter = ('key_type',)
    search_fields = ('number', 'notes')

    def is_assigned(self, obj):
        return obj.is_assigned()
    is_assigned.boolean = True
    is_assigned.short_description = 'Vergeben'


@admin.register(KeyAssignment)
class KeyAssignmentAdmin(admin.ModelAdmin):
    list_display = ('key', 'holder_name', 'holder_email', 'issued_date', 'return_date', 'is_active')
    list_filter = ('key__key_type', 'return_date')
    search_fields = ('holder_name', 'holder_email', 'holder_phone')
    date_hierarchy = 'issued_date'

    def is_active(self, obj):
        return obj.is_active
    is_active.boolean = True
    is_active.short_description = 'Noch vergeben'
