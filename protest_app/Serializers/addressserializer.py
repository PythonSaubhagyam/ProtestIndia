from rest_framework import serializers
from protest_app.models import CountryModel, StatesModel, CitiesModel


class CountriesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryModel
        fields = ['id', 'country_name', 'country_code', 'currency', 'calling_code']



class StateSerializer(serializers.ModelSerializer):
    country_name = serializers.SerializerMethodField(read_only=True)

    def get_country_name(self, obj):
        return obj.country.country_name if obj.country else None

    class Meta:
        model = StatesModel
        fields = ['id', 'country', 'country_name', 'name']


class CitiesSerializer(serializers.ModelSerializer):
    state_name = serializers.SerializerMethodField(read_only=True)
    country_name = serializers.SerializerMethodField(read_only=True)

    def get_state_name(self, obj):
        return obj.state.name if obj.state else None

    def get_country_name(self, obj):
        return obj.country.country_name if obj.country else None

    class Meta:
        model = CitiesModel
        fields = ['id', 'country', 'country_name', 'state', 'state_name', 'name', 'is_active']