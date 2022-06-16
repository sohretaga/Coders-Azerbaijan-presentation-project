from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Contact(models.Model):
    full_name = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(blank=False, null=False)
    message = models.TextField(blank=False, null=False)
    sent_date = models.DateTimeField(auto_now=True)