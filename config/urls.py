from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

from apps.serviteurs.views import account_settings, dashboard_home, deconnexion, public_home, serviteur_nouveau

urlpatterns = [
    path('', public_home, name='home'),
    path('inscription/', serviteur_nouveau, name='inscription'),
    path('connexion/', LoginView.as_view(template_name='serviteurs/login.html', redirect_authenticated_user=True), name='connexion'),
    path('deconnexion/', deconnexion, name='deconnexion'),
    path('dashboard/', dashboard_home, name='dashboard'),
    path('parametres/', account_settings, name='parametres'),
    path('admin/', admin.site.urls),
    path('serviteurs/', include('apps.serviteurs.urls', namespace='serviteurs')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
