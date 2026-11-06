from django.db import models
from django.contrib.auth.models import User


class Queue(models.Model):
    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Token(models.Model):

    STATUS_CHOICES = [
        ('Waiting', 'Waiting'),
        ('Serving', 'Serving'),
        ('Served', 'Served'),
        ('Cancelled', 'Cancelled'),
    ]

    queue = models.ForeignKey(
        Queue,
        on_delete=models.CASCADE,
        related_name='tokens'
    )
    person_name = models.CharField(max_length=100)
    token_number = models.PositiveIntegerField()
    position = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Waiting'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    called_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Token {self.token_number} - {self.person_name}"
