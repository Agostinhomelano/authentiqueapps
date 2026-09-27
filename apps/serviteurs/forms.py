import os

from django import forms
from django.core.exceptions import ValidationError

from .models import CurriculumMinisteriel, Serviteur


class ServiteurForm(forms.ModelForm):
    class Meta:
        model = Serviteur
        fields = [
            'eglise_nom',
            'region_apostolique',
            'district_apostolique',
            'district_ancien',
            'nom',
            'post_nom',
            'prenom',
            'lieu_naissance',
            'date_naissance',
            'etat_civil',
            'telephone',
            'email',
            'photo',
            'baptise_eau_date',
            'baptise_eau_par',
            'saint_sceau_date',
            'saint_sceau_par',
            'communaute_origine',
            'date_ordination',
            'ministere',
            'ordination_par',
            'champ_apostolique',
            'niveau_etudes',
            'domaine_etudes',
            'disponibilite',
            'lieu_remplissage',
            'date_remplissage',
            'signature',
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'baptise_eau_date': forms.DateInput(attrs={'type': 'date'}),
            'saint_sceau_date': forms.DateInput(attrs={'type': 'date'}),
            'date_ordination': forms.DateInput(attrs={'type': 'date'}),
            'date_remplissage': forms.DateInput(attrs={'type': 'date'}),
            'nom': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'post_nom': forms.TextInput(attrs={'placeholder': 'Post nom'}),
            'prenom': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'telephone': forms.TextInput(attrs={'placeholder': 'Ex: +243 ...'}),
            'email': forms.EmailInput(attrs={'placeholder': 'nom@domaine.com'}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if not photo:
            return photo

        max_size = 2 * 1024 * 1024
        if photo.size > max_size:
            raise ValidationError('La photo ne doit pas dépasser 2 Mo.')

        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        ext = os.path.splitext(photo.name)[1].lower()
        if ext not in allowed_extensions:
            raise ValidationError('Formats autorisés : JPG, JPEG, PNG, WEBP.')

        return photo


class CurriculumMinisterielForm(forms.ModelForm):
    class Meta:
        model = CurriculumMinisteriel
        fields = ['ordre', 'annee', 'libelle', 'details']
        widgets = {
            'ordre': forms.NumberInput(attrs={'min': 1}),
            'annee': forms.TextInput(attrs={'placeholder': 'Ex: 2024'}),
            'libelle': forms.TextInput(attrs={'placeholder': 'Ex: Pasteur, Responsable, ...'}),
            'details': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Détails complémentaires'}),
        }
