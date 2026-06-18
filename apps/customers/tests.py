from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.customers.forms import CustomerForm
from apps.customers.models import Customer
from apps.customers.selectors import active_customers, list_customers
from apps.customers.services import create_customer, set_customer_active, update_customer
from apps.users.models import User


VALID_PASSWORD = 'ClaveSegura123'


def customer_data(name='Maria Gonzalez', document='', email=''):
    return {'name': name, 'document': document, 'phone': '', 'email': email, 'address': '', 'notes': ''}


class CustomerValidationTests(TestCase):

    def test_name_is_required(self):
        customer_form = CustomerForm(data=customer_data(name=''))
        self.assertFalse(customer_form.is_valid())
        self.assertIn('name', customer_form.errors)

    def test_email_must_be_valid(self):
        customer_form = CustomerForm(data=customer_data(email='correo-invalido'))
        self.assertFalse(customer_form.is_valid())
        self.assertIn('email', customer_form.errors)

    def test_document_must_be_unique(self):
        Customer.objects.create(name='Cliente Uno', document='123')
        customer_form = CustomerForm(data=customer_data(name='Cliente Dos', document='123'))
        self.assertFalse(customer_form.is_valid())
        self.assertIn('document', customer_form.errors)


class CustomerServiceTests(TestCase):

    def test_create_customer(self):
        customer_form = CustomerForm(data=customer_data())
        self.assertTrue(customer_form.is_valid())
        new_customer = create_customer(customer_form)
        self.assertEqual(Customer.objects.count(), 1)
        self.assertEqual(new_customer.name, 'Maria Gonzalez')

    def test_update_customer(self):
        existing_customer = Customer.objects.create(name='Nombre Viejo')
        customer_form = CustomerForm(data=customer_data(name='Nombre Nuevo'), instance=existing_customer)
        self.assertTrue(customer_form.is_valid())
        updated_customer = update_customer(customer_form)
        self.assertEqual(updated_customer.name, 'Nombre Nuevo')

    def test_set_customer_active_does_not_delete(self):
        customer_to_change = Customer.objects.create(name='Cliente Activo')
        set_customer_active(customer_to_change, False)
        customer_to_change.refresh_from_db()
        self.assertFalse(customer_to_change.is_active)
        self.assertEqual(Customer.objects.count(), 1)


class CustomerSelectorTests(TestCase):

    def setUp(self):
        Customer.objects.create(name='Maria Gonzalez', document='111')
        Customer.objects.create(name='Carlos Lopez', document='999')

    def test_search_by_name(self):
        found_customers = list_customers('maria')
        self.assertEqual(found_customers.count(), 1)
        self.assertEqual(found_customers.first().name, 'Maria Gonzalez')

    def test_search_by_document(self):
        found_customers = list_customers('999')
        self.assertEqual(found_customers.count(), 1)
        self.assertEqual(found_customers.first().name, 'Carlos Lopez')

    def test_active_customers_excludes_inactive(self):
        Customer.objects.create(name='Cliente Inactivo', is_active=False)
        active_names = list(active_customers().values_list('name', flat=True))
        self.assertNotIn('Cliente Inactivo', active_names)
        self.assertEqual(active_customers().count(), 2)


class CustomerViewTests(TestCase):

    def setUp(self):
        self.member = User.objects.create_user(username='miembro', password=VALID_PASSWORD)
        self.member.user_permissions.add(*Permission.objects.filter(codename__in=['view_customer', 'add_customer', 'change_customer']))
        self.client.force_login(self.member)
        self.customer = Customer.objects.create(name='Cliente Base')

    def test_list_customers(self):
        response = self.client.get(reverse('customers:customer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cliente Base')

    def test_view_customer_form(self):
        response = self.client.get(reverse('customers:customer_edit', args=[self.customer.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cliente Base')

    def test_create_customer(self):
        self.client.post(reverse('customers:customer_create'), customer_data(name='Cliente Nuevo'))
        self.assertTrue(Customer.objects.filter(name='Cliente Nuevo').exists())

    def test_edit_customer(self):
        self.client.post(reverse('customers:customer_edit', args=[self.customer.id]), customer_data(name='Cliente Editado'))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, 'Cliente Editado')

    def test_toggle_customer_active(self):
        self.client.post(reverse('customers:customer_toggle_active', args=[self.customer.id]))
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_active)


class AccessControlTests(TestCase):

    def setUp(self):
        self.member = User.objects.create_user(username='sinpermiso', password=VALID_PASSWORD)
        self.customer_list_url = reverse('customers:customer_list')

    def test_user_without_permission_gets_forbidden(self):
        self.client.force_login(self.member)
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, 403)

    def test_user_with_permission_can_access(self):
        self.member.user_permissions.add(Permission.objects.get(codename='view_customer'))
        self.client.force_login(self.member)
        response = self.client.get(self.customer_list_url)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_access_is_logged(self):
        self.client.force_login(self.member)
        with self.assertLogs('apps.users', level='WARNING') as captured_logs:
            self.client.get(self.customer_list_url)
        self.assertIn('Acceso no autorizado', ''.join(captured_logs.output))
