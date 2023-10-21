from django.contrib import admin
from .models import Statistic, DataItem, Profile, Provider

# Register your models here.


admin.site.register(Statistic)
admin.site.register(DataItem)
admin.site.register(Profile)
admin.site.register(Provider)