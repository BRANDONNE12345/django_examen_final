# utilisateur/api_views.py
from rest_framework import viewsets, permissions
from .models import CustomUser, NewsletterSubscription
from .serializers import CustomUserSerializer, NewsletterSubscriptionSerializer

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAdminUser]  # ou [permissions.IsAuthenticated] selon ton besoin

class NewsletterSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = NewsletterSubscription.objects.all()
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
