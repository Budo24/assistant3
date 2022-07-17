"""All helping function for Location plugin"""

from geopy.geocoders import Nominatim
import geocoder


def locator():
    """Function to determine the users location."""
    nomi_locator = Nominatim(user_agent="Location Plugin")

    current_loc = geocoder.ip('me')

    latitude = current_loc.geojson['features'][0]['properties']['lat']
    longitude = current_loc.geojson['features'][0]['properties']['lng']

    location = nomi_locator.reverse(f"{latitude}, {longitude}")
    final_location = str(location)
    return final_location
