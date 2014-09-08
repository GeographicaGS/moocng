from django.contrib.auth.models import User
from django.db import models

class Teacher(models.Model):
    user = models.OneToOneField(User)
    organization = models.CharField(max_length=100,
                                    null=True,
                                    blank=True)
