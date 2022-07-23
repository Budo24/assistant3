"""All helping function for plugins."""

import json
import time
import typing
import urllib.request
from urllib.error import URLError

import geocoder
import requests
from geopy.geocoders import Nominatim
from pynput.keyboard import Controller, Key


def locator() -> str:
    """Determine the user location."""
    nomi_locator = Nominatim(user_agent='Location Plugin')

    current_loc = geocoder.ip('me')

    latitude = current_loc.geojson['features'][0]['properties']['lat']
    longitude = current_loc.geojson['features'][0]['properties']['lng']

    location = nomi_locator.reverse(f'{latitude}, {longitude}')
    return str(location)


def word_conv(
    textnum: str,
    numwords: dict[typing.Any, typing.Any] | object = None,
) -> int | str:
    """Convert words to numbers."""
    numwords = {}
    if not numwords:
        units = [
            'zero',
            'one',
            'two',
            'three',
            'four',
            'five',
            'six',
            'seven',
            'eight',
            'nine',
            'ten',
            'eleven',
            'twelve',
            'thirteen',
            'fourteen',
            'fifteen',
            'sixteen',
            'seventeen',
            'eighteen',
            'nineteen',
        ]

        tens = [
            '', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy',
            'eighty', 'ninety',
        ]

        scales = ['hundred', 'thousand', 'million', 'billion', 'trillion']

        numwords['and'] = (1, 0)
        for idx, word in enumerate(units):
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):
            numwords[word] = (10**(idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
            error_text = 'Illegal word: '
            return error_text

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


def add(left: float, right: float) -> float:
    """Add two operands.

    Args:
        left: First operand.
        right: Second operand.

    Returns:
        Sum of both operands.

    """
    return left + right


def sub(left: float, right: float) -> float:
    """Subtract Second operand from the First operand.

    Args:
        left: First operand.
        right: Second operand.

    Returns:
        Subtraction of the first operand from the second operand.

    """
    return left - right


def mul(left: float, right: float) -> float:
    """Multiplies first operand with the second operand.

    Args:
        left: First operand.
        right: Second operand.

    Returns:
        Multiplication of the first operand with the second operand.

    """
    return left * right


def div(left: float, right: float) -> float:
    """Divides first operand with the second operand.

    Args:
        left: First operand.
        right: Second operand.

    Returns:
        Division of the first operand with the second operand.

    """
    return left / right


def run(operator: str, left: float, right: float) -> float | str:
    """Execute the calculation."""
    if operator == 'add':
        return float(add(left, right))
    if operator == 'sub':
        return float(sub(left, right))
    if operator == 'multiply':
        return float(mul(left, right))
    if operator == 'division':
        return float(div(left, right))
    return 'operator doesnt exist'


def connect() -> bool:
    """Check if assistant is connected to internet or not."""
    try:
        urllib.request.urlopen('http://google.com')
        return True
    except URLError:
        return False


def increase_volume() -> None:
    """Increase the volume."""
    keyboard = Controller()
    for _i in range(8):
        keyboard.press(Key.media_volume_up)
        keyboard.release(Key.media_volume_up)
        time.sleep(0.1)


def decrease_volume() -> None:
    """Decrease the volume."""
    keyboard = Controller()
    for _i in range(8):
        keyboard.press(Key.media_volume_down)
        keyboard.release(Key.media_volume_down)
        time.sleep(0.1)


class WeatherMan():
    """Class to determine weather values of a city."""

    region: str = None
    time: str = None
    weather: str = None
    humidity: str = None
    temperature: int = None
    __measurement: str = 'c'
    __url: str = 'https://weatherdbi.herokuapp.com/data/weather/'

    def __init__(self, search: str) -> None:
        """Initialize the values."""
        self.search = search
        self.obtain_information()

    def set_measurement(self, measure_type: str) -> None:
        """Set measurements."""
        if measure_type.lower() == 'metric':
            self.__measurement = 'c'
        else:
            self.__measurement = 'f'

    def obtain_information(self) -> None:
        """Obtain informations."""
        req = requests.get(self.__url + self.search)
        self.__update_variables(req.json())

    def save_to_file(self, file_name: str) -> None:
        """Save to file."""
        data = {
            'region': self.region,
            'time': self.time,
            'weather': self.weather,
            'temperature': self.temperature,
            'humidity': self.humidity,
        }

        with open(file_name, 'w') as output:
            json.dump(data, output)

    def __update_variables(self, json: dict) -> None:
        """Update variable."""
        if 'status' in json:
            self.region = None
            self.time = None
            self.weather = None
            self.humidity = None
            self.temperature = None
        else:
            self.region = json['region']
            self.time = json['currentConditions']['dayhour']
            self.weather = json['currentConditions']['comment']
            self.temperature = json['currentConditions']['temp'][
                self.__measurement]
            self.humidity = json['currentConditions']['humidity']
