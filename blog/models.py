from django.db import models
from django.conf import settings
from django.utils.text import slugify
from datetime import date
from django_ckeditor_5.fields import CKEditor5Field

class Categorie(models.Model):
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    nom = models.CharField(verbose_name="Nom", max_length=255)
    description = models.TextField()
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

class Tag(models.Model):
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    nom = models.CharField(verbose_name="Nom", max_length=255)
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

class Article(models.Model):
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    titre = models.CharField(verbose_name="Titre", max_length=256)
    couverture = models.ImageField(
        upload_to="articles",
        verbose_name="Image de couverture",
        blank=True,
        null=True
    )
    resume = models.TextField(verbose_name="Résumé")
    contenu = CKEditor5Field('Contenu', config_name='default')

    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="articles",
        verbose_name="Auteur"
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.SET_NULL,
        null=True,
        related_name="articles",
        verbose_name="Catégorie"
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="articles",
        verbose_name="Tags",
        blank=True
    )
    
    est_publie = models.BooleanField(default=False, verbose_name="Publié")
    date_de_publication = models.DateField(auto_now_add=True, verbose_name="Date de publication")
    slug = models.SlugField(default="", blank=True, verbose_name="Slug", unique=True)  # <- unique ajouté

    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):  # ✅ bien placée DANS la classe Article
        if not self.slug:
            base_slug = slugify(self.titre) + "-" + str(date.today().year)
            slug = base_slug
            num = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

class Commentaire(models.Model):
    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"

    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="auteur_commentaire_ids"
    )
    article = models.ForeignKey(
        "blog.Article",
        on_delete=models.CASCADE,
        related_name="article_commentaire_ids"
    )
    contenu = models.TextField()
    
    statut = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.auteur.username if self.auteur else "Commentaire sans auteur"
