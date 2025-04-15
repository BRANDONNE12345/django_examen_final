# ecommerce/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Avg
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from django.http import JsonResponse, HttpResponseRedirect
from .models import Produit, Favorite


from .models import (
    Avis, CategorieProduit, Produit,
    Panier, PanierItem, Commande, DetailCommande, PromoCode
)
@login_required
def thankyou(request):
    return render(request, "thankyou.html")

# ----------------- BOUTIQUE -----------------
def shop(request):
    category_id = request.GET.get("category")
    search = request.GET.get("search", "").strip()

    categories = CategorieProduit.objects.all()
    produits = Produit.objects.all()
    if category_id:
        produits = produits.filter(categorie_id=category_id)
    if search:
        produits = produits.filter(nom__icontains=search)

    return render(
        request,
        "shop.html",
        {
            "produits": produits,
            "categories": categories,
            "selected_category": category_id,
        },
    )

def index(request):
    produits = Produit.objects.all()[:3]
    return render(request, "index.html", {"produits": produits})

def product_detail(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    produits_similaires = (
        Produit.objects.filter(categorie=produit.categorie)
        .exclude(pk=pk)[:4]
    )
    avg_note = produit.avis.aggregate(avg=Avg("note"))["avg"] or 0
    return render(
        request,
        "product_detail.html",
        {
            "produit": produit,
            "produits_similaires": produits_similaires,
            "avg_note": avg_note,
        },
    )

# ----------------- PANIER -----------------
@login_required
def add_to_cart(request, pk):
    """
    Ajoute un produit au panier de l'utilisateur connecté.
    Si l'item existe déjà, incrémente la quantité sans dépasser le stock.
    """
    produit = get_object_or_404(Produit, pk=pk)
    try:
        quantite = int(request.POST.get('quantite', 1))
        if quantite < 1:
            quantite = 1
    except ValueError:
        quantite = 1

    # Récupère ou crée le panier de l'utilisateur
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)

    # Récupère l'item existant ou en crée un nouveau
    panier_item, item_created = PanierItem.objects.get_or_create(panier=panier, produit=produit)
    if not item_created:
        new_quantite = panier_item.quantite + quantite
        panier_item.quantite = min(new_quantite, produit.stock)
    else:
        panier_item.quantite = min(quantite, produit.stock)
    panier_item.save()

    return redirect('ecommerce:cart')
@login_required
def cart_view(request):
    # Récupère ou crée le panier de l'utilisateur connecté
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    cart_items = panier.items.select_related('produit').all()
    total = sum(item.sous_total for item in cart_items)

    promo_total = None
    # Si un code promo a été appliqué (via session), recalculer le total réduit
    if "promo_discount" in request.session:
        try:
            discount_percentage = Decimal(request.session["promo_discount"])
            reduction = total * (discount_percentage / Decimal("100"))
            promo_total = total - reduction
        except Exception:
            promo_total = None

    context = {
        'cart_items': cart_items,
        'total': total,
        'promo_total': promo_total,  # Total après remise si promo appliquée
    }
    return render(request, 'cart.html', context)

@login_required
def remove_from_cart(request, item_id):
    """
    Supprime un article du panier de l'utilisateur.
    """
    panier = get_object_or_404(Panier, utilisateur=request.user)
    item = get_object_or_404(PanierItem, id=item_id, panier=panier)
    if request.method == 'POST':
        item.delete()
    return redirect('ecommerce:cart')


@login_required
def update_cart_item(request, item_id):
    """
    Met à jour la quantité d'un article dans le panier.
    Si la requête est AJAX, renvoie le sous-total de la ligne mise à jour et le total général.
    """
    item = get_object_or_404(PanierItem, id=item_id, panier__utilisateur=request.user)
    if request.method == 'POST':
        try:
            new_quantity = int(request.POST.get('quantite', 1))
        except ValueError:
            new_quantity = 1

        if new_quantity > 0 and new_quantity <= item.produit.stock:
            item.quantite = new_quantity
            item.save()
        else:
            # On peut renvoyer une erreur ou fixer la quantité minimale
            item.quantite = 1
            item.save()

        # Calcul du sous‑total pour la ligne et du total général pour le panier
        line_total = float(item.produit.prix_affiche) * item.quantite
        panier = item.panier
        overall_total = sum(float(x.sous_total) for x in panier.items.all())
        response_data = {
            'line_total': f"{line_total:.2f}",
            'overall_total': f"{overall_total:.2f}",
            'quantity': item.quantite,
        }
        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
