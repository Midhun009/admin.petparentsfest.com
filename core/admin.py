from django.contrib import admin
from import_export.admin import ImportExportMixin
from .models import Banner, Contact, PetCategory, PetWeightClass, PetRegistration, Package, BrandRegistration, Tickets


@admin.register(Banner)
class BannerAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'order_no', 'image', 'link')
    search_fields = ('name', 'order_no')


@admin.register(Contact)
class ContactAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile', 'subject')
    search_fields = ('name', 'email', 'subject')


@admin.register(PetCategory)
class PetCategoryAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(PetWeightClass)
class PetWeightClassAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)


@admin.register(PetRegistration)
class PetRegistrationAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('owner_name', 'pet_name', 'pet_category', 'weight_class', 'created')
    search_fields = ('owner_name', 'pet_name', 'emirates_id')
    list_filter = ('pet_category', 'weight_class', 'created')
    ordering = ('-created',)


@admin.register(Package)
class PackageAdmin(ImportExportMixin, admin.ModelAdmin):
    pass


@admin.register(BrandRegistration)
class BrandRegistrationAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        'company_name', 'company_email', 'company_phone', 'location',
        'person_name', 'person_email', 'person_mobile', 'person_designation',
        'package', 'status', 'payment_status'
    )
    search_fields = (
        'company_name', 'company_email', 'company_phone',
        'person_name', 'person_email', 'person_mobile'
    )
    list_filter = ('status', 'payment_status', 'package')

@admin.register(Tickets)
class TicketsAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile', 'nationality', 'how_many_members')
    search_fields = ('name', 'email', 'mobile', 'nationality')
    list_filter = ('nationality',)
