from rest_framework import generics,status
from core.models import Banner, Contact, PetCategory, PetRegistration, BrandRegistration, PetWeightClass, Tickets, Package, Referral
from core.serializers import BannerSerializer, ContactSerializer, PetCategorySerializer, PetRegistrationSerializer, \
    BrandRegistrationSerializer, PetWeightClassSerializer, TicketsSerializer, PackageSerializer, ReferralSerializer

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Create your views here.
class BannerListView(generics.ListAPIView):
    queryset = Banner.objects.order_by('-order_no')
    serializer_class = BannerSerializer

class ContactCreateView(generics.CreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class PetRegistrationCreateView(generics.CreateAPIView):
    queryset = PetRegistration.objects.all()
    serializer_class = PetRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                "success": True,
                "message": "Data submitted successfully.",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    



class PetCategoryListView(generics.ListAPIView):
    queryset = PetCategory.objects.all()
    serializer_class = PetCategorySerializer

@api_view(['GET']) # type: ignore
def get_weight_classes_by_category(request, category_id):
    try:
        category = PetCategory.objects.get(id=category_id)
        weight_classes = PetWeightClass.objects.filter(category=category)
        serializer = PetWeightClassSerializer(weight_classes, many=True)
        return Response(serializer.data)  # This will now include the 'id' field
    except PetCategory.DoesNotExist:
        return Response({"error": "Category not found"}, status=404)

    

    
    
class BrandRegistrationCreateView(generics.CreateAPIView):
    queryset = BrandRegistration.objects.all()
    serializer_class = BrandRegistrationSerializer

class TicketsCreateView(generics.CreateAPIView):
    queryset = Tickets.objects.all()
    serializer_class = TicketsSerializer

class PackageCreateView(generics.ListAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer

class ReferralCreateView(generics.CreateAPIView):
    queryset = Referral.objects.all()
    serializer_class = ReferralSerializer 

class ReferralTicketsCreateView(generics.CreateAPIView):
    queryset = Tickets.objects.all()
    serializer_class = TicketsSerializer

    def create(self, request, *args, **kwargs):
        # Extract the referral slug from the URL
        referral_slug = kwargs.get('slug')

        # Check if the referral_slug exists
        try:
            referral = Referral.objects.get(slug=referral_slug)
        except Referral.DoesNotExist:
            return Response({"error": "Referral with this slug does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Create a mutable copy of request.data
        data = request.data.copy()
        data['referral'] = referral.id  # Pass the PK of the referral instead of the slug

        # Pass the updated data to the serializer
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()

        # Prepare and return the response
        return Response(
            {
                "success": True,
                "ticket_id": ticket.id,
                "message": "Ticket created successfully!",
            },
            status=status.HTTP_201_CREATED,
        )