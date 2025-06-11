from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import RegistrationForm
from django.utils.crypto import get_random_string
from .models import CustomUser

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('main:home')  
        else:
            messages.error(request, "Ошибка регистрации. Проверьте введенные данные.")
    else:
        form = RegistrationForm()
    return render(request, 'auth/register.html', {'form': form})


def telegram_auth_view(request):
    telegram_id = request.GET.get("token")
    first_name = request.GET.get("first_name") or "TelegramUser"
    
    if telegram_id:
        phone_number = str(telegram_id)  
        user, created = CustomUser.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'first_name': first_name,
                'last_name': '',
                'password': get_random_string(50),
            }
        )
        if created:
            user.set_password(get_random_string(12))  
            user.save()

        login(request, user)
        return redirect("main:home") 

    return redirect("accounts:login")
