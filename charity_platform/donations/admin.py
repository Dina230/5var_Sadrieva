from django.contrib import admin
from .models import CharityProject, Donation


@admin.register(CharityProject)
class CharityProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_amount', 'current_amount', 'progress_percentage_display', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['current_amount', 'progress_percentage_display', 'days_remaining_display', 'created_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'image_url')
        }),
        ('Финансы', {
            'fields': ('target_amount', 'current_amount', 'progress_percentage_display')
        }),
        ('Временные параметры', {
            'fields': ('deadline', 'days_remaining_display', 'created_at')
        }),
        ('Статус', {
            'fields': ('status',)
        }),
    )

    def progress_percentage_display(self, obj):
        return f"{obj.progress_percentage:.1f}%"

    progress_percentage_display.short_description = 'Прогресс'

    def days_remaining_display(self, obj):
        return f"{obj.days_remaining} дней"

    days_remaining_display.short_description = 'Осталось дней'

    def get_fieldsets(self, request, obj=None):
        """Разные fieldsets для добавления и изменения"""
        if obj is None:  # Добавление нового объекта
            return (
                ('Основная информация', {
                    'fields': ('name', 'description', 'image_url')
                }),
                ('Финансы', {
                    'fields': ('target_amount', 'current_amount')
                }),
                ('Временные параметры', {
                    'fields': ('deadline',)
                }),
                ('Статус', {
                    'fields': ('status',)
                }),
            )
        else:  # Изменение существующего объекта
            return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        """Разные readonly_fields для добавления и изменения"""
        if obj is None:  # Добавление нового объекта
            return ['progress_percentage_display', 'days_remaining_display']
        else:  # Изменение существующего объекта
            return self.readonly_fields


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donor_name', 'amount', 'project', 'created_at', 'is_anonymous']
    list_filter = ['created_at', 'is_anonymous', 'project']
    search_fields = ['donor_name', 'email']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    def get_readonly_fields(self, request, obj=None):
        """Разные readonly_fields для добавления и изменения"""
        if obj is None:  # Добавление нового объекта
            return []
        else:  # Изменение существующего объекта
            return self.readonly_fields