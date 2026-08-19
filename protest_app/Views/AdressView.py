from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from protest_app.models import CountryModel, StatesModel, CitiesModel
from protest_app.Serializers.addressserializer import (
    CountriesListSerializer, StateSerializer, CitiesSerializer
)


class CountriesAPI(APIView):
    def get(self, request, id=None):
        if id:
            country = get_object_or_404(CountryModel, pk=id)
            serializer = CountriesListSerializer(country)
            return Response({'status': True, 'data': serializer.data, 'message': 'Country successfully fetched'}, status=status.HTTP_200_OK)


        countries = CountryModel.objects.all().order_by('country_name')

        search = request.query_params.get('search')
        if search:
            countries = countries.filter(country_name__icontains=search)

        serializer = CountriesListSerializer(countries, many=True)
        return Response({'status': True, 'data': serializer.data, 'message': 'Countries successfully fetched'}, status=status.HTTP_200_OK)


class StatesAPI(APIView):
    """
    GET /states/                          -> all states (paginated)
    GET /states/<id>/                     -> ONE state by its own pk
    GET /states/?country_id=<country_id>  -> states filtered by country (paginated)
    """
    def get(self, request, id=None):
        if id:
            state = get_object_or_404(StatesModel, pk=id)
            serializer = StateSerializer(state)
            return Response({'status': True, 'data': serializer.data, 'message': 'State successfully fetched'}, status=status.HTTP_200_OK)


        states = StatesModel.objects.all().order_by('name')
        country_id = request.query_params.get('country_id')
        if country_id:
            states = states.filter(country=country_id)

        search = request.query_params.get('search')
        if search:
            states = states.filter(name__icontains=search)

        serializer = StateSerializer(states, many=True)
        return Response({'status': True, 'data': serializer.data, 'message': 'States successfully fetched'}, status=status.HTTP_200_OK)


class CitiesAPI(APIView):
    """
    GET /cities/                      -> all cities (paginated)
    GET /cities/<id>/                 -> ONE city by its own pk
    GET /cities/?state_id=<state_id>  -> cities filtered by state (paginated)
    """
    def get(self, request, id=None):
        if id:
            city = get_object_or_404(CitiesModel, pk=id)
            serializer = CitiesSerializer(city)
            return Response({'status': True, 'data': serializer.data, 'message': 'City successfully fetched'}, status=status.HTTP_200_OK)


        cities = CitiesModel.objects.all().order_by('name')
        state_id = request.query_params.get('state_id')
        if state_id:
            cities = cities.filter(state=state_id)

        search = request.query_params.get('search')
        if search:
            cities = cities.filter(name__icontains=search)

        serializer = CitiesSerializer(cities, many=True)
        return Response({'status': True, 'data': serializer.data, 'message': 'Cities successfully fetched'}, status=status.HTTP_200_OK)