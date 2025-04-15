# blog/admin.py
from django.contrib import admin
from .models import Categorie, Tag, Article, Commentaire

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'statut', 'created_at')
    search_fields = ('nom',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nom', 'statut', 'created_at')
    search_fields = ('nom',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'categorie', 'est_publie', 'created_at')
    list_filter = ('est_publie', 'categorie', 'created_at')
    search_fields = ('titre', 'resume', 'contenu')
    prepopulated_fields = {"slug": ("titre",)}

@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('auteur_id', 'article_id', 'created_at')
    search_fields = ('auteur_id__username', 'contenu')
