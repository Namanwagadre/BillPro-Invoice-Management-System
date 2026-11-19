from django import forms
from .models import Invoice

class InvoiceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
       self.user = kwargs.pop('user')
       super().__init__(*args, **kwargs)

    class Meta:
        model = Invoice
        fields = ['customer_name','invoice_number','amount','is_paid']

    def clean_invoice_number(self):
       invoice_number = self.cleaned_data.get('invoice_number')

       invoices = Invoice.objects.filter(
          user=self.user,
          invoice_number=invoice_number
        )

       if self.instance.pk:
         invoices = invoices.exclude(pk=self.instance.pk)

       if invoices.exists():
          raise forms.ValidationError(
             'Invoice number already exists.'
           )

       return invoice_number
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero')
        return amount