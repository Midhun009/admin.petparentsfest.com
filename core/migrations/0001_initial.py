# Generated by Django 5.1.3 on 2024-11-23 09:12

import ckeditor.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.CharField(max_length=25)),
                ('name', models.CharField(max_length=255)),
                ('image', models.FileField(upload_to='Banner')),
                ('link', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('mobile', models.CharField(max_length=255)),
                ('subject', models.CharField(max_length=500)),
                ('message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('amount', models.CharField(max_length=255)),
                ('features', ckeditor.fields.RichTextField()),
            ],
        ),
        migrations.CreateModel(
            name='PetCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Tickets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('mobile', models.CharField(max_length=255)),
                ('nationality', models.CharField(max_length=255)),
                ('how_many_members', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='BrandRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=255)),
                ('company_email', models.EmailField(max_length=255)),
                ('company_phone', models.CharField(max_length=15)),
                ('location', models.CharField(max_length=255)),
                ('person_name', models.CharField(max_length=255)),
                ('person_email', models.EmailField(max_length=255)),
                ('person_mobile', models.CharField(max_length=15)),
                ('person_designation', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Rejected', 'Rejected')], default='Pending', max_length=10)),
                ('payment_status', models.CharField(choices=[('Paid', 'Paid'), ('Pending', 'Pending')], default='Unpaid', max_length=10)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.package')),
            ],
        ),
        migrations.CreateModel(
            name='PetWeightClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.petcategory')),
            ],
        ),
        migrations.CreateModel(
            name='PetRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_name', models.CharField(max_length=250)),
                ('owner_email', models.CharField(max_length=99)),
                ('owner_phone', models.CharField(max_length=99)),
                ('owner_address', models.TextField()),
                ('emirates_id', models.CharField(max_length=99)),
                ('pet_name', models.CharField(max_length=250)),
                ('breed', models.CharField(max_length=250)),
                ('age', models.CharField(max_length=250)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=250)),
                ('microchip_number', models.CharField(blank=True, max_length=250, null=True)),
                ('special_needs', models.TextField(blank=True, null=True)),
                ('pet_photo', models.FileField(upload_to='Pet Registration')),
                ('weight', models.CharField(blank=True, max_length=250, null=True)),
                ('spayed_neutered', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=250, null=True)),
                ('attended_similar_events', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=250)),
                ('comfortable_in_crowds', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=250)),
                ('socialized_with_pets_people', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], max_length=250)),
                ('passport_vaccine', models.FileField(blank=True, null=True, upload_to='passport_vaccines/')),
                ('created', models.DateTimeField(auto_now=True)),
                ('pet_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.petcategory')),
                ('weight_class', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.petweightclass')),
            ],
        ),
    ]
