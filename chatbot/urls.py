from django.urls import path
from chatbot import views

urlpatterns = [
    path('', views.chatbot_page, name='chatbot_page'),
    path('get-response/', views.chatbot_response, name='chatbot_response'),
    path('review/', views.review_page, name='review_page'),
    path('submit-review/', views.submit_review, name='submit_review'),
]
