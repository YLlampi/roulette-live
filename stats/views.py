from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum

from .models import Statistic, DataItem

from faker import Faker

fake = Faker()

# Create your views here.
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
    obj = get_object_or_404(Statistic, slug=slug)
    context['name'] = obj.name
    context['slug'] = obj.slug
    context['data'] = obj.data
    context['user'] = request.user.username if request.user.username else fake.name()

    return render(request, 'stats/dashboard.html', context)


def chart_data(request, slug):
    obj = get_object_or_404(Statistic, slug=slug)
    qs = obj.data.values('owner').annotate(Sum('value'))
    chart_data = [x['value__sum'] for x in qs]
    chart_labels = [x['owner'] for x in qs]
    return JsonResponse({
        'chartData': chart_data,
        'chartLabels': chart_labels
    })