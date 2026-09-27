from django.test import TestCase

from apps.serviteurs.models import CurriculumMinisteriel, Serviteur


class ServiteurModelTest(TestCase):
    def test_create_serviteur_with_ministerial_curriculum(self):
        serviteur = Serviteur.objects.create(
            nom='Dupont',
            post_nom='Mokolo',
            prenom='Jean',
            lieu_naissance='Kinshasa',
            date_naissance='1990-01-15',
            etat_civil='celibataire',
            telephone='0999999999',
            email='jean@example.com',
            baptise_eau_date='2010-01-01',
            baptise_eau_par='Pasteur X',
            saint_sceau_date='2012-01-01',
            saint_sceau_par='Pasteur Y',
            communaute_origine='Communauté A',
            date_ordination='2015-01-01',
            ministere='Pasteur',
            ordination_par='Supérieur',
            champ_apostolique='Kinshasa',
            disponibilite='temps_plein',
            lieu_remplissage='Goma',
            date_remplissage='2024-06-01',
        )

        CurriculumMinisteriel.objects.create(
            serviteur=serviteur,
            ordre=1,
            annee='2014',
            libelle='Prêcheur',
        )

        self.assertEqual(serviteur.nom_complet, 'Dupont Mokolo Jean')
        self.assertEqual(serviteur.curriculum.count(), 1)
        self.assertEqual(serviteur.curriculum.first().libelle, 'Prêcheur')
