from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from .views import ProfileView, KycDocumentListCreateView, ProfileTemplateView, KycTemplateView, HomeView, DocumentsTemplateView, ViewProfileTemplateView


app_name = 'kyc'

urlpatterns = [
    # Home page
    path('', HomeView.as_view(), name='home'),
    
    # Auth token retrieval
    path('auth/token/', obtain_auth_token, name='api_token_auth'),

    # Profile endpoints
    path('profile/', ProfileView.as_view(), name='profile'),

    # KYC endpoints
    path('profile/kyc/', KycDocumentListCreateView.as_view(), name='profile-kyc-list-create'),

    # Frontend pages (MVT forms)
    path('view-profile-page/', ViewProfileTemplateView.as_view(), name='view-profile-page'),
    path('edit-profile-page/', ProfileTemplateView.as_view(), name='edit-profile-page'),
    path('profile-page/', ProfileTemplateView.as_view(), name='profile-page'),  # Keep for backward compatibility
    path('kyc-page/', KycTemplateView.as_view(), name='kyc-page'),
    path('documents-page/', DocumentsTemplateView.as_view(), name='documents-page'),
]


