from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


# Create your models here.

class Provider(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name}'


class Statistic(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=True)
    is_premium = models.BooleanField(default=True)
    image = models.ImageField(upload_to='roulette', blank=True, null=True)
    is_operative = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('stats:dashboard', kwargs={'slug': self.slug})

    @property
    def data(self):
        return self.dataitem_set.all()

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class DataItem(models.Model):
    statistic = models.ForeignKey(Statistic, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField()
    owner = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.owner}: {self.value}'


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    is_pro = models.BooleanField(verbose_name='PRO', default=False)
    activation_date = models.DateTimeField(null=True, blank=True)
    deactivation_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username}'


class Product(models.Model):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'

    FREQUENCY_CHOICES = (
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (MONTHLY, 'Monthly')
    )

    name = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default=DAILY)
    description = models.CharField(max_length=100)
    price = models.IntegerField()
    frequency = models.PositiveSmallIntegerField()
    image = models.URLField(blank=True, null=True)

    def get_price(self):
        return f'{self.price/100:.2f}'

    def get_frequency_in_hours(self):
        return self.frequency * 24

    def __str__(self):
        return f'{self.name}: {self.price}'
