from rest_framework import serializers
from .models import Banner, Contact, PetCategory, PetRegistration, BrandRegistration, PetWeightClass, Tickets, Referral, Package


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['image', 'link']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'mobile', 'subject', 'message']

class PetRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetRegistration
        fields = [
            'owner_name', 'owner_email', 'owner_phone', 'owner_address', 'emirates_id',
            'pet_category', 'pet_name', 'breed', 'age', 'gender',
            'microchip_number', 'special_needs', 'pet_photo', 'weight_class', 'weight',
            'spayed_neutered', 'attended_similar_events', 'comfortable_in_crowds','instagram',
            'socialized_with_pets_people' ,'passport_vaccine','pet_talent_show','snap_my_pet',
        ]
    def create(self, validated_data):
        
        return PetRegistration.objects.create(**validated_data)

class BrandRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandRegistration
        fields = ('company_name', 'company_email', 'company_phone', 'location', 'person_name', 'person_email', 'person_mobile', 'person_designation', 'package')

class TicketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tickets
        fields = ('name', 'email', 'mobile', 'nationality', 'how_many_members', 'have_pets', 'referral')

        

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = ('name', 'amount', 'features')

class PetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PetCategory
        fields = ['id', 'name'] 

class PetWeightClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetWeightClass
        fields = ['id', 'category', 'name'] 


class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = '__all__'