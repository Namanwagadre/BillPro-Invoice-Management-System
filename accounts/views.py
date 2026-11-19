from django.shortcuts import render,redirect
from .forms import CustomeUserCreationForm
from django.contrib.auth import logout

def signup(request):
    if request.method == 'POST':
        form = CustomeUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomeUserCreationForm() 

    data = {
        'form':form
    }       
    return render(request,'accounts/signup.html',data)

def logout_view(request):
    logout(request)
    return redirect("login")
