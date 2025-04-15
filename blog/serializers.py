# blog/serializers.py
from rest_framework import serializers
from .models import Categorie, Tag, Article, Commentaire

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class ArticleSerializer(serializers.ModelSerializer):
    auteur = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Article
        fields = '__all__'

class CommentaireSerializer(serializers.ModelSerializer):
    auteur = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Commentaire
        fields = '__all__'
