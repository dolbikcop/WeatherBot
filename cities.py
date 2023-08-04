import json
import os
import time
from typing import Any, Dict

import requests
from dotenv import load_dotenv

from database import db_add_weather_info, db_get_weather_info

load_dotenv()
api_key = os.getenv('API_KEY')

base_url = "https://api.openweathermap.org/data/2.5/weather?appid=" + api_key + '&q='

available_cities = ('Екатеринбург', 'Амстердам', "Москва", "Челябинск")

directions = {
    0: 'С',
    1: 'СВ',
    2: 'В',
    3: 'ЮВ',
    4: 'Ю',
    5: 'ЮЗ',
    6: 'З',
    7: 'СЗ'
}

cache = {}


def get_api_response(city_name: str) -> Dict[str, Any]:
    """
    Функция, которая выполняет запрос к API и кэширует результат.
    :param city_name: Название города.
    :return: Словарь из значений названия города, температуры, показателей ветра и времени жизни этого результата.
    """
    cache_info = cache.get(city_name)
    if cache_info is not None and cache_info['timeout'] > time.time():
        result = cache_info
    else:
        response = requests.get(base_url + city_name, timeout=20).json()
        print(response)
        result = {
            'name': city_name,
            'temp': from_kelvin_to_celsius(response['main']['temp']),
            'wind_speed': response['wind']['speed'],
            'wind_dir': from_deg_to_rotation(response['wind']['deg']),
            'timeout': time.time() + 600
        }
        cache[city_name] = result
        db_add_weather_info(result)
    return result


def get_info_about_city(city_name: str) -> str:
    """
    Функция, запрашивающая данные из запроса и приводящая их в вид сообщения.
    :param city_name: Название города.
    :return: Текст сообщения.
    """
    city_weather = get_api_response(city_name)
    print(*city_weather.items())
    return (f'Выбранный город: {city_weather["name"]},\n'
            f'Температура воздуха: {city_weather["temp"]} градусов Цельсия,\n'
            f'Скорость ветра: {city_weather["wind_speed"]} м/с,\n'
            f'Направление ветра: {city_weather["wind_dir"]}.\n')


def get_weather_journal(city_name: str):
    result = []
    for i in db_get_weather_info(city_name):
        result.append(
            f'Дата записи: {i.datetime}, \n'
            f'Температура воздуха: {i.temp} градусов Цельсия, \n'
            f'Скорость ветра: {i.wind_speed} м/с, \n'
            f'Направление ветра: {i.wind_dir}. \n'
        )
    return result


def from_kelvin_to_celsius(temp: float) -> float:
    """
    Перевод Кельвинов в градусы Цельсия.
    """
    return round(temp - 273.15, 2)


def from_deg_to_rotation(deg: int):
    """
    Перевод направления ветра в сторону света.
    """
    side = round(deg / 45) % 8
    return directions[side]
