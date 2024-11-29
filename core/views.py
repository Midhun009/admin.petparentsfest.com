from rest_framework import generics,status
from core.models import Banner, Contact, PetCategory, PetRegistration, BrandRegistration, PetWeightClass, Tickets, Package
from core.serializers import BannerSerializer, ContactSerializer, PetCategorySerializer, PetRegistrationSerializer, \
    BrandRegistrationSerializer, PetWeightClassSerializer, TicketsSerializer, PackageSerializer

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

@api_view(['GET'])
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