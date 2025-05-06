from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.conf import settings
from datetime import date
from django.core.exceptions import ValidationError
from django.utils import timezone



class CustomUser(AbstractUser):
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_groups",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions", 
        blank=True
    )

    birthday = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True)

    points = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class JournalEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    mood = models.CharField(max_length=100)
    entry = models.TextField()  # Text for the user to write their entry
    created_at = models.DateTimeField(auto_now_add=True)  # Time of entry creation
    
    def __str__(self):
        return f"Entry by {self.user.username} on {self.date}"
    
class ToDo(models.Model):
    STATUS_CHOICES = [
        ('to_do', 'To Do'),
        ('done', 'Done'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    title = models.CharField(max_length=100)
    description = models.TextField()
    date_due = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='to_do')

    def __str__(self):
        return self.title

class DailyQuote(models.Model):
    date = models.DateField(unique=True)
    quote = models.TextField()

    def __str__(self):
        return self.quote[:500]
    
class SleepRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(unique=True)
    sleep_time = models.TimeField()
    wake_time = models.TimeField()

    def __str__(self):
        return f"{self.date}: {self.sleep_time} - {self.wake_time}"

class WaterIntakeRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    intake_ml = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.intake_ml} ml"
    
class FavoriteSong(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    song_uri = models.URLField()

    def __str__(self):
        return f"Favorite by {self.user.username}: {self.song_uri}"