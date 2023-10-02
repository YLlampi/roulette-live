import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liveDashboards.settings')
django_asgi_app = get_asgi_application()

import stats.routing

application = ProtocolTypeRouter(
    {
        'hhtp': django_asgi_app,
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(stats.routing.websocket_urlpatterns))

        )
    }
)
