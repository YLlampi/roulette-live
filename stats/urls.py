from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    path('', views.main, name='main'),
    path('become_pro/', login_required(views.become_pro), name='become_pro'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    path('<slug>/', login_required(views.dashboard), name='dashboard'),
    path('<slug>/chart/', login_required(views.chart_data), name='chart'),
]
