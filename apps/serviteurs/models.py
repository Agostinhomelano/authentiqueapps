from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower


class Disponibilite(models.TextChoices):
    TEMPS_PLEIN = 'temps_plein', 'Temps plein'
    PARTIELLE = 'partielle', 'Partielle'
    INDISPONIBLE = 'indisponible', 'Indisponible'


class EtatCivil(models.TextChoices):
    CELIBATAIRE = 'celibataire', 'Célibataire'
    MARIE = 'marie', 'Marié(e)'
    DIVORCE = 'divorce', 'Divorcé(e)'
    VEUF = 'veuf', 'Veuf/Veuve'
    UNION_LIBRE = 'union_libre', 'En union libre'


class Serviteur(models.Model):
    eglise_nom = models.CharField('Église', max_length=200, default='Église Nouvel Apostolat Authentique en RDC')
    region_apostolique = models.CharField('Région Apostolique', max_length=150, blank=True)
    district_apostolique = models.CharField('District Apostolique de', max_length=150, blank=True)
    district_ancien = models.CharField('District d\'Ancien de', max_length=150, blank=True)

    nom = models.CharField('Nom de famille', max_length=100)
    post_nom = models.CharField('Post nom', max_length=100, blank=True)
    prenom = models.CharField('Prénom', max_length=100)
    lieu_naissance = models.CharField('Lieu de naissance', max_length=150, blank=True)
    date_naissance = models.DateField('Date de naissance', blank=True, null=True)
    etat_civil = models.CharField('État civil', max_length=30, choices=EtatCivil.choices, blank=True)
    adresse = models.CharField('Adresse', max_length=255, blank=True)
    telephone = models.CharField('Téléphone (WhatsApp)', max_length=30)
    email = models.EmailField('E-mail', blank=True)
    photo = models.ImageField('Photo', upload_to='photos/', blank=True, null=True)

    baptise_eau_date = models.DateField('Date de baptême d\'eau', blank=True, null=True)
    baptise_eau_par = models.CharField('Personne ayant effectué le baptême d\'eau', max_length=200, blank=True)
    saint_sceau_date = models.DateField('Date de Saint Scellé', blank=True, null=True)
    saint_sceau_par = models.CharField('Personne ayant effectué le Saint Scellé', max_length=200, blank=True)
    communaute_origine = models.CharField('Communauté d\'origine', max_length=150, blank=True)
    date_ordination = models.DateField('Date d\'ordination actuelle', blank=True, null=True)
    ministere = models.CharField('Ministère', max_length=150, blank=True)
    ordination_par = models.CharField('Personne ayant effectué l\'ordination', max_length=200, blank=True)
    champ_apostolique = models.CharField('Champ Apostolique Affecté', max_length=150, blank=True)

    niveau_etudes = models.CharField('Niveau', max_length=120, blank=True)
    domaine_etudes = models.CharField('Domaine', max_length=150, blank=True)

    disponibilite = models.CharField('Disponibilité à l\'œuvre', max_length=30, choices=Disponibilite.choices, default=Disponibilite.TEMPS_PLEIN)

    lieu_remplissage = models.CharField('Lieu de remplissage', max_length=150, blank=True)
    date_remplissage = models.DateField('Date', blank=True, null=True)
    signature = models.CharField('Signature', max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nom', 'post_nom', 'prenom']
        verbose_name = 'Serviteur de Dieu'
        verbose_name_plural = 'Serviteurs de Dieu'
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                condition=~Q(email=''),
                name='serviteur_email_unique_ci',
            ),
            models.UniqueConstraint(
                fields=['telephone'],
                name='serviteur_telephone_unique',
            ),
            models.UniqueConstraint(
                fields=['nom', 'post_nom', 'prenom', 'date_naissance'],
                name='serviteur_identite_unique',
            ),
        ]

    def __str__(self):
        return self.nom_complet

    @property
    def nom_complet(self):
        parties = [self.nom, self.post_nom, self.prenom]
        return ' '.join(partie for partie in parties if partie)


class CurriculumMinisteriel(models.Model):
    serviteur = models.ForeignKey(Serviteur, related_name='curriculum', on_delete=models.CASCADE, verbose_name='Serviteur')
    ordre = models.PositiveIntegerField('Ordre', default=1)
    annee = models.CharField('Année', max_length=10, blank=True)
    libelle = models.CharField('Libellé', max_length=200)
    details = models.CharField('Détails', max_length=255, blank=True)

    class Meta:
        ordering = ['-annee', 'ordre']
        verbose_name = 'Parcours ministériel'
        verbose_name_plural = 'Parcours ministériels'

    def __str__(self):
        return f'{self.ordre} - {self.libelle}'
