from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(pre_save, sender=Profile)
def deactivate_if_hours_passed(sender, instance, **kwargs):
    if instance.is_pro and instance.deactivation_date:
        elapsed_time = timezone.now() - instance.activation_date
        time_limit = instance.deactivation_date - instance.activation_date

        if elapsed_time.total_seconds() >= time_limit.total_seconds():
            instance.is_pro = False
            instance.deactivation_date = None

