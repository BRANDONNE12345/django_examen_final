# blog/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ArticleViewSet, CommentaireViewSet, CategorieViewSet, TagViewSet

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'commentaires', CommentaireViewSet)
router.register(r'categories', CategorieViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
