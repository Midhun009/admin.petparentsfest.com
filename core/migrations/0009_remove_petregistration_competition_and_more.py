# Generated by Django 5.1.3 on 2024-11-28 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_petregistration_competition_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='petregistration',
            name='competition',
        ),
        migrations.AddField(
            model_name='petregistration',
            name='pet_photo_competition',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='petregistration',
            name='pet_trick_competition',
            field=models.BooleanField(default=False),
        ),
    ]
