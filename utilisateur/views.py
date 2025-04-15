# utilisateur/views.py

from functools import lru_cache  # pour la fonction de test (à conserver si nécessaire)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .forms import CustomUserCreationForm, CustomProfileForm
from .models import CustomUser
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings

@lru_cache(maxsize=None)
def is_admin(user):
    """Teste si l'utilisateur est authentifié et a pour rôle 'admin'"""
    return user.is_authenticated and user.role == 'admin'

# Vues réservées aux administrateurs

@user_passes_test(is_admin)
def admin_register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            role_choice = form.cleaned_data.get('role')
            user = form.save(commit=False)
            if role_choice == 'admin':
                user.is_staff = True
                user.is_superuser = True
            else:
                user.is_staff = False
                user.is_superuser = False
            user.save()
            messages.success(request, "L'utilisateur a bien été créé.")
            return redirect('utilisateur:user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'admin_register.html', {'form': form})

@user_passes_test(is_admin)
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'user_list.html', {'users': users})

# Vues d'authentification

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')  # Redirection vers la page index après connexion
        else:
            messages.error(request, "Identifiants invalides.")
    return render(request, "login.html")



# Vue pour consultation et modification du profil
@login_required
def profile_view(request):
    """
    Affiche les informations en mode lecture seule par défaut.
    Un bouton "Modifier" permet de passer en mode édition.
    En mode édition, l'utilisateur peut mettre à jour ses informations.
    """
    # Vérification du paramètre GET pour le mode édition
    editing = request.GET.get('edit') == 'true'

    if request.method == 'POST':
        # Traitement du formulaire en mode édition
        form = CustomProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour.")
            return redirect('utilisateur:profile')  # Retour au mode lecture seule
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
            editing = True  # Rester en mode édition si erreurs
    else:
        form = CustomProfileForm(instance=request.user)

    context = {
        'form': form,
        'editing': editing,
        'user_info': request.user,  # Pour l'affichage en lecture seule
    }
    return render(request, 'profile.html', context)
# Vue pour le changement de mot de passe
@login_required
def password_change_view(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Votre mot de passe a bien été changé.")
            return redirect('utilisateur:profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, "password_change.html", {"form": form})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Désactive le compte jusqu’à validation
            user.save()

            # Construction du lien d'activation
            activation_link = request.build_absolute_uri(
                f"/utilisateur/activate/{user.email_token}/"
            )

            # Envoi de l'email d'activation
            send_mail(
                subject='Activation de votre compte Furni',
                message=f"Bonjour {user.username},\n\nCliquez ici pour activer votre compte : {activation_link}\n\nMerci !",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.success(request, "Un lien de confirmation a été envoyé à votre adresse email.")
            return redirect('utilisateur:login')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})
def activate_user(request, token):
    try:
        user = CustomUser.objects.get(email_token=token)
        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, "Votre compte a été activé avec succès.")
        else:
            messages.info(request, "Ce compte est déjà activé.")
    except CustomUser.DoesNotExist:
        messages.error(request, "Le lien d'activation est invalide.")

    return redirect('utilisateur:login')


def logout_view(request):
    logout(request)
    return redirect('utilisateur:login')


def newsletter_subscription(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')

        if not name or not email:
            messages.error(request, "Veuillez renseigner tous les champs.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Enregistrement dans la base de données
        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={'name': name}
        )
        if not created:
            # Optionnel: vous pouvez mettre à jour le nom si nécessaire
            subscription.name = name
            subscription.save()

        # Construction du message pour notification
        subject = "Nouvelle inscription à la Newsletter"
        message = f"Un nouvel abonné s'est inscrit à la newsletter :\n\nNom : {name}\nEmail : {email}"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [settings.EMAIL_HOST_USER]
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            messages.success(request, "Merci pour votre inscription à la Newsletter !")
        except Exception as e:
            messages.error(request, "Une erreur s'est produite lors de l'envoi de l'email.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

def contact(request):
    if request.method == 'POST':
        # Récupération des données du formulaire
        fname = request.POST.get('fname', '')
        lname = request.POST.get('lname', '')
        email = request.POST.get('email', '')
        message_body = request.POST.get('message', '')

        # Validation simple (à améliorer selon vos besoins)
        if not all([fname, lname, email, message_body]):
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('contact')  # ou réafficher la page avec les erreurs

        # Construction du sujet et du contenu de l'email
        subject = f"Message de Contact de {fname} {lname}"
        message_content = (
            f"Nom : {fname} {lname}\n"
            f"Email : {email}\n\n"
            f"Message :\n{message_body}"
        )
        # Vous pouvez définir l'expéditeur avec l'email du visiteur ou votre propre adresse
        from_email = settings.EMAIL_HOST_USER  # Par exemple, celui configuré dans vos settings
        recipient_list = [settings.EMAIL_HOST_USER]

        try:
            send_mail(subject, message_content, from_email, recipient_list, fail_silently=False)
            messages.success(request, "Votre message a bien été envoyé.")
        except Exception as e:
            messages.error(request, "Une erreur est survenue lors de l'envoi de votre message.")
            
        return redirect('contact')
        
    # GET : Afficher le formulaire
    return render(request, 'contact.html')
    """
    Cette vue traite la soumission du formulaire de newsletter du footer.
    Elle récupère le nom et l'email de l'utilisateur et envoie un email avec ces informations.
    """
    if request.method == "POST":
        # Récupération des données du formulaire
        name = request.POST.get('name')
        email = request.POST.get('email')

        if not name or not email:
            messages.error(request, "Veuillez renseigner tous les champs.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Construction du sujet et du corps du message
        subject = "Nouvelle inscription à la Newsletter"
        message = f"Un nouvel abonné s'est inscrit à la newsletter :\n\nNom : {name}\nEmail : {email}"
        # Remarque : Généralement, le from_email doit être l'email configuré sur votre serveur SMTP
        from_email = settings.EMAIL_HOST_USER
        # Vous pouvez définir recipient_list avec l'adresse à laquelle vous souhaitez recevoir ces notifications
        recipient_list = [settings.EMAIL_HOST_USER]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            messages.success(request, "Merci pour votre inscription à la Newsletter !")
        except Exception as e:
            messages.error(request, "Une erreur s'est produite lors de l'envoi de l'email.")
    return redirect(request.META.get('HTTP_REFERER', '/'))