# Generated by Django 5.1.3 on 2024-11-28 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_competition_petregistration_competitions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='petregistration',
            name='competitions',
        ),
        migrations.AddField(
            model_name='petregistration',
            name='competition',
            field=models.CharField(choices=[('Competion1', 'Competion1'), ('Competion2', 'Competion2')], default=0, max_length=250),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Competition',
        ),
    ]
