from django.urls import path
from chatbot import views

urlpatterns = [
    path('', views.chatbot_page, name='chatbot_page'),
    path('get-response/', views.chatbot_response, name='chatbot_response'),
]
