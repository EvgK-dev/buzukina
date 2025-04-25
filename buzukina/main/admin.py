from django.contrib import admin
from .models import *

class HousePhotosInline(admin.TabularInline):
    model = HousePhotos

class ReservedDatesInline(admin.TabularInline):
    model = ReservedDates

class HousesAdmin(admin.ModelAdmin):
    inlines = [HousePhotosInline, ReservedDatesInline]

admin.site.register(TitleImage)
admin.site.register(Houses, HousesAdmin)
admin.site.register(HousePhotos)
admin.site.register(AdditionalService)
admin.site.register(Review)

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file')

admin.site.register(Document, DocumentAdmin)

@admin.register(ReservedDates)
class ReservedDatesAdmin(admin.ModelAdmin):
    list_display = ('id', 'house', 'date', 'person', 'contact', 'num_people', 'total_amount', 'additional_services')
    list_filter = ('house', 'date')
    search_fields = ('house__name', 'date', 'person', 'contact', 'num_people', 'total_amount', 'additional_services')
    ordering = ('house__name', 'date')
