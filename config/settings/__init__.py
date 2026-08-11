from decouple import config

env = config('DJANGO_ENV', default='local').lower()

if env in ('production', 'prod'):
    from .production import *
else:
    from .local import *
