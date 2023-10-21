from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from .models import Statistic, DataItem
from .forms import LoginForm, RegisterForm

from faker import Faker

fake = Faker()


# Create your views here.

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                # Obtén la URL a la que se debe redirigir después del inicio de sesión
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)  # Redirige a la URL proporcionada
                else:
                    return redirect(reverse('stats:main'))  # Redirige a la URL predeterminada
    else:
        form = LoginForm()
    return render(request, 'stats/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('stats:login')


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('stats:login')
    else:
        form = RegisterForm()

    return render(request, 'stats/register.html', {'form': form})


def main(request):
    context = {}

    qs = Statistic.objects.all()

    if request.method == 'POST':
        new_stat = request.POST.get('new-statistic')
        obj, created = Statistic.objects.get_or_create(name=new_stat)
        return redirect('stats:dashboard', obj.slug)

    context['qs'] = qs

    return render(request, 'stats/main.html', context)


def dashboard(request, slug):
    context = {}
    try:
        obj = get_object_or_404(Statistic, slug=slug)
    except Exception:
        return redirect('stats:main')

    context['dashboard'] = obj
    # context['slug'] = obj.slug
    # context['data'] = obj.data
    context['user'] = request.user.username if request.user.username else fake.name()

    return render(request, 'stats/dashboard.html', context)


def become_pro(request):
    context = {}
    return render(request, 'stats/become_pro.html', context)


def chart_data(request, slug):
    obj = get_object_or_404(Statistic, slug=slug)
    qs = obj.data.values('owner').annotate(Sum('value'))
    chart_data = [x['value__sum'] for x in qs]
    chart_labels = [x['owner'] for x in qs]
    return JsonResponse({
        'chartData': chart_data,
        'chartLabels': chart_labels
    })
