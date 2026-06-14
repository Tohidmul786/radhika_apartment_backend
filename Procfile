web: gunicorn core.wsgi:application --timeout 120 --workers 2
release: python manage.py migrate --noinput
