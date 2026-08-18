from rest_framework import serializers
from protest_app.models import *


class MemberSerializer(serializers.ModelSerializer):
    city = serializers.CharField()
    state = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    country = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    country_name = serializers.SerializerMethodField(read_only=True)
    state_name = serializers.SerializerMethodField(read_only=True)
    city_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Members
        fields = ["id", "full_name", "email", "mobile_number", "country", "country_name", "state", "state_name", "city", "city_name", "why_join", "created_at", "is_deleted"]
        read_only_fields = ["id", "created_at", "is_deleted", "country_name", "state_name", "city_name"]
    
    def get_country_name(self, obj):
        return obj.country.country_name if obj.country else None
    
    def get_state_name(self, obj):
        return obj.state.name if obj.state else None
    
    def get_city_name(self, obj):
        return obj.city.name if obj.city else None

    def validate(self, data):
        city_value = self.initial_data.get("city")
        if not city_value:
            raise serializers.ValidationError({"city": "This field is required."})
        return data
    


    def resolve_state(self, state_value):
        """Accepts either a State ID (numeric) or a State name (string). Returns a State instance or None."""
        if state_value in (None, ""):
            return None
        if str(state_value).isdigit():
            try:
                return StatesModel.objects.get(id=int(state_value))
            except StatesModel.DoesNotExist:
                raise serializers.ValidationError({"state": f"State with id {state_value} does not exist."})
        state_obj, _ = StatesModel.objects.get_or_create(name=state_value)
        return state_obj

    def resolve_city(self, city_value, state_obj):
        """Accepts either a City ID or a City name. Returns a City instance."""
        if str(city_value).isdigit():
            try:
                return CitiesModel.objects.get(id=int(city_value))
            except CitiesModel.DoesNotExist:
                raise serializers.ValidationError({"city": f"City with id {city_value} does not exist."})
        if state_obj is None:
            raise serializers.ValidationError({"state": "State is required to create a new city."})
        city_obj, _ = CitiesModel.objects.get_or_create(name=city_value, state=state_obj)
        return city_obj

    def create(self, validated_data):
        city_value = self.initial_data.get("city")
        state_value = self.initial_data.get("state")
        country_value = self.initial_data.get("country")

        # Remove raw string values so they don't clash with resolved objects
        validated_data.pop("city", None)
        validated_data.pop("state", None)
        validated_data.pop("country", None)

        state_obj = self.resolve_state(state_value) if state_value not in (None, "") else None
        city_obj = self.resolve_city(city_value, state_obj)

        if state_obj is None:
            state_obj = city_obj.state

        country_obj = None
        if country_value not in (None, ""):
            if str(country_value).isdigit():
                try:
                    country_obj = CountryModel.objects.get(id=int(country_value))
                except CountryModel.DoesNotExist:
                    raise serializers.ValidationError({"country": f"Country with id {country_value} does not exist."})
            else:
                try:
                    country_obj = CountryModel.objects.get(country_name__iexact=country_value)
                except CountryModel.DoesNotExist:
                    raise serializers.ValidationError({"country": f"Country '{country_value}' does not exist."})
        else:
            # Get country from city if not provided
            country_obj = city_obj.country if city_obj else None

        validated_data["city"] = city_obj
        validated_data["state"] = state_obj
        validated_data["country"] = country_obj
        return Members.objects.create(**validated_data)

    def update(self, instance, validated_data):
        city_value = self.initial_data.get("city")
        state_value = self.initial_data.get("state")
        country_value = self.initial_data.get("country")

        # Remove raw string values so the final loop doesn't overwrite resolved objects
        validated_data.pop("city", None)
        validated_data.pop("state", None)
        validated_data.pop("country", None)

        state_obj = instance.state

        if state_value not in (None, ""):
            state_obj = self.resolve_state(state_value)
            instance.state = state_obj

        if city_value is not None:
            city_obj = self.resolve_city(city_value, state_obj)
            instance.city = city_obj
            if state_value in (None, "") and city_obj.state_id:
                instance.state = city_obj.state

        if country_value not in (None, ""):
            if str(country_value).isdigit():
                try:
                    country_obj = CountryModel.objects.get(id=int(country_value))
                except CountryModel.DoesNotExist:
                    raise serializers.ValidationError({"country": f"Country with id {country_value} does not exist."})
            else:
                try:
                    country_obj = CountryModel.objects.get(country_name__iexact=country_value)
                except CountryModel.DoesNotExist:
                    raise serializers.ValidationError({"country": f"Country '{country_value}' does not exist."})
            instance.country = country_obj
        elif city_value is not None:
            # Update country from city if city changed and no explicit country provided
            instance.country = instance.city.country if instance.city else None

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance