# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PythonAnywhere WSGI Configuration File for TezMindz
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Paste this configuration into your PythonAnywhere WSGI file:
# (/var/www/<your-username>_pythonanywhere_com_wsgi.py)

import os
import sys

# Path to project directory
project_home = os.path.expanduser('~/TezMindz')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set the Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Load WSGI application handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
