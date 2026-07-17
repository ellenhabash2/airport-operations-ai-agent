"""
AI tools for querying weather information.
"""

from repositories.weather_repository import WeatherRepository


def get_latest_weather() -> dict:
    """
    Return the latest weather report.
    """
    weather = WeatherRepository.get_latest()

    if weather is None:
        return {
            "error": "No weather reports found."
        }

    return weather.to_dict()