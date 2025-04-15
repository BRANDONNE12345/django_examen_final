# ecommerce/serializers.py
from rest_framework import serializers
from .models import (
    CategorieProduit, Produit, ProduitImage, Panier, PanierItem,
    Commande, DetailCommande, Avis, PromoCode, Favorite
)

class CategorieProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorieProduit
        fields = '__all__'

class ProduitImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProduitImage
        fields = '__all__'

class ProduitSerializer(serializers.ModelSerializer):
    images = ProduitImageSerializer(many=True, read_only=True)
    prix_affiche = serializers.ReadOnlyField()

    class Meta:
        model = Produit
        fields = '__all__'

class AvisSerializer(serializers.ModelSerializer):
    utilisateur = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Avis
        fields = '__all__'

class PanierItemSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)

    class Meta:
        model = PanierItem
        fields = '__all__'

class PanierSerializer(serializers.ModelSerializer):
    items = PanierItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()

    class Meta:
        model = Panier
        fields = '__all__'

class DetailCommandeSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)

    class Meta:
        model = DetailCommande
        fields = '__all__'

class CommandeSerializer(serializers.ModelSerializer):
    utilisateur = serializers.StringRelatedField(read_only=True)
    details = DetailCommandeSerializer(many=True, read_only=True)
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Commande
        fields = '__all__'

class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
