from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from apps.suppliers.forms import SupplierForm
from apps.suppliers.models import Supplier
from apps.suppliers.selectors import active_suppliers, list_suppliers
from apps.suppliers.services import create_supplier, set_supplier_active, update_supplier
from apps.users.models import User


VALID_PASSWORD = 'ClaveSegura123'


def supplier_data(name='Distribuidora Central', document='', email=''):
    return {'name': name, 'document': document, 'phone': '', 'email': email, 'address': '', 'main_contact': '', 'notes': ''}


class SupplierValidationTests(TestCase):

    def test_name_is_required(self):
        supplier_form = SupplierForm(data=supplier_data(name=''))
        self.assertFalse(supplier_form.is_valid())
        self.assertIn('name', supplier_form.errors)

    def test_email_must_be_valid(self):
        supplier_form = SupplierForm(data=supplier_data(email='correo-invalido'))
        self.assertFalse(supplier_form.is_valid())
        self.assertIn('email', supplier_form.errors)

    def test_document_must_be_unique(self):
        Supplier.objects.create(name='Proveedor Uno', document='123')
        supplier_form = SupplierForm(data=supplier_data(name='Proveedor Dos', document='123'))
        self.assertFalse(supplier_form.is_valid())
        self.assertIn('document', supplier_form.errors)


class SupplierServiceTests(TestCase):

    def test_create_supplier(self):
        supplier_form = SupplierForm(data=supplier_data())
        self.assertTrue(supplier_form.is_valid())
        new_supplier = create_supplier(supplier_form)
        self.assertEqual(Supplier.objects.count(), 1)
        self.assertEqual(new_supplier.name, 'Distribuidora Central')

    def test_update_supplier(self):
        existing_supplier = Supplier.objects.create(name='Nombre Viejo')
        supplier_form = SupplierForm(data=supplier_data(name='Nombre Nuevo'), instance=existing_supplier)
        self.assertTrue(supplier_form.is_valid())
        updated_supplier = update_supplier(supplier_form)
        self.assertEqual(updated_supplier.name, 'Nombre Nuevo')

    def test_set_supplier_active_does_not_delete(self):
        supplier_to_change = Supplier.objects.create(name='Proveedor Activo')
        set_supplier_active(supplier_to_change, False)
        supplier_to_change.refresh_from_db()
        self.assertFalse(supplier_to_change.is_active)
        self.assertEqual(Supplier.objects.count(), 1)


class SupplierSelectorTests(TestCase):

    def setUp(self):
        Supplier.objects.create(name='Distribuidora Central', document='111')
        Supplier.objects.create(name='Importadora Sur', document='999')

    def test_search_by_name(self):
        found_suppliers = list_suppliers('central')
        self.assertEqual(found_suppliers.count(), 1)
        self.assertEqual(found_suppliers.first().name, 'Distribuidora Central')

    def test_search_by_document(self):
        found_suppliers = list_suppliers('999')
        self.assertEqual(found_suppliers.count(), 1)
        self.assertEqual(found_suppliers.first().name, 'Importadora Sur')

    def test_active_suppliers_excludes_inactive(self):
        Supplier.objects.create(name='Proveedor Inactivo', is_active=False)
        active_names = list(active_suppliers().values_list('name', flat=True))
        self.assertNotIn('Proveedor Inactivo', active_names)
        self.assertEqual(active_suppliers().count(), 2)


class SupplierViewTests(TestCase):

    def setUp(self):
        self.member = User.objects.create_user(username='miembro', password=VALID_PASSWORD)
        self.member.user_permissions.add(*Permission.objects.filter(codename__in=['view_supplier', 'add_supplier', 'change_supplier']))
        self.client.force_login(self.member)
        self.supplier = Supplier.objects.create(name='Proveedor Base')

    def test_list_suppliers(self):
        response = self.client.get(reverse('suppliers:supplier_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Proveedor Base')

    def test_view_supplier_form(self):
        response = self.client.get(reverse('suppliers:supplier_edit', args=[self.supplier.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Proveedor Base')

    def test_create_supplier(self):
        self.client.post(reverse('suppliers:supplier_create'), supplier_data(name='Proveedor Nuevo'))
        self.assertTrue(Supplier.objects.filter(name='Proveedor Nuevo').exists())

    def test_edit_supplier(self):
        self.client.post(reverse('suppliers:supplier_edit', args=[self.supplier.id]), supplier_data(name='Proveedor Editado'))
        self.supplier.refresh_from_db()
        self.assertEqual(self.supplier.name, 'Proveedor Editado')

    def test_toggle_supplier_active(self):
        self.client.post(reverse('suppliers:supplier_toggle_active', args=[self.supplier.id]))
        self.supplier.refresh_from_db()
        self.assertFalse(self.supplier.is_active)


class AccessControlTests(TestCase):

    def setUp(self):
        self.member = User.objects.create_user(username='sinpermiso', password=VALID_PASSWORD)
        self.supplier_list_url = reverse('suppliers:supplier_list')

    def test_user_without_permission_gets_forbidden(self):
        self.client.force_login(self.member)
        response = self.client.get(self.supplier_list_url)
        self.assertEqual(response.status_code, 403)

    def test_user_with_permission_can_access(self):
        self.member.user_permissions.add(Permission.objects.get(codename='view_supplier'))
        self.client.force_login(self.member)
        response = self.client.get(self.supplier_list_url)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_access_is_logged(self):
        self.client.force_login(self.member)
        with self.assertLogs('apps.users', level='WARNING') as captured_logs:
            self.client.get(self.supplier_list_url)
        self.assertIn('Acceso no autorizado', ''.join(captured_logs.output))
