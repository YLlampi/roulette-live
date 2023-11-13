from django.utils import timezone


class AutomaticDeactivationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for automatic deactivation on each request
        self.check_deactivation(request.user)

        response = self.get_response(request)
        return response

    def check_deactivation(self, user):
        # Check and deactivate if necessary
        if user.is_authenticated and user.profile.is_pro and user.profile.deactivation_date:
            elapsed_time = timezone.now() - user.profile.activation_date
            time_limit = user.profile.deactivation_date - user.profile.activation_date

            if elapsed_time.total_seconds() >= time_limit.total_seconds():
                user.profile.is_pro = False
                user.profile.deactivation_date = None
                user.save()
