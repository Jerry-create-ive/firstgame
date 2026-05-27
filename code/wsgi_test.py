import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'red_story.settings')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("WSGI application created successfully")
except Exception as e:
    print(f"Error creating WSGI application: {e}")
    import traceback
    traceback.print_exc()