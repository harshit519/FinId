from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login

from .models import UserProfile, KycDocument
from .serializers import UserProfileSerializer, KycDocumentSerializer
from .forms import UserProfileForm, KycDocumentForm, ProfileCombinedForm, UserSignupForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.views import View


class EnsureUserProfileMixin:
    def get_user_profile(self, user: User) -> UserProfile:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        return profile


class HomeView(View):
    def get(self, request):
        if request.user.is_authenticated:
            profile = UserProfile.objects.get_or_create(user=request.user)[0]
            documents = KycDocument.objects.filter(user_profile=profile)
            return render(request, 'kyc/home.html', {
                'profile': profile,
                'documents': documents
            })
        return render(request, 'kyc/home.html')


class SignupView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = UserSignupForm()
        return render(request, 'kyc/signup.html', {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login after successful signup
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to FinId.')
            return redirect('home')
        return render(request, 'kyc/signup.html', {'form': form})


class ProfileView(APIView, EnsureUserProfileMixin):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = self.get_user_profile(request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = self.get_user_profile(request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@method_decorator(login_required, name='dispatch')
class ProfileTemplateView(EnsureUserProfileMixin, View):
    def get(self, request):
        profile = self.get_user_profile(request.user)
        form = ProfileCombinedForm(instance=profile, user=request.user)
        return render(request, 'kyc/profile.html', {'form': form, 'profile': profile})

    def post(self, request):
        profile = self.get_user_profile(request.user)
        form = ProfileCombinedForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('kyc:edit-profile-page')
        return render(request, 'kyc/profile.html', {'form': form, 'profile': profile})


@method_decorator(login_required, name='dispatch')
class ViewProfileTemplateView(EnsureUserProfileMixin, View):
    def get(self, request):
        profile = self.get_user_profile(request.user)
        return render(request, 'kyc/view_profile.html', {'profile': profile})


class KycDocumentListCreateView(APIView, EnsureUserProfileMixin):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        profile = self.get_user_profile(request.user)
        documents = KycDocument.objects.filter(user_profile=profile)
        serializer = KycDocumentSerializer(documents, many=True)
        return Response(serializer.data)

    def post(self, request):
        profile = self.get_user_profile(request.user)
        data = request.data.copy()
        data['user_profile'] = profile.id
        serializer = KycDocumentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(login_required, name='dispatch')
class KycTemplateView(EnsureUserProfileMixin, View):
    def get(self, request):
        profile = self.get_user_profile(request.user)
        form = KycDocumentForm()
        return render(request, 'kyc/kyc_upload.html', {'form': form, 'profile': profile})

    def post(self, request):
        profile = self.get_user_profile(request.user)
        form = KycDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            kyc_doc: KycDocument = form.save(commit=False)
            kyc_doc.user_profile = profile
            kyc_doc.save()
            return redirect('kyc:kyc-page')
        return render(request, 'kyc/kyc_upload.html', {'form': form, 'profile': profile})


@method_decorator(login_required, name='dispatch')
class DocumentsTemplateView(EnsureUserProfileMixin, View):
    def get(self, request):
        profile = self.get_user_profile(request.user)
        documents = KycDocument.objects.filter(user_profile=profile)
        return render(request, 'kyc/documents.html', {'documents': documents, 'profile': profile})

    def post(self, request):
        profile = self.get_user_profile(request.user)
        document_id = request.POST.get('document_id')
        
        if document_id:
            try:
                document = KycDocument.objects.get(id=document_id, user_profile=profile)
                document.delete()
                messages.success(request, 'Document deleted successfully.')
            except KycDocument.DoesNotExist:
                messages.error(request, 'Document not found.')
        
        return redirect('kyc:documents-page')
