# Deploying TezMindz on PythonAnywhere

Step-by-step guide to hosting TezMindz on [PythonAnywhere](https://www.pythonanywhere.com/).

---

## 1. Open Bash Console on PythonAnywhere
In your PythonAnywhere Dashboard, go to **Consoles** and click **Bash**.

---

## 2. Clone the Repository
Run the following commands in the Bash console:
```bash
cd ~
git clone https://github.com/vyankateshwarpund/TezMindz.git
cd TezMindz
```

---

## 3. Create & Activate Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.10 tezmindz-env
pip install -r requirements.txt
```

---

## 4. Run Migrations, Seeding & Collect Static Files
```bash
python manage.py migrate
python manage.py seed_chapter1
python manage.py collectstatic --noinput
```

*(Optional) Create an admin superuser:*
```bash
python manage.py createsuperuser
```

---

## 5. Configure the Web Tab on PythonAnywhere
1. Go to the **Web** tab in PythonAnywhere Dashboard.
2. Click **Add a new web app** -> Choose **Manual configuration** -> Select **Python 3.10**.
3. In the **Code** section:
   - **Source code**: `/home/<your-username>/TezMindz`
   - **Working directory**: `/home/<your-username>/TezMindz`
   - **WSGI configuration file**: Click the link (`/var/www/<your-username>_pythonanywhere_com_wsgi.py`) and replace its entire content with:
     ```python
     import os
     import sys

     path = '/home/<your-username>/TezMindz'
     if path not in sys.path:
         sys.path.insert(0, path)

     os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

     from django.core.wsgi import get_wsgi_application
     application = get_wsgi_application()
     ```
     *(Make sure to replace `<your-username>` with your actual PythonAnywhere username)*.
4. In the **Virtualenv** section:
   - Enter: `/home/<your-username>/.virtualenvs/tezmindz-env`
5. In the **Static files** section:
   - **URL**: `/static/`
   - **Directory**: `/home/<your-username>/TezMindz/staticfiles`

---

## 6. Reload the Web App
Click the big green **"Reload <your-username>.pythonanywhere.com"** button at the top of the Web tab.

Your TezMindz platform is now live at `https://<your-username>.pythonanywhere.com`!
