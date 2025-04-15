from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# JWT Auth
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Swagger
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Vues locales
from ecommerce import views as ecommerce_views 
from utilisateur import views as user_views

# Vue racine de l'API
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def api_root(request):
    return Response({
        "Blog API": "/api/blog/",
        "Ecommerce API": "/api/ecommerce/",
        "Utilisateur API": "/api/utilisateur/",
        "Swagger": "/swagger/",
        "ReDoc": "/redoc/",
    })

# Swagger Schema View
schema_view = get_schema_view(
   openapi.Info(
      title="API Empire of Meubles Africains",
      default_version='v1',
      description="Documentation complète de l’API pour blog, ecommerce et utilisateurs.",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Pages front
    path('index/', ecommerce_views.index, name='index'),
    path('', user_views.login_view, name='login'),
    path('about/', TemplateView.as_view(template_name="about.html"), name="about"),
    path('contact/', TemplateView.as_view(template_name="contact.html"), name="contact"),
    path('cart/', TemplateView.as_view(template_name="cart.html"), name="cart"),
    path('chatBot/', TemplateView.as_view(template_name="chatBot.html"), name="chatBot"),
    path('checkout/', TemplateView.as_view(template_name="checkout.html"), name="checkout"),
    path('services/', TemplateView.as_view(template_name="services.html"), name="services"),
    path('shop/', ecommerce_views.shop, name="shop"),
    path('thankyou/', TemplateView.as_view(template_name="thankyou.html"), name="thankyou"),
    path('test/', TemplateView.as_view(template_name="test.html"), name="test"),

    # Apps classiques
    path('utilisateur/', include('utilisateur.urls')),
    path('blog/', include('blog.urls')),
    path('ecommerce/', include('ecommerce.urls')),

    # Entrée API (vue racine + sous-routes)
    path('api/', api_root, name='api-root'),
    path('api/blog/', include('blog.api_urls')),
    path('api/ecommerce/', include('ecommerce.api_urls')),
    path('api/utilisateur/', include('utilisateur.api_urls')),

    # Auth JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Documentation Swagger & Redoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # CKEditor
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

# Gestion des fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
