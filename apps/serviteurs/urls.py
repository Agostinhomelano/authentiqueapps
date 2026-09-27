from django.urls import path

from .views import (
    export_csv,
    export_excel,
    serviteur_detail,
    serviteur_liste,
    serviteur_modifier,
    serviteur_nouveau,
    serviteur_success,
    serviteur_supprimer,
)

app_name = 'serviteurs'

urlpatterns = [
    path('', serviteur_liste, name='lister'),
    path('nouveau/', serviteur_nouveau, name='nouveau'),
    path('confirmation/<int:pk>/', serviteur_success, name='success'),
    path('<int:pk>/', serviteur_detail, name='detail'),
    path('<int:pk>/modifier/', serviteur_modifier, name='modifier'),
    path('<int:pk>/supprimer/', serviteur_supprimer, name='supprimer'),
    path('export/csv/', export_csv, name='export_csv'),
    path('export/excel/', export_excel, name='export_excel'),
]
