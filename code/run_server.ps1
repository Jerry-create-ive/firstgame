$env:DEBUG_MODE = "True"
$env:DJANGO_SECRET_KEY = "test_key_for_development_only"
python manage.py runserver 8000