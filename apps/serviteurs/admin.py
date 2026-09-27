from django.contrib import admin
from django.utils.html import format_html

from .models import CurriculumMinisteriel, Serviteur


@admin.register(CurriculumMinisteriel)
class CurriculumMinisterielAdmin(admin.ModelAdmin):
    list_display = ('serviteur', 'ordre', 'libelle', 'annee')
    list_filter = ('annee',)
    search_fields = ('libelle', 'serviteur__nom', 'serviteur__post_nom', 'serviteur__prenom')


@admin.register(Serviteur)
class ServiteurAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'telephone', 'ministere', 'champ_apostolique', 'disponibilite', 'photo_preview')
    search_fields = ('nom', 'post_nom', 'prenom', 'telephone', 'email')
    list_filter = ('ministere', 'champ_apostolique', 'disponibilite', 'etat_civil')
    fieldsets = (
        ('Informations de l\'église', {
            'fields': ('eglise_nom', 'region_apostolique', 'district_apostolique', 'district_ancien')
        }),
        ('Identité', {
            'fields': ('nom', 'post_nom', 'prenom', 'lieu_naissance', 'date_naissance', 'etat_civil', 'telephone', 'email', 'photo')
        }),
        ('Ministère', {
            'fields': ('baptise_eau_date', 'baptise_eau_par', 'saint_sceau_date', 'saint_sceau_par', 'communaute_origine', 'date_ordination', 'ministere', 'ordination_par', 'champ_apostolique')
        }),
        ('Études faites', {
            'fields': ('niveau_etudes', 'domaine_etudes')
        }),
        ('Autres', {
            'fields': ('disponibilite',)
        }),
        ('Informations finales', {
            'fields': ('lieu_remplissage', 'date_remplissage', 'signature')
        }),
    )
    readonly_fields = ('photo_preview',)

    def photo_preview(self, obj):
        if not obj.photo:
            return 'Aucune photo'
        return format_html('<img src="{}" style="max-height:60px; border-radius:8px;" />', obj.photo.url)

    photo_preview.short_description = 'Photo'
