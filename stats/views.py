import paypalrestsdk
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

import uuid

from .models import Statistic, DataItem, Product, Profile
from .forms import LoginForm, RegisterForm

from paypal.standard.forms import PayPalPaymentsForm
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
    # context['user'] = request.user.username if request.user.username else fake.name()
    context['user'] = User.objects.get(id=request.user.id)

    return render(request, 'stats/dashboard.html', context)


def become_pro(request):
    products = Product.objects.all()

    context = {
        'products': products
    }
    return render(request, 'stats/become_pro.html', context)


def get_mode_paypal():
    if settings.DEBUG:
        return f"sandbox"  # Change to "live" for production
    else:
        return f"live"


paypalrestsdk.configure({
    "mode": get_mode_paypal(),
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET,
})


def create_payment(request, product_id):
    product = Product.objects.get(id=product_id)

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(
                reverse('stats:execute_payment', kwargs={'product_id': product_id})),
            "cancel_url": request.build_absolute_uri(reverse('stats:payment_failed')),
        },
        "transactions": [
            {
                "amount": {
                    "total": product.get_price(),  # Total amount in USD
                    "currency": "USD",
                },
                "description": product.description,
            }
        ],
    })

    if payment.create():
        return redirect(payment.links[1].href)  # Redirect to PayPal for payment

    else:
        return render(request, 'stats/payment_failed.html')


# def checkout(request, product_id):
#     product = Product.objects.get(id=product_id)
#
#     host = request.get_host()
#
#     paypal_checkout = {
#         'business': settings.PAYPAL_RECEIVER_EMAIL,
#         'amount': product.get_price(),
#         'item_name': product.name,
#         'invoice': uuid.uuid4(),
#         'currency_code': 'USD',
#         'notify_url': f"http://{host}{reverse('paypal-ipn')}",
#         'return_url': f"http://{host}{reverse('stats:payment_success', kwargs={'product_id': product_id})}",
#         'cancel_url': f"http://{host}{reverse('stats:payment_failed', kwargs={'product_id': product_id})}",
#     }
#
#     paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)
#
#     context = {
#         'product': product,
#         'paypal': paypal_payment
#     }
#
#     return render(request, 'stats/checkout.html', context)


# views.py

def execute_payment(request, product_id):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        product = Product.objects.get(id=product_id)
        user = User.objects.get(id=request.user.id)

        user.profile.is_pro = True
        user.profile.activation_date = timezone.now()

        product_duration_in_seconds = product.get_frequency_in_hours() * 3600
        user.profile.deactivation_date = user.profile.activation_date + timezone.timedelta(
            seconds=product_duration_in_seconds)
        user.save()
        # return render(request, 'stats/tables.html')
        return redirect('stats:main')
    else:
        return render(request, 'stats/payment_failed.html')


def payment_checkout(request):
    return render(request, 'stats/checkout.html')


# def payment_successful(request, product_id):
#     context = {}
#     return render(request, 'stats/payment_success.html', context)


def payment_failed(request):
    context = {}

    return render(request, 'stats/payment_failed.html', context)


def chart_data(request, slug):
    obj = get_object_or_404(Statistic, slug=slug)
    qs = obj.data.values('owner').annotate(Sum('value'))
    chart_data = [x['value__sum'] for x in qs]
    chart_labels = [x['owner'] for x in qs]
    return JsonResponse({
        'chartData': chart_data,
        'chartLabels': chart_labels
    })


def custom_404(request, exception):
    return render(request, '404.html', status=404)
