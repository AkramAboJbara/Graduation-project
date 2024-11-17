# Graduation-project
Set Up Virtual Environment:
source venv/bin/activate  # On Windows: venv\Scripts\activate

Start Django Project:
django-admin startproject ecommerce_backend .

Create an App (core):
python manage.py startapp core

#to link the front in settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Frontend or other origins
]
 
