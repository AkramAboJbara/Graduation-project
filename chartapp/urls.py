from django.urls import include, path
from . import views

urlpatterns = [
    path('dashboard-info', views.dashboard_view, name='index'),
]