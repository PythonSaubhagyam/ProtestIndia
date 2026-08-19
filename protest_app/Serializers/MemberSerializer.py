from rest_framework import serializers
from protest_app.models import CountryModel, StatesModel, CitiesModel, Members


class MemberSerializer(serializers.ModelSerializer):
    city = serializers.CharField()
    state = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    country = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    country_name = serializers.SerializerMethodField(read_only=True)
    state_name = serializers.SerializerMethodField(read_only=True)
    city_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Members
        fields = ["id", "full_name", "email", "mobile_number", "country", "country_name",
                  "state", "state_name", "city", "city_name", "why_join", "created_at", "is_deleted"]
        read_only_fields = ["id", "created_at", "is_deleted", "country_name", "state_name", "city_name"]

    def get_country_name(self, obj):
        return obj.country.country_name if obj.country else None

    def get_state_name(self, obj):
        return obj.state.name if obj.state else None

    def get_city_name(self, obj):
        return obj.city.name if obj.city else None

    def validate(self, data):
        if not self.initial_data.get("city"):
            raise serializers.ValidationError({"city": "This field is required."})
        return data

    # ---- resolvers ----

    def resolve_country(self, country_value):
        """Accepts a Country ID or name. Returns a CountryModel instance or None."""
        if country_value in (None, ""):
            return None
        if str(country_value).isdigit():
            try:
                return CountryModel.objects.get(id=int(country_value))
            except CountryModel.DoesNotExist:
                raise serializers.ValidationError({"country": f"Country with id {country_value} does not exist."})
        try:
            return CountryModel.objects.get(country_name__iexact=country_value)
        except CountryModel.DoesNotExist:
            raise serializers.ValidationError({"country": f"Country '{country_value}' does not exist."})

    def resolve_state(self, state_value, country_obj):
        """Accepts a State ID or name. Returns a StatesModel instance or None."""
        if state_value in (None, ""):
            return None
        if str(state_value).isdigit():
            try:
                return StatesModel.objects.get(id=int(state_value))
            except StatesModel.DoesNotExist:
                raise serializers.ValidationError({"state": f"State with id {state_value} does not exist."})

        # State sent as name — check if it already exists before demanding country
        existing_qs = StatesModel.objects.filter(name__iexact=state_value)
        if country_obj is not None:
            existing_qs = existing_qs.filter(country=country_obj)

        existing_count = existing_qs.count()
        if existing_count == 1:
            return existing_qs.first()
        if existing_count > 1:
            raise serializers.ValidationError({
                "country": f"Multiple states named '{state_value}' exist. Please also select a country."
            })

        # No existing match — must create new, so country is mandatory
        if country_obj is None:
            raise serializers.ValidationError({"country": "Country is required to create a new state."})

        state_obj, _ = StatesModel.objects.get_or_create(name=state_value, country=country_obj)
        return state_obj

    def resolve_city(self, city_value, state_obj):
        """Accepts a City ID or name. Returns a CitiesModel instance."""
        if str(city_value).isdigit():
            try:
                return CitiesModel.objects.get(id=int(city_value))
            except CitiesModel.DoesNotExist:
                raise serializers.ValidationError({"city": f"City with id {city_value} does not exist."})

        # City sent as name — check if it already exists before demanding state
        existing_qs = CitiesModel.objects.filter(name__iexact=city_value)
        if state_obj is not None:
            existing_qs = existing_qs.filter(state=state_obj)

        existing_count = existing_qs.count()
        if existing_count == 1:
            return existing_qs.first()
        if existing_count > 1:
            raise serializers.ValidationError({
                "state": f"Multiple cities named '{city_value}' exist. Please also select a state."
            })

        # No existing match — must create new, so state is mandatory
        if state_obj is None:
            raise serializers.ValidationError({"state": "State is required to create a new city."})

        city_obj, _ = CitiesModel.objects.get_or_create(
            name=city_value, state=state_obj, defaults={"country": state_obj.country}
        )
        return city_obj
    # ---- create / update ----

    def create(self, validated_data):
        city_value = self.initial_data.get("city")
        state_value = self.initial_data.get("state")
        country_value = self.initial_data.get("country")

        validated_data.pop("city", None)
        validated_data.pop("state", None)
        validated_data.pop("country", None)

        # Resolve in dependency order: country -> state -> city
        country_obj = self.resolve_country(country_value)
        state_obj = self.resolve_state(state_value, country_obj)
        city_obj = self.resolve_city(city_value, state_obj)

        # Backfill anything not explicitly provided
        if state_obj is None:
            state_obj = city_obj.state
        if country_obj is None:
            country_obj = state_obj.country if state_obj else city_obj.country

        validated_data["city"] = city_obj
        validated_data["state"] = state_obj
        validated_data["country"] = country_obj
        return Members.objects.create(**validated_data)

    def update(self, instance, validated_data):
        city_value = self.initial_data.get("city")
        state_value = self.initial_data.get("state")
        country_value = self.initial_data.get("country")

        validated_data.pop("city", None)
        validated_data.pop("state", None)
        validated_data.pop("country", None)

        country_obj = instance.country
        if country_value not in (None, ""):
            country_obj = self.resolve_country(country_value)
            instance.country = country_obj

        state_obj = instance.state
        if state_value not in (None, ""):
            state_obj = self.resolve_state(state_value, country_obj)
            instance.state = state_obj

        if city_value is not None:
            city_obj = self.resolve_city(city_value, state_obj)
            instance.city = city_obj
            if state_value in (None, "") and city_obj.state_id:
                instance.state = city_obj.state
            if country_value in (None, "") and city_obj.country_id:
                instance.country = city_obj.country

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance