from django.test import TestCase
from unittest.mock import patch, MagicMock
from .views import get_weather
from rest_framework.test import APIRequestFactory
import requests


class GetWeatherTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch('api.views.get_coords')
    @patch('requests.get')
    def test_get_weather_success(self, mock_requests_get, mock_get_coords):
        # Задаем мок ответ от функции get_coords
        mock_get_coords.return_value = (37.6173, 55.7558)

        # Задаем мок ответ от API погоды
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'fact': {
                'temp': 20,
                'pressure_mm': 760,
                'wind_speed': 5
            }
        }
        mock_requests_get.return_value = mock_response

        # Создаем запрос к нашему API
        request = self.factory.get('/weather_api/get_weather?city=Москва')
        response = get_weather(request)

        self.assertEqual(response.status_code, 200)

        # Проверяем содержание ответа
        self.assertEqual(response.data['Температура'], '20 гр. по Цельсию')
        self.assertEqual(response.data['Давление'], '760 мм рт.ст.')
        self.assertEqual(response.data['Скорость ветра'], '5 м/c')

        # Проверяем, что были сделаны запросы к функции get_coords и к API погоды
        mock_get_coords.assert_called_once_with('Москва')
        mock_requests_get.assert_called_once()


    @patch('api.views.get_coords')
    def test_get_weather_coords_error(self, mock_get_coords):
        # Мокирование get_coords для возврата None, None, имитируя ошибку определения координат
        mock_get_coords.return_value = (None, None)

        # Создаем запрос к нашему API
        request = self.factory.get('/weather_api/get_weather?city=НесуществующийГород')
        response = get_weather(request)

        # Проверяем статус ответа
        self.assertEqual(response.status_code, 400)

        # Проверяем содержание ответа
        self.assertEqual(response.data['error'], 'Ошибка при определении координат города')
