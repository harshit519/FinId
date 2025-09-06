from django.contrib import admin
from .models import UserProfile, KycDocument


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'nationality', 'language', 'date_of_birth')
    search_fields = ('user__username', 'user__email', 'phone_number', 'nationality')
    list_filter = ('language', 'date_of_birth')


@admin.register(KycDocument)
class KycDocumentAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'uploaded_at', 'document_type', 'document_id', 'registration_number')
    search_fields = (
        'user_profile__user__username',
        'document_id',
        'registration_number',
        'document_type',
    )
    list_filter = ('uploaded_at', 'document_type')

# Register your models here.
