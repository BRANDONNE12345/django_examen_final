# utilisateur/api_urls.py
from rest_framework.routers import DefaultRouter
from .api_views import CustomUserViewSet, NewsletterSubscriptionViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'newsletters', NewsletterSubscriptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
