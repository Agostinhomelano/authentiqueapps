import csv
import io

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import AccountSettingsForm, CurriculumMinisterielForm, ServiteurForm
from .models import CurriculumMinisteriel, Serviteur

CurriculumFormSet = inlineformset_factory(
    Serviteur,
    CurriculumMinisteriel,
    form=CurriculumMinisterielForm,
    extra=0,
    can_delete=True,
    fields=('ordre', 'annee', 'libelle', 'details'),
)


def save_curriculum_formset(formset):
    formset.save()
    entries = sorted(
        formset.instance.curriculum.all(),
        key=lambda entry: (entry.annee, entry.pk),
        reverse=True,
    )
    for position, entry in enumerate(entries, start=1):
        if entry.ordre != position:
            CurriculumMinisteriel.objects.filter(pk=entry.pk).update(ordre=position)


def serviteur_liste(request):
    query = request.GET.get('q', '').strip()
    ministere = request.GET.get('ministere', '').strip()
    champ = request.GET.get('champ', '').strip()
    date_filter = request.GET.get('date', '').strip()

    serviteurs = Serviteur.objects.all()

    if query:
        serviteurs = serviteurs.filter(
            Q(nom__icontains=query)
            | Q(post_nom__icontains=query)
            | Q(prenom__icontains=query)
            | Q(telephone__icontains=query)
            | Q(ministere__icontains=query)
            | Q(champ_apostolique__icontains=query)
        ).distinct()

    if ministere:
        serviteurs = serviteurs.filter(ministere__icontains=ministere)

    if champ:
        serviteurs = serviteurs.filter(champ_apostolique__icontains=champ)

    if date_filter:
        serviteurs = serviteurs.filter(created_at__date=date_filter)

    ministeres = Serviteur.objects.exclude(ministere='').values_list('ministere', flat=True).distinct()
    champs = Serviteur.objects.exclude(champ_apostolique='').values_list('champ_apostolique', flat=True).distinct()

    return render(
        request,
        'serviteurs/serviteur_list.html',
        {
            'serviteurs': serviteurs,
            'query': query,
            'ministere': ministere,
            'champ': champ,
            'date_filter': date_filter,
            'ministeres': ministeres,
            'champs': champs,
        },
    )


def public_home(request):
    return render(request, 'serviteurs/public_home.html')


@require_POST
def deconnexion(request):
    logout(request)
    return redirect('home')


def serviteur_nouveau(request):
    if request.method == 'POST':
        form = ServiteurForm(request.POST, request.FILES)
        formset = CurriculumFormSet(request.POST, instance=Serviteur())
        if form.is_valid() and formset.is_valid():
            serviteur = form.save()
            formset.instance = serviteur
            save_curriculum_formset(formset)
            messages.success(request, 'Le serviteur a été enregistré avec succès.')
            return redirect('serviteurs:success', pk=serviteur.pk)
    else:
        form = ServiteurForm()
        formset = CurriculumFormSet(instance=Serviteur())
    return render(request, 'serviteurs/serviteur_form.html', {'form': form, 'formset': formset, 'title': 'Nouveau serviteur'})


@login_required
def serviteur_modifier(request, pk):
    serviteur = get_object_or_404(Serviteur, pk=pk)
    if request.method == 'POST':
        form = ServiteurForm(request.POST, request.FILES, instance=serviteur)
        formset = CurriculumFormSet(request.POST, instance=serviteur)
        if form.is_valid() and formset.is_valid():
            serviteur = form.save()
            save_curriculum_formset(formset)
            messages.success(request, 'Les informations du serviteur ont été mises à jour.')
            return redirect('serviteurs:success', pk=serviteur.pk)
    else:
        form = ServiteurForm(instance=serviteur)
        formset = CurriculumFormSet(instance=serviteur)
    return render(request, 'serviteurs/serviteur_form.html', {'form': form, 'formset': formset, 'serviteur': serviteur, 'title': 'Modifier le serviteur'})


@login_required
def dashboard_home(request):
    total = Serviteur.objects.count()
    today = Serviteur.objects.filter(created_at__date=timezone.localdate()).count()
    this_week = Serviteur.objects.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7)).count()
    this_month = Serviteur.objects.filter(
        created_at__year=timezone.now().year,
        created_at__month=timezone.now().month,
    ).count()
    recent = Serviteur.objects.order_by('-created_at')[:5]
    return render(
        request,
        'serviteurs/dashboard.html',
        {
            'total': total,
            'today': today,
            'this_week': this_week,
            'this_month': this_month,
            'recent': recent,
        },
    )


@login_required
def account_settings(request):
    profile_form = AccountSettingsForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if request.POST.get('form_type') == 'password':
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Votre mot de passe a été modifié.')
                return redirect('parametres')
        else:
            profile_form = AccountSettingsForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Vos informations ont été mises à jour.')
                return redirect('parametres')

    return render(
        request,
        'serviteurs/account_settings.html',
        {
            'form': profile_form,
            'password_form': password_form,
            'account_role': (
                'Superadministrateur'
                if request.user.is_superuser
                else 'Administrateur' if request.user.is_staff else 'Utilisateur'
            ),
            'account_status': 'Actif' if request.user.is_active else 'Désactivé',
            'account_username': request.user.username,
            'account_display_name': request.user.get_full_name() or request.user.username,
            'account_initial': (request.user.get_full_name() or request.user.username)[0].upper(),
            'account_language': 'Français' if settings.LANGUAGE_CODE.startswith('fr') else settings.LANGUAGE_CODE,
            'account_timezone': settings.TIME_ZONE.rsplit('/', maxsplit=1)[-1].replace('_', ' '),
            'password_help_text': password_form.fields['new_password1'].help_text,
        },
    )


