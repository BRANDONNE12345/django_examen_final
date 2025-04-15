# blog/forms.py
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget  # Widget pour CKEditor5
from .models import Article, Commentaire

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        # Utilisez les noms de champs du modèle
        fields = ["titre", "couverture", "resume", "contenu", "categorie", "tags"]
        widgets = {
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        fields = ["contenu"]
