from django import forms

from apps.suppliers.models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'document', 'phone', 'email', 'address', 'main_contact', 'notes']
        labels = {
            'name': 'Nombre o razón social',
            'document': 'Documento / RUC',
            'phone': 'Teléfono',
            'email': 'Correo',
            'address': 'Dirección',
            'main_contact': 'Contacto principal',
            'notes': 'Observaciones',
        }

    # El documento es opcional, pero si se carga no puede repetirse
    def clean_document(self):
        document = self.cleaned_data.get('document', '').strip()
        if document and Supplier.objects.filter(document=document).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un proveedor con este documento.')
        return document
