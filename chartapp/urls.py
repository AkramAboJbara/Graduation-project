from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='index'),
]