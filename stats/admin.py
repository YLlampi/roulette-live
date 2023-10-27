from django.contrib import admin
from .models import Statistic, DataItem, Profile, Provider, Product

# Register your models here.


admin.site.register(Statistic)
# admin.site.register(DataItem)
admin.site.register(Profile)
admin.site.register(Provider)
admin.site.register(Product)
