# models.py
from django.db import models
from django.contrib.auth.models import User

class Review(models.Model):
    email = models.EmailField()
    message = models.TextField()
    rating = models.PositiveIntegerField(default=1)  # 1 to 5 stars
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.email} - Rating: {self.rating}"