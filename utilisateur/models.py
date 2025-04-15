from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('client', 'Client'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    is_active = models.BooleanField(default=False)  # Désactivation à la création
    email_token = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.email_token:
            self.email_token = get_random_string(50)
        super().save(*args, **kwargs)

# utilisateur/models.py (ou un fichier dédié comme newsletter/models.py)


class NewsletterSubscription(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(unique=True, verbose_name="Email")
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    active = models.BooleanField(default=True, verbose_name="Abonnement actif")

    def __str__(self):
        return f"{self.name} - {self.email}"