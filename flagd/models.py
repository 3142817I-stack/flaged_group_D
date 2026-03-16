from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    password_hash = models.CharField(max_length=128)
    is_guest = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        ordering = ['-score', 'username']

    def __str__(self):
        return f"{self.username} ({'guest' if self.is_guest else 'user'})"


class Flag(models.Model):
    flag_id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=120)
    continent = models.CharField(max_length=32, blank=True)

    class Meta:
        db_table = 'flag'
        ordering = ['flag_id']

    def __str__(self):
        return self.country_name
