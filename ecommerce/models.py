# ecommerce/models.py
from django.db import models
from django.conf import settings
import secrets
import string
from django.utils.translation import gettext_lazy as _

# --------------------------------------------------
#  Catégories
# --------------------------------------------------
class CategorieProduit(models.Model):
    """
    Catégorie de produit (ex. chaises, tables, canapés africains, etc.).
    """
    nom = models.CharField(_("Nom"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True)

    class Meta:
        verbose_name = _("Catégorie de produit")
        verbose_name_plural = _("Catégories de produits")
        ordering = ["nom"]

    def __str__(self):
        return self.nom


# --------------------------------------------------
#  Produits
# --------------------------------------------------
class Produit(models.Model):
    # --- Informations principales ---
    nom          = models.CharField(_("Nom"), max_length=200)
    description  = models.TextField(_("Description"))
    image        = models.ImageField(
        _("Image principale"),
        upload_to="produits/",
        blank=True,
        null=True,
    )

    # --- Prix & stock ---
    prix         = models.DecimalField(_("Prix"), max_digits=10, decimal_places=2)
    stock        = models.PositiveIntegerField(_("Stock disponible"))

    # --- Badges / Promotions ---
    est_nouveau  = models.BooleanField(_("Nouveau"), default=False)
    en_promotion = models.BooleanField(_("En promotion"), default=False)
    prix_promo   = models.DecimalField(
        _("Prix promo"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Laisser vide si pas de promo ou si remise % gérée ailleurs"),
    )

    # --- Détails techniques ---
    matiere   = models.CharField(_("Matière"), max_length=100, blank=True)
    longueur  = models.PositiveIntegerField(_("Longueur (cm)"), blank=True, null=True)
    largeur   = models.PositiveIntegerField(_("Largeur (cm)"), blank=True, null=True)
    hauteur   = models.PositiveIntegerField(_("Hauteur (cm)"), blank=True, null=True)

    # --- Relations ---
    categorie = models.ForeignKey(
        CategorieProduit,
        on_delete=models.SET_NULL,
        null=True,
        related_name="produits",
        verbose_name=_("Catégorie"),
    )

    class Meta:
        verbose_name = _("Produit")
        verbose_name_plural = _("Produits")
        ordering = ["nom"]

    # ---------- helpers ----------
    def __str__(self):
        return self.nom

    @property
    def prix_affiche(self):
        """
        Renvoie le prix à afficher (prix promo si actif, sinon prix normal).
        """
        if self.en_promotion and self.prix_promo:
            return self.prix_promo
        return self.prix

    @property
    def dimensions(self):
        """
        Retourne une chaîne du type « 200 × 80 × 75 cm » ou « — » si absent.
        """
        if self.longueur and self.largeur and self.hauteur:
            return f"{self.longueur}×{self.largeur}×{self.hauteur} cm"
        return "—"


# --------------------------------------------------
#  Galerie d’images pour un produit
# --------------------------------------------------
class ProduitImage(models.Model):
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Produit"),
    )
    image   = models.ImageField(_("Image"), upload_to="produits_gallery/")
    legende = models.CharField(_("Légende"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("Image de produit")
        verbose_name_plural = _("Images de produits")

    def __str__(self):
        return f"Image de {self.produit.nom}"


# --------------------------------------------------
#  Panier & PanierItem
# --------------------------------------------------
class Panier(models.Model):
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="panier",
        verbose_name=_("Utilisateur"),
    )

    class Meta:
        verbose_name = _("Panier")
        verbose_name_plural = _("Paniers")

    def __str__(self):
        return f"Panier de {self.utilisateur.username}"

    @property
    def total(self):
        return sum(item.sous_total for item in self.items.all())


class PanierItem(models.Model):
    panier   = models.ForeignKey(
        Panier, on_delete=models.CASCADE, related_name="items", verbose_name=_("Panier")
    )
    produit  = models.ForeignKey(
        Produit, on_delete=models.CASCADE, verbose_name=_("Produit")
    )
    quantite = models.PositiveIntegerField(_("Quantité"), default=1)

    class Meta:
        unique_together = ("panier", "produit")
        verbose_name = _("Article de panier")
        verbose_name_plural = _("Articles de panier")

    def __str__(self):
        return f"{self.quantite} × {self.produit.nom}"

    @property
    def sous_total(self):
        return self.quantite * self.produit.prix_affiche


# --------------------------------------------------
#  Commandes
# --------------------------------------------------

ORDER_STATUS_CHOICES = (
    ('en_attente', "En attente"),
    ('en_cours', "En cours de traitement"),
    ('expediee', "Expédiée"),
    ('terminee', "Terminée"),
    ('annulee', "Annulée"),

)

class Commande(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="commandes",
        verbose_name=_("Utilisateur"),
    )
    date = models.DateTimeField(_("Date"), auto_now_add=True)
    montant_total = models.DecimalField(_("Montant total"), max_digits=10, decimal_places=2)
    etat = models.CharField(_("État"), max_length=50, choices=ORDER_STATUS_CHOICES, default="en_attente")
    # Champs de facturation
    pays = models.CharField(_("Pays"), max_length=50, blank=True, null=True)
    prenom = models.CharField(_("Prénom"), max_length=100, blank=True, null=True)
    nom = models.CharField(_("Nom"), max_length=100, blank=True, null=True)
    adresse = models.CharField(_("Adresse"), max_length=255, blank=True, null=True)
    ville = models.CharField(_("Ville"), max_length=100, blank=True, null=True)
    code_postal = models.CharField(_("Code Postal"), max_length=20, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    telephone = models.CharField(_("Téléphone"), max_length=20, blank=True, null=True)
    PAYMENT_METHOD_CHOICES = [
        ('orange_money', "Orange Money"),
        ('mtn_mooney', "MTN Mooney"),
        ('moov_monney', "Moov Monney"),
    ]
    mode_paiement = models.CharField(
        _("Mode de paiement"),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        null=True,
        help_text=_("Sélectionnez votre moyen de paiement")
    )

    class Meta:
        verbose_name = _("Commande")
        verbose_name_plural = _("Commandes")
        ordering = ["-date"]

    def __str__(self):
        return f"Commande {self.id} de {self.utilisateur.username}"
    
    @property
    def progress_percentage(self):
        status_map = {
            'en_attente': 25,
            'en_cours': 50,
            'expediee': 75,
            'terminee': 100,
            'annulee': 0,
        }
        return status_map.get(self.etat, 0)

class DetailCommande(models.Model):
    commande  = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name="details",
        verbose_name=_("Commande"),
    )
    produit   = models.ForeignKey(
        Produit, on_delete=models.CASCADE, verbose_name=_("Produit")
    )
    quantite  = models.PositiveIntegerField(_("Quantité"))
    sous_total = models.DecimalField(_("Sous‑total"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Ligne de commande")
        verbose_name_plural = _("Lignes de commande")

    def __str__(self):
        return f"{self.quantite} × {self.produit.nom} (Cmd {self.commande.id})"


# --------------------------------------------------
#  Avis / Notes
# --------------------------------------------------
class Avis(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="avis",
        verbose_name=_("Utilisateur"),
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        related_name="avis",
        verbose_name=_("Produit"),
    )
    note        = models.PositiveSmallIntegerField(_("Note"), default=5)
    commentaire = models.TextField(_("Commentaire"), blank=True)
    date        = models.DateTimeField(_("Date"), auto_now_add=True)

    class Meta:
        verbose_name = _("Avis")
        verbose_name_plural = _("Avis")
        ordering = ["-date"]

    def __str__(self):
        return f"Avis de {self.utilisateur.username} sur {self.produit.nom} ({self.note}/5)"


class PromoCode(models.Model):
    code = models.CharField(_("Code Promo"), max_length=10, unique=True, blank=True)
    discount_percentage = models.PositiveIntegerField(
        _("Pourcentage de Réduction"),
        help_text=_("Pourcentage de réduction (ex. 10 = 10%)")
    )
    is_used = models.BooleanField(_("Utilisé"), default=False)

    class Meta:
        verbose_name = _("Code Promo")
        verbose_name_plural = _("Codes Promo")
    
    def __str__(self):
        return f"{self.code} ({self.discount_percentage}%{' - utilisé' if self.is_used else ''})"
    
    def save(self, *args, **kwargs):
        # Si aucun code n'est renseigné, on le génère automatiquement.
        if not self.code:
            alphabet = string.ascii_uppercase + string.digits
            self.code = ''.join(secrets.choice(alphabet) for _ in range(10))
        super().save(*args, **kwargs)


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",  # Accès depuis l'utilisateur
        verbose_name="Utilisateur"
    )
    produit = models.ForeignKey(
        'Produit',
        on_delete=models.CASCADE,
        related_name="liked_by",  # Vous permettra d'utiliser produit.liked_by.count()
        verbose_name="Produit"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "produit")
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"

    def __str__(self):
        return f"{self.user.username} aime {self.produit.nom}"
    
    