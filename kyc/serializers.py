from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

from .models import UserProfile, KycDocument


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'phone_number', 'address', 'date_of_birth', 'linkedin_profile', 'github_profile', 'profile_photo', 'nationality', 'language', 'education_level', 'institution', 'graduation_year', 'profession', 'profession_type')


ALLOWED_CONTENT_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/png',
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class KycDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KycDocument
        fields = (
            'id',
            'user_profile',
            'document_file',
            'uploaded_at',
            'document_id',
            'registration_number',
            'document_type',
        )
        read_only_fields = ('id', 'uploaded_at', 'user_profile')

    def validate_document_file(self, file: UploadedFile):
        content_type = getattr(file, 'content_type', None)
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError('Unsupported file type. Allowed: PDF, JPEG, PNG.')
        if file.size > MAX_FILE_SIZE:
            raise serializers.ValidationError('File too large. Maximum allowed size is 5 MB.')
        return file



