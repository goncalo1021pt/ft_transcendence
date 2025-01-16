from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from .models import User

def index(request):
    form = UserRegistrationForm()
    return render(request, 'index.html', {'form': form})
