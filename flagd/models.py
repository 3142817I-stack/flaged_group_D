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
    country_code = models.CharField(max_length=2, blank=True, help_text="ISO 3166-1 alpha-2 code (e.g., 'ua' for Ukraine)")
    continent = models.CharField(max_length=32, blank=True)

    class Meta:
        db_table = 'flag'
        ordering = ['flag_id']

    def __str__(self):
        return self.country_name


class CountryAlias(models.Model):
    """Alternative names for countries (e.g., Czech Republic = Czechia, Central African Republic = CAR)."""
    alias_id = models.AutoField(primary_key=True)
    flag = models.ForeignKey(Flag, on_delete=models.CASCADE, related_name='aliases')
    alias_name = models.CharField(max_length=120, help_text="Alternative name for the country")

    class Meta:
        db_table = 'country_alias'
        ordering = ['flag', 'alias_name']
        unique_together = ['flag', 'alias_name']

    def __str__(self):
        return f"{self.flag.country_name} → {self.alias_name}"