def update_cart(request):
    """
    Met à jour les quantités pour l'ensemble des items du panier.
    Chaque champ doit être nommé quantite_<item_id>.
    """
    if request.method == "POST":
        panier = get_object_or_404(Panier, utilisateur=request.user)
        for item in panier.items.all():
            new_qty = request.POST.get(f'quantite_{item.id}')
            try:
                new_qty = int(new_qty)
                if new_qty > 0 and new_qty <= item.produit.stock:
                    item.quantite = new_qty
                    item.save()
                elif new_qty <= 0:
                    item.delete()
            except (TypeError, ValueError):
                continue
        messages.success(request, "Le panier a été mis à jour.")
        return redirect('ecommerce:cart')
    return redirect('ecommerce:cart')

# ----------------- COMMANDE -----------------
@login_required
def checkout(request):
    # Récupérer le panier de l'utilisateur
    panier = get_object_or_404(Panier, utilisateur=request.user)
    items = panier.items.select_related("produit")
    if not items.exists():
        messages.error(request, "Votre panier est vide.")
        return redirect("ecommerce:shop")
    
    total = sum(item.sous_total for item in items)
    
    promo_total = None
    if "promo_total" in request.session:
        try:
            promo_total = Decimal(request.session["promo_total"])
        except Exception:
            promo_total = None

    final_total = promo_total if promo_total is not None else total

    if request.method == "POST":
        pays = request.POST.get('pays')
        prenom = request.POST.get('prenom')
        nom = request.POST.get('nom')
        adresse = request.POST.get('adresse')
        ville = request.POST.get('ville')
        code_postal = request.POST.get('code_postal')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        mode_paiement = request.POST.get('mode_paiement')
        
        with transaction.atomic():
            for item in items:
                if item.quantite > item.produit.stock:
                    messages.error(request, f"Stock insuffisant pour {item.produit.nom}.")
                    return redirect("ecommerce:cart")
            
            # Créer la commande avec l'état initial "en_cours" (vous pouvez adapter cet état)
            commande = Commande.objects.create(
                utilisateur=request.user,
                montant_total=final_total,
                etat="en_cours",
                pays=pays,
                prenom=prenom,
                nom=nom,
                adresse=adresse,
                ville=ville,
                code_postal=code_postal,
                email=email,
                telephone=telephone,
                mode_paiement=mode_paiement,
            )
            
            for item in items:
                DetailCommande.objects.create(
                    commande=commande,
                    produit=item.produit,
                    quantite=item.quantite,
                    sous_total=item.sous_total,
                )
                Produit.objects.filter(pk=item.produit.pk).update(
                    stock=F("stock") - item.quantite
                )
            
            items.delete()
            
            for key in ["promo_code", "promo_discount", "promo_reduction", "promo_total"]:
                request.session.pop(key, None)
            
        messages.success(request, "Commande validée avec succès!")
        # Redirection vers la page thankyou après la validation de la commande
        return redirect("ecommerce:thankyou")
    
    return render(request, "checkout.html", {
        "items": items,
        "total": total,
        "promo_total": promo_total,
    })

@login_required
def order_history(request):
    commandes = Commande.objects.filter(utilisateur=request.user)
    return render(request, "order_history.html", {"commandes": commandes})

@login_required
def order_detail(request, order_id):
    commande = get_object_or_404(Commande, id=order_id, utilisateur=request.user)
    return render(request, "order_detail.html", {"commande": commande})

