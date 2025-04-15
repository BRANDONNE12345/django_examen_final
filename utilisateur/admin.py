from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, NewsletterSubscription

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subscribed_at', 'active')
    list_filter = ('active', 'subscribed_at')
    search_fields = ('name', 'email')