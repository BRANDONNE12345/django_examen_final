# ecommerce/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import *

router = DefaultRouter()
router.register(r'produits', ProduitViewSet)
router.register(r'categories', CategorieProduitViewSet)
router.register(r'avis', AvisViewSet)
router.register(r'panier', PanierViewSet)
router.register(r'panier-items', PanierItemViewSet)
router.register(r'commandes', CommandeViewSet)
router.register(r'promos', PromoCodeViewSet)
router.register(r'favoris', FavoriteViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
