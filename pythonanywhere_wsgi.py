# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PythonAnywhere WSGI Configuration File for TezMindz
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Open your PythonAnywhere Web tab -> click on your WSGI configuration file link:
# (/var/www/<your-username>_pythonanywhere_com_wsgi.py)
# Replace all contents with the code below:

import os
import sys

# 1. Add project directory to sys.path
# Checks both ~/TezMindz and other typical folder names
possible_paths = [
    os.path.expanduser('~/TezMindz'),
    os.path.expanduser('~/TezMindz-project'),
    os.path.expanduser('~/tezmindz'),
    os.path.dirname(os.path.abspath(__file__)),
]

for p in possible_paths:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)
        break
else:
    # Fallback default
    default_home = os.path.expanduser('~/TezMindz')
    if default_home not in sys.path:
        sys.path.insert(0, default_home)

# 2. Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 3. Load WSGI application handler
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

