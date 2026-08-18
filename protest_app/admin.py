from django.contrib import admin
from .models import CountryModel, StatesModel, CitiesModel, Members


@admin.register(CountryModel)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("country_name", "country_code", "currency", "calling_code")
    search_fields = ("country_name", "country_code")
    ordering = ("country_name",)


@admin.register(StatesModel)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name", "country__country_name")
    list_filter = ("country",)
    ordering = ("country", "name")


@admin.register(CitiesModel)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "country", "is_active")
    search_fields = ("name", "state__name", "country__country_name")
    list_filter = ("country", "state", "is_active")
    ordering = ("country", "state", "name")


@admin.register(Members)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "mobile_number", "country", "state", "city", "created_at", "is_deleted")
    search_fields = ("full_name", "email", "mobile_number", "city__name", "state__name", "country__country_name")
    list_filter = ("country", "state", "city", "created_at", "is_deleted")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
