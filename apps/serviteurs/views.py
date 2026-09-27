import csv
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CurriculumMinisterielForm, ServiteurForm
from .models import CurriculumMinisteriel, Serviteur

CurriculumFormSet = inlineformset_factory(
    Serviteur,
    CurriculumMinisteriel,
    form=CurriculumMinisterielForm,
    extra=2,
    can_delete=True,
    fields=('ordre', 'annee', 'libelle', 'details'),
)


def serviteur_liste(request):
    query = request.GET.get('q', '').strip()
    serviteurs = Serviteur.objects.all()
    if query:
        serviteurs = serviteurs.filter(
            Q(nom__icontains=query)
            | Q(post_nom__icontains=query)
            | Q(prenom__icontains=query)
            | Q(telephone__icontains=query)
            | Q(ministere__icontains=query)
        ).distinct()
    return render(request, 'serviteurs/serviteur_list.html', {'serviteurs': serviteurs, 'query': query})


@login_required
def serviteur_nouveau(request):
    if request.method == 'POST':
        form = ServiteurForm(request.POST, request.FILES)
        formset = CurriculumFormSet(request.POST, instance=Serviteur())
        if form.is_valid() and formset.is_valid():
            serviteur = form.save()
            formset.instance = serviteur
            formset.save()
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
            formset.save()
            messages.success(request, 'Les informations du serviteur ont été mises à jour.')
            return redirect('serviteurs:success', pk=serviteur.pk)
    else:
        form = ServiteurForm(instance=serviteur)
        formset = CurriculumFormSet(instance=serviteur)
    return render(request, 'serviteurs/serviteur_form.html', {'form': form, 'formset': formset, 'serviteur': serviteur, 'title': 'Modifier le serviteur'})


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


def export_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="serviteurs.csv"'

    output = io.StringIO(newline='')
    writer = csv.writer(output, delimiter=';', dialect='excel')
    writer.writerow([
        'Nom', 'Post nom', 'Prénom', 'Lieu de naissance', 'Date de naissance',
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
        'Nom', 'Post nom', 'Prénom', 'Lieu de naissance', 'Date de naissance',
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
