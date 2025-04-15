# utilisateur/urls.py

from django.urls import path
from . import views
from .views import contact 

app_name = 'utilisateur'

urlpatterns = [
    # Routes administrateurs
    path('admin/register/', views.admin_register_view, name='admin_register'),
    path('admin/users/', views.user_list, name='user_list'),

    # Routes d'authentification
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', contact, name='contact'),
    
    # Profil
    path('profile/', views.profile_view, name='profile'),
    path('activate/<str:token>/', views.activate_user, name='activate_user'),
    path('register/', views.register_view, name='register'),
    # Changement de mot de passe
    path('profile/password/', views.password_change_view, name='password_change'),
    path('newsletter/', views.newsletter_subscription, name='newsletter_subscription'),
]
