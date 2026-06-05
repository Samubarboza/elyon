from axes.utils import reset
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.users.forms import UserCreateForm
from apps.users.models import Company, Plan, User
from apps.users.selectors import count_active_users
from apps.users.services import UserActionError, create_user, set_user_active


VALID_PASSWORD = 'ClaveSegura123'


def build_create_form(username):
    return UserCreateForm(data={'username': username, 'password1': VALID_PASSWORD, 'password2': VALID_PASSWORD})


class PlanLimitTests(TestCase):

    def setUp(self):
        self.company = Company.get_config()
        self.company.plan = Plan.objects.get(name='Starter')
        self.company.save()

    def test_create_user_succeeds_below_limit(self):
        user_form = build_create_form('nuevo')
        self.assertTrue(user_form.is_valid())
        created_user = create_user(user_form)
        self.assertEqual(count_active_users(), 1)
        self.assertTrue(created_user.check_password(VALID_PASSWORD))

    def test_create_user_blocked_when_limit_reached(self):
        for index in range(self.company.max_users):
            User.objects.create_user(username='user' + str(index), password=VALID_PASSWORD)
        user_form = build_create_form('extra')
        self.assertTrue(user_form.is_valid())
        with self.assertRaises(UserActionError):
            create_user(user_form)
        self.assertEqual(count_active_users(), self.company.max_users)


class UserBusinessRulesTests(TestCase):

    # Los usuarios del sistema nunca entran al panel de administracion de Django
    def test_created_user_is_not_staff_and_not_superuser(self):
        user_form = build_create_form('miembro')
        self.assertTrue(user_form.is_valid())
        created_user = create_user(user_form)
        self.assertFalse(created_user.is_staff)
        self.assertFalse(created_user.is_superuser)

    def test_cannot_deactivate_main_admin(self):
        main_admin = User.objects.create_user(username='admin', password=VALID_PASSWORD, is_main_admin=True)
        with self.assertRaises(UserActionError):
            set_user_active(main_admin, False)
        main_admin.refresh_from_db()
        self.assertTrue(main_admin.is_active)


class AccessControlTests(TestCase):

    def setUp(self):
        self.member = User.objects.create_user(username='miembro', password=VALID_PASSWORD)
        self.user_list_url = reverse('users:user_list')

    def test_user_without_permission_gets_forbidden(self):
        self.client.force_login(self.member)
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, 403)

    def test_user_with_permission_can_access(self):
        view_user_permission = Permission.objects.get(codename='view_user')
        self.member.user_permissions.add(view_user_permission)
        self.client.force_login(self.member)
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_access_is_logged(self):
        self.client.force_login(self.member)
        with self.assertLogs('apps.users', level='WARNING') as captured_logs:
            self.client.get(self.user_list_url)
        self.assertIn('Acceso no autorizado', ''.join(captured_logs.output))


class AuthenticationTests(TestCase):

    def setUp(self):
        reset()
        self.login_url = reverse('users:login')

    def test_inactive_user_cannot_login(self):
        User.objects.create_user(username='inactivo', password=VALID_PASSWORD, is_active=False)
        self.client.post(self.login_url, {'username': 'inactivo', 'password': VALID_PASSWORD})
        self.assertNotIn('_auth_user_id', self.client.session)

    # Tras alcanzar el limite de intentos fallidos axes bloquea el acceso
    def test_login_locks_after_failed_attempts(self):
        bad_credentials = {'username': 'alguien', 'password': 'claveincorrecta'}
        for _ in range(5):
            self.client.post(self.login_url, bad_credentials)
        locked_response = self.client.post(self.login_url, bad_credentials)
        self.assertEqual(locked_response.status_code, 429)