@login_required
def request_cancellation(request, order_id):
    commande = get_object_or_404(Commande, id=order_id, utilisateur=request.user)
    # Vous pouvez restreindre cette action aux commandes en attente ou en cours.
    if commande.etat in ['en_attente', 'en_cours']:
        commande.etat = 'annulee'
        commande.save()
        messages.success(request, "Votre demande d'annulation a été enregistrée.")
    else:
        messages.error(request, "Cette commande ne peut pas être annulée à ce stade.")
    return redirect("ecommerce:order_history")


@login_required
def add_avis(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == "POST":
        try:
            note = int(request.POST.get("note", 5))
        except ValueError:
            note = 5
        commentaire = request.POST.get("commentaire", "")
        Avis.objects.create(
            utilisateur=request.user,
            produit=produit,
            note=note,
            commentaire=commentaire,
        )
    return redirect("ecommerce:product_detail", pk=pk)

@login_required
def clear_cart(request):
    """
    Vide entièrement le panier de l'utilisateur.
    """
    panier = get_object_or_404(Panier, utilisateur=request.user)
    if request.method == 'POST':
        panier.items.all().delete()
    return redirect('ecommerce:cart')


@login_required
def apply_promo_code(request):
    """
    Applique le code promo soumis.
    Si le code est valide et non utilisé, il calcule la réduction sur le total du panier,
    enregistre les valeurs dans la session et marque le code comme utilisé.
    """
    if request.method == "POST":
        promo_code_str = request.POST.get("promo_code", "").strip()
        if not promo_code_str:
            return JsonResponse({"error": "Veuillez saisir un code promo."}, status=400)
        try:
            promo = PromoCode.objects.get(code=promo_code_str, is_used=False)
        except PromoCode.DoesNotExist:
            return JsonResponse({"error": "Code promo invalide ou déjà utilisé."}, status=400)
        
        # Récupère ou crée le panier de l'utilisateur
        panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
        cart_items = panier.items.all()
        total = sum(item.sous_total for item in cart_items)  # total est un Decimal

        # Calcul de la remise
        discount_percentage = Decimal(promo.discount_percentage)
        reduction = total * (discount_percentage / Decimal("100"))
        new_total = total - reduction

        # Marquer le code promo comme utilisé
        promo.is_used = True
        promo.save()

        # Enregistrer dans la session (les valeurs sont enregistrées en chaînes pour la compatibilité)
        request.session["promo_code"] = promo.code
        request.session["promo_discount"] = str(discount_percentage)
        request.session["promo_reduction"] = f"{reduction:.2f}"
        request.session["promo_total"] = f"{new_total:.2f}"

        return JsonResponse({
            "promo_code": promo.code,
            "discount_percentage": promo.discount_percentage,
            "reduction": f"{reduction:.2f}",
            "new_total": f"{new_total:.2f}"
        })
    return JsonResponse({"error": "Méthode invalide."}, status=400)

@login_required
def request_cancellation(request, order_id):
    commande = get_object_or_404(Commande, id=order_id, utilisateur=request.user)
    if commande.etat in ['en_attente', 'en_cours']:
        commande.etat = 'annulee'
        commande.save()
        messages.success(request, "Votre demande d'annulation a été enregistrée.")
    else:
        messages.error(request, "Cette commande ne peut pas être annulée à ce stade.")
    return redirect("ecommerce:order_history")





@login_required
def toggle_like(request, pk):
    """Bascule le like pour le produit de pk pour l'utilisateur connecté."""
    produit = get_object_or_404(Produit, pk=pk)
    # Tente de récupérer le like existant
    favorite, created = Favorite.objects.get_or_create(user=request.user, produit=produit)
    if not created:
        # Déjà liké, on retire le like
        favorite.delete()
        liked = False
    else:
        liked = True

    # Pour une requête AJAX, on retourne le statut et le nombre total de likes
    if request.is_ajax():
        return JsonResponse({"liked": liked, "likes_count": produit.liked_by.count()})
    # Sinon, redirige vers la page précédente
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))