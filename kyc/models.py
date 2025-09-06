from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    LANGUAGES = [
        ('english', 'English'),
        ('hindi', 'Hindi'),
        ('spanish', 'Spanish'),
        ('french', 'French'),
        ('german', 'German'),
        ('chinese', 'Chinese'),
        ('japanese', 'Japanese'),
        ('arabic', 'Arabic'),
        ('other', 'Other'),
    ]
    
    EDUCATION_LEVELS = [
        ('high_school', 'High School'),
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD/Doctorate'),
        ('other', 'Other'),
    ]
    
    PROFESSION_TYPES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('freelance', 'Freelance'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('unemployed', 'Unemployed'),
        ('student', 'Student'),
        ('retired', 'Retired'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    linkedin_profile = models.URLField(blank=True, max_length=200)
    github_profile = models.URLField(blank=True, max_length=200)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=20, choices=LANGUAGES, default='english')
    
    # Education fields
    education_level = models.CharField(max_length=20, choices=EDUCATION_LEVELS, blank=True)
    institution = models.CharField(max_length=200, blank=True)
    graduation_year = models.IntegerField(null=True, blank=True)
    
    # Profession fields
    profession = models.CharField(max_length=100, blank=True)
    profession_type = models.CharField(max_length=20, choices=PROFESSION_TYPES, blank=True)

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"


def kyc_document_upload_path(instance: 'KycDocument', filename: str) -> str:
    return f"kyc/{instance.user_profile.user.id}/{filename}"


class KycDocument(models.Model):
    DOCUMENT_TYPES = [
        ('passport', 'Passport'),
        ('driving_license', 'Driving License'),
        ('national_id', 'National ID'),
        ('birth_certificate', 'Birth Certificate'),
        ('utility_bill', 'Utility Bill'),
        ('bank_statement', 'Bank Statement'),
        ('employment_letter', 'Employment Letter'),
        ('other', 'Other'),
    ]
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='kyc_documents')
    # Core file upload
    document_file = models.FileField(upload_to=kyc_document_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Enriched KYC metadata
    document_id = models.CharField(max_length=20, blank=True)
    registration_number = models.CharField(max_length=20, blank=True)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES, default='other')

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self) -> str:
        return f"KYC Doc for {self.user_profile.user.username} at {self.uploaded_at}"

# Create your models here.
