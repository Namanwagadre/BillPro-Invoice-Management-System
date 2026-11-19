from django.views.generic import TemplateView, ListView, DetailView
from django.shortcuts import render,redirect
from django.db.models import Q
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Invoice
from django.db.models import Sum, Count
from reportlab.lib.colors import HexColor
from django.contrib import messages
from .forms import InvoiceForm
from django.shortcuts import get_object_or_404

@login_required(login_url='login')
def add_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST,user=request.user)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.user = request.user
            invoice.save()
            messages.success(request, 'Invoice created successfully!')
            return redirect('invoice-list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InvoiceForm(user=request.user)

    data =  {
        'form':form
    }      
    return render(request,'add_invoices.html',data) 

#create
# def create_invoice(request):
#     if request.method == 'POST':
#         customer_name = request.POST.get("customer_name")
#         invoice_number = request.POST.get("invoice_number")
#         amount = request.POST.get("amount")
#         is_paid = request.POST.get("is_paid")
#         notes = request.POST.get("notes")
#         payment_date = request.POST.get("payment_date")
#         payment_method = request.POST.get("payment_method")
        
#         Invoice.objects.create(
#             customer_name = customer_name,
#             invoice_number = invoice_number,
#             amount = amount,
#             is_paid = is_paid,
#             notes = notes,
#             payment_date = payment_date,
#             payment_method = payment_method,
#         )
#         return redirect(request, 'invoice_list.html')
#     return render(request,'add_invoices.html')

#update
@login_required(login_url='login')
def update_invoice(request,invoice_id):
    invoice = get_object_or_404(
    Invoice,
    id=invoice_id,
    user=request.user
)

    if request.method == 'POST':
        form = InvoiceForm(request.POST,instance=invoice,user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Invoice updated successfully!')
            return redirect('invoice-list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = InvoiceForm(instance=invoice,user=request.user)

    return render(request,'update_invoice.html',{'form':form})        

#delete
@login_required(login_url='login')
def delete_invoice(request,invoice_id):
    if request.method == 'POST':
        info = get_object_or_404(
           Invoice,
           id=invoice_id,
           user=request.user
        )
        info.delete()

        messages.success(request, 'Invoice deleted successfully!')

    return redirect('invoice-list')


#fetch
@login_required(login_url='login')
def show_one_invoices(request):
    invoice = Invoice.objects.get(id = 5)

    data = {
        'invoice': invoice
    }  
    return render(request, 'invoice_details.html',data)


#filter
@login_required(login_url='login')
def show_unpaid_invoices(request):
    unpaid_invoices = Invoice.objects.filter(is_paid = False)
    data = {
        'unpaid_invoices':unpaid_invoices
    }
    return render(request, 'invoice_list.html',data)

@login_required(login_url='login')
def mark_as_paid(request):
    Invoice.objects.filter(invoice_number = 'INV-001').update(is_paid=True)
    all_invoices = Invoice.objects.filter(is_paid = False)
    data = {
        'all_invoices':all_invoices
    }
    return render(request, 'invoice_list.html',data)


def home(request):
    total_invoices = Invoice.objects.filter(user=request.user).count()

    total_revenue = Invoice.objects.filter(
        user=request.user
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    paid_amount = Invoice.objects.filter(
        user=request.user,
        is_paid=True
    ).aggregate(
       total=Sum('amount')
    )['total'] or 0

    unpaid_amount = Invoice.objects.filter(
        user=request.user,
        is_paid=False
    ).aggregate(
       total=Sum('amount')
    )['total'] or 0

    data = {
    'total_invoices': total_invoices,
    'total_revenue': total_revenue,
    'paid_amount': paid_amount,
    'unpaid_amount': unpaid_amount,
    }

    return render(request, 'index.html',data)

@login_required(login_url='login')
def show_invoices(request):
    search_query = request.GET.get('search','')
    status = request.GET.get('status','')


    all_invoices = Invoice.objects.filter(user=request.user)

    if search_query:
        all_invoices = all_invoices.filter(
            Q(invoice_number__icontains=search_query)| Q(customer_name__icontains=search_query)
        )

    if status == 'paid':
        all_invoices = all_invoices.filter(is_paid=True)
    elif status == 'unpaid':
        all_invoices = all_invoices.filter(is_paid=False)    


    all_invoices = all_invoices.order_by('-date_created')    
    data = {
        'all_invoices': all_invoices,
        'search_query':search_query,
        'status':status
    }
    return render(request, "invoice_list.html",data)

@login_required(login_url='login')
def show_cust_invoices(request):
    all_invoices = Invoice.objects.filter(user=request.user)
    data = {
            'all_invoices': all_invoices
        }
    return render(request, "cust_name.html",data)


class HomePageView(LoginRequiredMixin,TemplateView):
    template_name = 'index.html'

@login_required(login_url='login')
def download_invoice(request, invoice_id):
    invoice = get_object_or_404(
    Invoice,
    id=invoice_id,
    user=request.user)  
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{invoice.invoice_number}.pdf"'  
    p = canvas.Canvas(response)
    p.setFillColor(HexColor("#245A42"))
    p.setFont("Helvetica-Bold", 20)
    p.drawString(200, 800, "BillPro Invoice")
    p.setFillColor(HexColor("#000000"))
    p.setLineWidth(1)
    p.line(50, 780, 550, 780)
    p.setFont("Helvetica", 12)

    p.drawString(50, 750, f"Invoice Number: {invoice.invoice_number}")
    p.drawString(50, 720, f"Customer Name: {invoice.customer_name}")
    p.drawString(50, 690, f"Invoice Date: {invoice.date_created}")
    p.drawString(50, 660, f"Due Date: {invoice.due_date or 'N/A'}")
    p.setFont("Helvetica-Bold", 13)
    p.drawString(50, 630, f"Amount: Rs. {invoice.amount}")
    p.setFont("Helvetica", 12)
    if invoice.is_paid:
       p.setFillColor(HexColor("#287A42"))
    else:
       p.setFillColor(HexColor("#B42318"))

    p.drawString(50, 600, f"Payment Status: {'Paid' if invoice.is_paid else 'Unpaid'}")

    p.setFillColor(HexColor("#000000"))
    p.drawString(50, 570, f"Payment Date: {invoice.payment_date or 'N/A'}")
    p.drawString(50, 540, f"Payment Method: {invoice.payment_method or 'N/A'}")
    p.drawString(50, 510, f"Notes: {invoice.notes or 'N/A'}")
    p.showPage()
    p.save()

    return response 