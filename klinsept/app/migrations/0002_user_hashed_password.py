# Generated by Django 5.1.3 on 2024-11-05 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='hashed_password',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
