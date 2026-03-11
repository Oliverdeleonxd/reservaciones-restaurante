web: /app/.venv/bin/python manage.py collectstatic --noinput && /app/.venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
release: /app/.venv/bin/python manage.py migrate