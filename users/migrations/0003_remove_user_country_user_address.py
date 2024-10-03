# Generated by Django 5.0 on 2024-09-12 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='country',
        ),
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Адрес'),
        ),
    ]
