from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    path('', views.main, name='main'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    path('become_pro/', login_required(views.become_pro), name='become_pro'),
    # path('checkout/<int:product_id>/', login_required(views.checkout), name='checkout'),
    # path('payment_success/<int:product_id>/', login_required(views.payment_successful), name='payment_success'),
    path('payment_failed/', login_required(views.payment_failed), name='payment_failed'),

    path('checkout/', views.payment_checkout, name='checkout_payment'),
    path('create_payment/<int:product_id>/', views.create_payment, name='create_payment'),
    path('execute_payment/<int:product_id>/', views.execute_payment, name='execute_payment'),

    path('<slug>/', login_required(views.dashboard), name='dashboard'),
    path('<slug>/chart/', login_required(views.chart_data), name='chart'),

]
