from django import forms

from apps.customers.models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'document', 'phone', 'email', 'address', 'notes']
        labels = {
            'name': 'Nombre o razón social',
            'document': 'Documento / RUC',
            'phone': 'Teléfono',
            'email': 'Correo',
            'address': 'Dirección',
            'notes': 'Observaciones',
        }

    # El documento es opcional, pero si se carga no puede repetirse
    def clean_document(self):
        document = self.cleaned_data.get('document', '').strip()
        if document and Customer.objects.filter(document=document).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ya existe un cliente con este documento.')
        return document
