from os import rename
from django.utils.text import slugify 

from ckeditor.fields import RichTextField
from django.db import models
from django.shortcuts import render


# Create your models here.

class Referral(models.Model):

    CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No')
    ]

    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)
    nationality = models.CharField(max_length=255)
    have_pets = models.CharField(max_length=255, choices=CHOICES)
    slug = models.SlugField(unique=True, blank=True)  

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}'s referral"
    

class Banner(models.Model):
    order_no = models.CharField(max_length=25)
    name = models.CharField(max_length=255)
    image = models.FileField(upload_to='Banner')
    link = models.CharField(max_length=500)

    def __str__(self):
        return self.name

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)
    subject = models.CharField(max_length=500)
    message = models.TextField()

    def __str__(self):
        return self.name

class PetCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class PetWeightClass(models.Model):
    category = models.ForeignKey(PetCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class PetRegistration(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No')
    ]


    referrals = models.ForeignKey(Referral, on_delete=models.SET_NULL, blank=True, null=True)
    owner_name = models.CharField(max_length=250)
    owner_email = models.CharField(max_length=99)
    owner_phone = models.CharField(max_length=99)
    owner_address = models.TextField()
    emirates_id = models.CharField(max_length=250)

    pet_category = models.ForeignKey(PetCategory, on_delete=models.CASCADE)
    pet_name = models.CharField(max_length=250)
    breed = models.CharField(max_length=250)
    age = models.CharField(max_length=250)
    gender = models.CharField(max_length=250, choices=GENDER_CHOICES)
    microchip_number = models.CharField(max_length=250, blank=True, null=True)
    special_needs = models.TextField(blank=True, null=True)
    pet_photo = models.FileField(upload_to='Pet Registration' , blank=True, null=True)  
    weight_class = models.ForeignKey(PetWeightClass, on_delete=models.CASCADE,null=True)
    weight = models.CharField(max_length=250, blank=True, null=True)
    instagram = models.CharField(max_length=250, blank=True, null=True)
    spayed_neutered = models.CharField(max_length=250, choices=CHOICES,null=True)
    attended_similar_events = models.CharField(max_length=250, choices=CHOICES)
    comfortable_in_crowds = models.CharField(max_length=250, choices=CHOICES)
    socialized_with_pets_people = models.CharField(max_length=250, choices=CHOICES)
    passport_vaccine = models.FileField(upload_to='passport_vaccines/', blank=True, null=True)
    pet_talent_show = models.BooleanField(default=False)
    snap_my_pet = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.owner_name
    def get_slug(self):
        # Generate a slug using the pet's category and name
        return slugify(f"{self.pet_category.name}-{self.pet_name}-{self.id}")
    

class Tickets(models.Model):


    CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No')
    ]
    referral = models.ForeignKey(Referral, on_delete=models.CASCADE, related_name="tickets", null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)
    nationality = models.CharField(max_length=255)
    how_many_members = models.CharField(max_length=255)
    have_pets = models.CharField(max_length=255,choices=CHOICES)

    def __str__(self):
        return self.name


class Package(models.Model):
    name = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    features = RichTextField()

    def __str__(self):
        return self.name

class BrandRegistration(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Rejected', 'Rejected'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    ]
    company_name = models.CharField(max_length=255)
    company_email = models.EmailField(max_length=255)
    company_phone = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    person_name = models.CharField(max_length=255)
    person_email = models.EmailField(max_length=255)
    person_mobile = models.CharField(max_length=15)
    person_designation = models.CharField(max_length=255)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Unpaid')

    def __str__(self):
        return self.company_name
    

