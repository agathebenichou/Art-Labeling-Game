"""
WSGI config for artgame project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os, sys
# add the hellodjango project path into the sys.path
# sys.path.append('<PATH_TO_MY_DJANGO_PROJECT>/artgame')

# add the virtualenv site-packages path to the sys.path
# ssys.path.append('<PATH_TO_VIRTUALENV>/Lib/site-packages')



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "artgame.settings")
# os.environ['HTTPS'] = "on"

import django
django.setup()

from django.core.wsgi import get_wsgi_application

from django.contrib.auth.handlers.modwsgi import check_password

#from django.core.handlers.wsgi import WSGIHandler

#application = WSGIHandler()

application = get_wsgi_application()
