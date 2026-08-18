from django.urls import path
from .Views.MemberView import MemberAPI, MemberRestoreAPI
from .Views.AdressView import CountriesAPI, StatesAPI, CitiesAPI

urlpatterns = [
    # Countries APIs
    path("countries/", CountriesAPI.as_view(), name="countries-list"),
    path("countries/<int:id>/", CountriesAPI.as_view(), name="countries-detail"),
    
    # States APIs
    path("states/", StatesAPI.as_view(), name="states-list"),
    path("states/<int:id>/", StatesAPI.as_view(), name="states-detail"),
    
    # Cities APIs
    path("cities/", CitiesAPI.as_view(), name="cities-list"),
    path("cities/<int:id>/", CitiesAPI.as_view(), name="cities-detail"),
    
    # Members APIs
    path("members/", MemberAPI.as_view(), name="member-api"),
    path("members/<int:id>/", MemberAPI.as_view(), name="member-detail"),
    path("members/<int:id>/restore/", MemberRestoreAPI.as_view(), name="member-restore"),
]
