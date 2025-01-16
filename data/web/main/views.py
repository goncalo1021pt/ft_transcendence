from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from .models import User

def index(request):
    form = UserRegistrationForm()
    return render(request, 'main/index.html', {'form': form})

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    return redirect('index')

def users_list(request):
	users = User.objects.all()
	return render(request, 'main/users.html', {'users': users})