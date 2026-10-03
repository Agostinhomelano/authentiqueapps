from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.serviteurs.forms import ServiteurForm
from apps.serviteurs.models import CurriculumMinisteriel, Serviteur


class AccountSettingsViewTest(TestCase):
    def test_account_settings_requires_login(self):
        response = self.client.get(reverse('parametres'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('connexion'), response.url)

    def test_account_settings_updates_current_user(self):
        user = get_user_model().objects.create_user(
            username='responsable',
            password='test-password-123',
        )
        self.client.force_login(user)

        page = self.client.get(reverse('parametres'))
        self.assertContains(page, 'Paramètres')
        self.assertContains(page, 'Préférences de l’application')
        self.assertContains(page, 'name="old_password"')
        self.assertContains(page, 'name="new_password1"')
        self.assertContains(page, 'name="new_password2"')

        response = self.client.post(
            reverse('parametres'),
            {
                'first_name': 'Jean',
                'last_name': 'Mabiala',
                'username': 'jean.mabiala',
                'email': 'jean@example.com',
            },
        )

        self.assertRedirects(response, reverse('parametres'))
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Jean')
        self.assertEqual(user.last_name, 'Mabiala')
        self.assertEqual(user.username, 'jean.mabiala')
        self.assertEqual(user.email, 'jean@example.com')

    def test_account_settings_changes_password_without_ending_session(self):
        user = get_user_model().objects.create_user(
            username='responsable',
            password='Old-Password-4821',
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse('parametres'),
            {
                'form_type': 'password',
                'old_password': 'Old-Password-4821',
                'new_password1': 'New-Password-9821',
                'new_password2': 'New-Password-9821',
            },
        )

        self.assertRedirects(response, reverse('parametres'))
        user.refresh_from_db()
        self.assertTrue(user.check_password('New-Password-9821'))
        self.assertEqual(self.client.get(reverse('parametres')).status_code, 200)


class DashboardNavigationTest(TestCase):
    def test_dashboard_renders_admin_menu_for_logged_in_user(self):
        user = get_user_model().objects.create_user(username='responsable')
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard'))

        self.assertContains(response, 'id="main-nav"')
        self.assertContains(response, 'aria-controls="main-nav"')
        self.assertContains(response, 'ENAA')
        self.assertContains(response, 'Exportations')
        self.assertContains(response, 'Paramètres')
        self.assertContains(response, 'Déconnexion')
        self.assertContains(response, 'nav-logout-button')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertNotContains(response, 'admin-menu-toggle')
        self.assertNotContains(response, 'Django Admin')

    def test_django_admin_link_is_reserved_for_superusers(self):
        user = get_user_model().objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='test-password-123',
        )
        self.client.force_login(user)

        self.assertContains(self.client.get(reverse('dashboard')), 'Django Admin')


class PublicNavigationTest(TestCase):
    def test_public_home_only_exposes_public_navigation(self):
        response = self.client.get(reverse('home'))

        self.assertContains(response, 'Accueil')
        self.assertContains(response, "S'inscrire")
        self.assertContains(response, 'home-hero')
        self.assertNotContains(response, 'Connexion')
        self.assertNotContains(response, 'Espace responsable')
        self.assertNotContains(response, 'Django Admin')

    def test_login_page_has_no_public_header_or_footer(self):
        response = self.client.get(reverse('connexion'))

        self.assertNotContains(response, 'site-header')
        self.assertNotContains(response, 'site-footer')
        self.assertNotContains(response, "S'inscrire")
        self.assertNotContains(response, 'Accueil')


class LogoutViewTest(TestCase):
    def test_logout_post_ends_session_and_redirects_home(self):
        user = get_user_model().objects.create_user(username='responsable')
        self.client.force_login(user)

        response = self.client.post(reverse('deconnexion'))

        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_get_does_not_end_session(self):
        user = get_user_model().objects.create_user(username='responsable')
        self.client.force_login(user)

        response = self.client.get(reverse('deconnexion'))

        self.assertEqual(response.status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)


class ServiteurModelTest(TestCase):
    def test_etat_civil_uses_select_widget(self):
        field = ServiteurForm()['etat_civil']

        self.assertIn('<select', str(field))

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


class ServiteurDuplicateValidationTest(TestCase):
    def make_form_data(self, **overrides):
        data = {
            'eglise_nom': 'Église ENAA',
            'nom': 'Kabila',
            'post_nom': 'Mwamba',
            'prenom': 'Jean',
            'date_naissance': '1990-03-12',
            'telephone': '+243811111111',
            'email': 'jean@example.com',
            'disponibilite': 'temps_plein',
        }
        data.update(overrides)
        return data

    def test_rejects_duplicate_phone_number(self):
        Serviteur.objects.create(
            nom='Autre',
            prenom='Personne',
            telephone='+243811111111',
        )
        form = ServiteurForm(self.make_form_data())

        self.assertFalse(form.is_valid())
        self.assertIn('telephone', form.errors)

    def test_rejects_duplicate_email_ignoring_case(self):
        Serviteur.objects.create(
            nom='Autre',
            prenom='Personne',
            telephone='+243822222222',
            email='Jean@Example.com',
        )
        form = ServiteurForm(self.make_form_data(telephone='+243833333333'))

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_rejects_duplicate_identity_and_birth_date(self):
        Serviteur.objects.create(
            nom='Kabila',
            post_nom='Mwamba',
            prenom='Jean',
            date_naissance='1990-03-12',
            telephone='+243844444444',
        )
        form = ServiteurForm(
            self.make_form_data(telephone='+243855555555', email='different@example.com')
        )

        self.assertFalse(form.is_valid())
        self.assertIn('nom', form.errors)


class ServiteurFormTemplateTest(TestCase):
    def test_family_name_is_not_repeated_in_ministry_step(self):
        response = self.client.get(reverse('inscription'))
        html = response.content.decode()

        self.assertEqual(html.count('Nom de famille'), 1)
        self.assertIn('id_adresse', html)
        self.assertIn('id_communaute_origine', html)
        self.assertIn('curriculum-add-toggle', html)
        self.assertNotIn('type="checkbox"', html)


class CurriculumOrderingTest(TestCase):
    def test_registration_saves_curriculum_in_descending_year_order(self):
        data = {
            'eglise_nom': 'Église ENAA',
            'nom': 'Kabila',
            'prenom': 'Jean',
            'telephone': '+243899900011',
            'adresse': '12, avenue de la Paix',
            'disponibilite': 'temps_plein',
            'curriculum-TOTAL_FORMS': '2',
            'curriculum-INITIAL_FORMS': '0',
            'curriculum-MIN_NUM_FORMS': '0',
            'curriculum-MAX_NUM_FORMS': '1000',
            'curriculum-0-id': '',
            'curriculum-0-ordre': '2',
            'curriculum-0-annee': '2019',
            'curriculum-0-libelle': 'Diacre',
            'curriculum-0-details': '',
            'curriculum-1-id': '',
            'curriculum-1-ordre': '1',
            'curriculum-1-annee': '2025',
            'curriculum-1-libelle': 'Pasteur',
            'curriculum-1-details': '',
        }

        response = self.client.post(reverse('inscription'), data)

        self.assertEqual(response.status_code, 302)
        serviteur = Serviteur.objects.get(telephone='+243899900011')
        self.assertEqual(serviteur.adresse, '12, avenue de la Paix')
        self.assertEqual(
            list(serviteur.curriculum.values_list('annee', flat=True)),
            ['2025', '2019'],
        )
        self.assertEqual(
            list(serviteur.curriculum.values_list('ordre', flat=True)),
            [1, 2],
        )
