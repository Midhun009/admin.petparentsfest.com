from django.conf.urls.static import static
from django.urls import path

from petparentsexpo import settings
from .views import BannerListView, ContactCreateView, PetCategoryListView, PetRegistrationCreateView, \
    BrandRegistrationCreateView, TicketsCreateView, PackageCreateView, ReferralCreateView, ReferralTicketsCreateView
from core import views


urlpatterns = [
    path('api/banners/', BannerListView.as_view(), name='banners'),
    path('api/contact/', ContactCreateView.as_view(), name='contact'),
    path('api/pet-registration/', PetRegistrationCreateView.as_view(), name='pet-registration'),
    path('api/brand-registrations/', BrandRegistrationCreateView.as_view(), name='brand-registrations'),
    path('api/tickets/', TicketsCreateView.as_view(), name='tickets'),
    path('api/packages/', PackageCreateView.as_view(), name='packages'),
    path('api/category/', PetCategoryListView.as_view(), name='category'),
    path('api/weight_classes/<int:category_id>/', views.get_weight_classes_by_category, name='get_weight_classes_by_category'),
    path('api/referrals/', ReferralCreateView.as_view(), name='referral-create'),
    path('api/tickets/<slug:slug>/', ReferralTicketsCreateView.as_view(), name='referral-tickets-api'), 

]
if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
