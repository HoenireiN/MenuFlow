from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.shortcuts import redirect, render

from restaurants.models import Restaurant

from .forms import CustomUserCreationForm


class SmartLoginView(LoginView):

    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user

        if user.is_staff or Restaurant.objects.filter(owner=user).exists():
            return reverse('dashboard')

        return reverse('home')


def register(request):

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')

            if user.role == 'OWNER':
                return redirect('dashboard')

            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(
        request,
        'accounts/register.html',
        {
            'form': form
        }
    )
