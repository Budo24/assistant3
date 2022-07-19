"""All helping function for Location plugin."""

import geocoder
from geopy.geocoders import Nominatim


def locator() -> None:
    """Determine the user location."""
    nomi_locator = Nominatim(user_agent='Location Plugin')

    current_loc = geocoder.ip('me')

    latitude = current_loc.geojson['features'][0]['properties']['lat']
    longitude = current_loc.geojson['features'][0]['properties']['lng']

    location = nomi_locator.reverse(f'{latitude}, {longitude}')
    print(type(location))
    debug = str(location)
    print(debug)
    print(type(debug))
    splits = debug.split()
    print(splits)
    return location

locator()