def serviteur_success(request, pk):
    serviteur = get_object_or_404(Serviteur, pk=pk)
    return render(request, 'serviteurs/serviteur_success.html', {'serviteur': serviteur})


@login_required
def serviteur_supprimer(request, pk):
    serviteur = get_object_or_404(Serviteur, pk=pk)
    if request.method == 'POST':
        serviteur.delete()
        messages.success(request, 'Le serviteur a été supprimé.')
        return redirect('serviteurs:lister')
    return render(request, 'serviteurs/serviteur_confirm_delete.html', {'serviteur': serviteur})


def serviteur_detail(request, pk):
    serviteur = get_object_or_404(Serviteur, pk=pk)
    curriculum = serviteur.curriculum.all()
    return render(request, 'serviteurs/serviteur_detail.html', {'serviteur': serviteur, 'curriculum': curriculum})


def exportations(request):
    return render(request, 'serviteurs/exportations.html')


def export_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="serviteurs.csv"'

    output = io.StringIO(newline='')
    writer = csv.writer(output, delimiter=';', dialect='excel')
    writer.writerow([
        'Nom', 'Post nom', 'Prénom', 'Lieu de naissance', 'Date de naissance', 'Adresse',
        'État civil', 'Téléphone', 'E-mail', 'Photo', 'Date de baptême d\'eau',
        'Personne ayant effectué le baptême d\'eau', 'Date de Saint Scellé',
        'Personne ayant effectué le Saint Scellé', 'Communauté d\'origine',
        'Date d\'ordination actuelle', 'Ministère', 'Personne ayant effectué l\'ordination',
        'Champ Apostolique Affecté', 'Niveau', 'Domaine', 'Disponibilité',
        'Lieu de remplissage', 'Date', 'Signature'
    ])

    for serviteur in Serviteur.objects.all():
        writer.writerow([
            serviteur.nom,
            serviteur.post_nom,
            serviteur.prenom,
            serviteur.lieu_naissance,
            serviteur.date_naissance,
            serviteur.adresse,
            serviteur.get_etat_civil_display(),
            serviteur.telephone,
            serviteur.email,
            serviteur.photo.name if serviteur.photo else '',
            serviteur.baptise_eau_date,
            serviteur.baptise_eau_par,
            serviteur.saint_sceau_date,
            serviteur.saint_sceau_par,
            serviteur.communaute_origine,
            serviteur.date_ordination,
            serviteur.ministere,
            serviteur.ordination_par,
            serviteur.champ_apostolique,
            serviteur.niveau_etudes,
            serviteur.domaine_etudes,
            serviteur.get_disponibilite_display(),
            serviteur.lieu_remplissage,
            serviteur.date_remplissage,
            serviteur.signature,
        ])

    response.write('\ufeff')
    response.write(output.getvalue())
    return response


def export_excel(request):
    try:
        from openpyxl import Workbook
    except ImportError:
        messages.error(request, 'Le support Excel n\'est pas disponible dans l\'environnement actuel.')
        return redirect('serviteurs:lister')

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Serviteurs'
    headers = [
        'Nom', 'Post nom', 'Prénom', 'Lieu de naissance', 'Date de naissance', 'Adresse',
        'État civil', 'Téléphone', 'E-mail', 'Date de baptême d\'eau',
        'Personne ayant effectué le baptême d\'eau', 'Date de Saint Scellé',
        'Personne ayant effectué le Saint Scellé', 'Communauté d\'origine',
        'Date d\'ordination actuelle', 'Ministère', 'Personne ayant effectué l\'ordination',
        'Champ Apostolique Affecté', 'Niveau', 'Domaine', 'Disponibilité',
        'Lieu de remplissage', 'Date', 'Signature'
    ]
    sheet.append(headers)

    for serviteur in Serviteur.objects.all():
        sheet.append([
            serviteur.nom,
            serviteur.post_nom,
            serviteur.prenom,
            serviteur.lieu_naissance,
            serviteur.date_naissance,
            serviteur.adresse,
            serviteur.get_etat_civil_display(),
            serviteur.telephone,
            serviteur.email,
            serviteur.baptise_eau_date,
            serviteur.baptise_eau_par,
            serviteur.saint_sceau_date,
            serviteur.saint_sceau_par,
            serviteur.communaute_origine,
            serviteur.date_ordination,
            serviteur.ministere,
            serviteur.ordination_par,
            serviteur.champ_apostolique,
            serviteur.niveau_etudes,
            serviteur.domaine_etudes,
            serviteur.get_disponibilite_display(),
            serviteur.lieu_remplissage,
            serviteur.date_remplissage,
            serviteur.signature,
        ])

    output = io.BytesIO()
    workbook.save(output)
    response = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="serviteurs.xlsx"'
    return response
