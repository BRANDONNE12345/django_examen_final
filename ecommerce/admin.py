from django.contrib import admin
from .models import PromoCode
from .models import (
    CategorieProduit,
    Produit,
    ProduitImage,
    Panier,
    PanierItem,
    Commande,
    DetailCommande,
    Avis,
)

# ---------- Inlines ----------

class ProduitImageInline(admin.TabularInline):
    """
    Permet d’ajouter plusieurs images secondaires à un produit.
    """
    model = ProduitImage
    extra = 1

class DetailCommandeInline(admin.TabularInline):
    """
    Affiche les lignes de commande dans la fiche Commande.
    """
    model = DetailCommande
    readonly_fields = ("produit", "quantite", "sous_total")
    extra = 0

# ---------- ModelAdmins ----------

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    inlines = [ProduitImageInline]
    list_display = (
        "nom",
        "prix",
        "prix_affiche",
        "en_promotion",
        "est_nouveau",
        "stock",
        "categorie",
    )
    search_fields = ("nom",)
    list_filter = ("categorie", "en_promotion", "est_nouveau")
    fieldsets = (
        (
            "Informations de base",
            {
                "fields": ("nom", "description", "categorie", "image"),
            },
        ),
        (
            "Prix & Stock",
            {"fields": ("prix", "prix_promo", "en_promotion", "stock")},
        ),
        (
            "Détails techniques",
            {"fields": ("matiere", "longueur", "largeur", "hauteur")},
        ),
        (
            "Badge",
            {"fields": ("est_nouveau",)},
        ),
    )

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    inlines = [DetailCommandeInline]
    list_display = ("id", "utilisateur", "montant_total", "date", "etat")
    readonly_fields = ("montant_total", "date")

    def save_model(self, request, obj, form, change):
        """
        Lors de la création d'une commande via l’admin,
        on remplit automatiquement les lignes de commande à partir du panier de l'utilisateur.
        """
        if not change:
            # Récupère le panier éventuel de l’utilisateur
            panier = getattr(obj.utilisateur, "panier", None)

            if panier:
                items = panier.items.all()
                obj.montant_total = sum(
                    item.produit.prix * item.quantite for item in items
                )
            else:
                obj.montant_total = 0

            super().save_model(request, obj, form, change)

            # Création des lignes de commande et vidage du panier
            if panier:
                for item in items:
                    DetailCommande.objects.create(
                        commande=obj,
                        produit=item.produit,
                        quantite=item.quantite,
                        sous_total=item.produit.prix * item.quantite,
                    )
                panier.items.all().delete()
        else:
            super().save_model(request, obj, form, change)

# ---------- Enregistrements simples ----------

admin.site.register(CategorieProduit)
admin.site.register(Panier)
admin.site.register(PanierItem)
admin.site.register(DetailCommande)  # utile pour le reporting
admin.site.register(Avis)
admin.site.register(PromoCode)