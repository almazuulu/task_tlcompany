import os
import requests

from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from urllib.parse import unquote
from decouple import config


GEOCODE_API_KEY = config('GEOCODE_API_KEY') 
WEATHER_API_KEY = config('WEATHER_API_KEY')


def get_coords(city_name):
    cache_key = f'coords_{city_name}'
    if cache.get(cache_key):
        return cache.get(cache_key)

    geocode_url = f"https://geocode-maps.yandex.ru/1.x/?apikey={GEOCODE_API_KEY}&geocode={city_name}&lang=ru_RU&format=json"
    
    try:
        response = requests.get(geocode_url)
        response.raise_for_status()
        response_data = response.json()
        pos = response_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
        lon, lat = pos.split(' ')
        cache.set(cache_key, (float(lon), float(lat)), timeout=86400)  # Кэширование на 1 день
        return float(lon), float(lat)
    except requests.RequestException:
        return None, None


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('city', openapi.IN_QUERY, description="Название города", type=openapi.TYPE_STRING)
    ]
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_weather(request):
    city_name_encoded = request.GET.get('city', '')
    city_name = unquote(city_name_encoded)

    cache_key = f'weather_data_{city_name}'
    if cache.get(cache_key):
        return Response(cache.get(cache_key))

    coordinates = get_coords(city_name)
    if coordinates is None or None in coordinates:
        return Response({'error': 'Ошибка при определении координат города'}, status=400)

    lon, lat = coordinates
    weather_url = f"https://api.weather.yandex.ru/v2/forecast?lat={lat}&lon={lon}"
    headers = {'X-Yandex-API-Key': WEATHER_API_KEY}

    try:
        response = requests.get(weather_url, headers=headers)
        response.raise_for_status()
        weather_data = response.json()
        cache.set(cache_key, weather_data, timeout=1800)  # Кэширование на 30 минут

        current_weather = weather_data['fact']
        temperature = current_weather['temp']
        pressure = current_weather['pressure_mm']
        wind_speed = current_weather['wind_speed']

        response_data = {'Температура': f'{temperature} гр. по Цельсию',
                         'Давление': f'{pressure} мм рт.ст.',
                         'Скорость ветра': f'{wind_speed} м/c'}
        cache.set(cache_key, response_data, timeout=1800)  # Обновление кэша

        return Response(response_data)
    except requests.RequestException as e:
        return Response({'error': 'Ошибка при получении погоды'}, status=e.response.status_code if e.response else 500)
