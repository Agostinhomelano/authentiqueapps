import os

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import CurriculumMinisteriel, Serviteur


class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username', 'email')


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
            'adresse',
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
            'etat_civil': forms.Select,
            'adresse': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Rue, quartier, commune...'}),
            'disponibilite': forms.RadioSelect,
            'photo': forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png,image/webp', 'class': 'photo-input'}),
            'nom': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'post_nom': forms.TextInput(attrs={'placeholder': 'Post nom'}),
            'prenom': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'telephone': forms.TextInput(attrs={'placeholder': 'Ex: +243 ...'}),
            'email': forms.EmailInput(attrs={'placeholder': 'nom@domaine.com'}),
        }

    def clean_telephone(self):
        telephone = self.cleaned_data['telephone']
        duplicates = Serviteur.objects.filter(telephone=telephone)
        if self.instance.pk:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise ValidationError('Ce numéro de téléphone est déjà utilisé.')
        return telephone

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email:
            duplicates = Serviteur.objects.filter(email__iexact=email)
            if self.instance.pk:
                duplicates = duplicates.exclude(pk=self.instance.pk)
            if duplicates.exists():
                raise ValidationError('Cette adresse e-mail est déjà utilisée.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        nom = cleaned_data.get('nom')
        post_nom = cleaned_data.get('post_nom', '')
        prenom = cleaned_data.get('prenom')
        date_naissance = cleaned_data.get('date_naissance')

        if nom and prenom and date_naissance:
            duplicates = Serviteur.objects.filter(
                nom=nom,
                post_nom=post_nom,
                prenom=prenom,
                date_naissance=date_naissance,
            )
            if self.instance.pk:
                duplicates = duplicates.exclude(pk=self.instance.pk)
            if duplicates.exists():
                self.add_error(
                    'nom',
                    'Un serviteur portant cette identité et cette date de naissance est déjà enregistré.',
                )

        return cleaned_data

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
            'ordre': forms.HiddenInput(),
            'annee': forms.TextInput(attrs={'placeholder': 'Ex: 2024'}),
            'libelle': forms.TextInput(attrs={'placeholder': 'Ex: Pasteur, Responsable, ...'}),
            'details': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Détails complémentaires'}),
        }
