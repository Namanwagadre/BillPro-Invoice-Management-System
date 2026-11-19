from django.db import models
from django.conf import settings

#invoice
class Invoice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
    customer_name = models.CharField(max_length=200)
    invoice_number = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True,blank=True)
    is_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    payment_date = models.DateField(null=True,blank=True)

    payment_method = models.CharField(max_length=50, blank=True)


    class Meta:
      constraints = [
          models.UniqueConstraint(
              fields=['user','invoice_number'],
              name='unique_invoice_per_user'
          )
      ]   
    
    def __str__(self):
        return self.invoice_number

