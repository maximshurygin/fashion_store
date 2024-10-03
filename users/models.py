from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

NULLABLE = {'null': True, 'blank': True}


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='email')
    fullname = models.CharField(max_length=100, verbose_name='ФИО', **NULLABLE)
    phone = models.CharField(max_length=35, verbose_name='Номер телефон', **NULLABLE)
    address = models.CharField(max_length=300, verbose_name='Адрес', **NULLABLE)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
