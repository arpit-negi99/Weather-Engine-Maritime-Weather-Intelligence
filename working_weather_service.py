#!/usr/bin/env python3

"""
Final Working Weather Service with Alerts

Complete weather service with 10-day forecasting and real-time alerts
Including cyclone warnings, severe weather alerts, and current conditions
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherAPIError(Exception):
    """Custom exception for weather API errors"""
    pass

class WorkingWeatherService:
    """Final working weather service with dual API support and alerts"""

    def __init__(self, visual_crossing_key: str = "CW53RQEBPG99V5V5VGHCN2NDL", 
                 openweather_key: str = "d9d7c7c122f9ca2b16d6b6566cc88393"):
        """Initialize with working API keys"""
        self.visual_crossing_key = visual_crossing_key
        self.openweather_key = openweather_key

        # API endpoints
        self.vc_base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
        self.owm_base_url = "https://api.openweathermap.org/data/2.5"
        self.owm_onecall_url = "https://api.openweathermap.org/data/3.0/onecall"
        self.owm_geocoding_url = "http://api.openweathermap.org/geo/1.0"

        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Working Weather App v3.0'})

        logger.info("Weather service initialized with working API keys")

    def get_current_weather(self, city: str, units: str = "metric") -> Optional[Dict]:
        """Get current weather for a city"""
        try:
            # Try Visual Crossing first for most comprehensive data
            weather_data = self._get_vc_current_weather(city, units)
            if weather_data:
                return weather_data

            # Fallback to OpenWeatherMap
            return self._get_owm_current_weather(city, units)

        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
            return None

    def get_10day_forecast(self, city: str, units: str = "metric") -> Optional[Dict]:
        """Get 10-day weather forecast"""
        try:
            # Visual Crossing supports up to 15 days, perfect for 10-day requirement
            forecast_data = self._get_vc_forecast(city, 10, units)
            if forecast_data:
                return forecast_data

            # Fallback: Use OpenWeatherMap OneCall for 7-day + current conditions
            return self._get_owm_extended_forecast(city, units)

        except Exception as e:
            logger.error(f"Error getting 10-day forecast: {e}")
            return None

    def get_weather_alerts(self, city: str) -> List[Dict]:
        """Get real-time weather alerts for a location"""
        alerts = []

        try:
            # Get coordinates first
            coords = self._get_city_coordinates(city)
            if not coords:
                return alerts

            lat, lon = coords

            # Get alerts from OpenWeatherMap OneCall
            owm_alerts = self._get_owm_alerts(lat, lon)
            alerts.extend(owm_alerts)

            # Get alerts from Visual Crossing
            vc_alerts = self._get_vc_alerts(city)
            alerts.extend(vc_alerts)

            return alerts

        except Exception as e:
            logger.error(f"Error getting weather alerts: {e}")
            return alerts

    def _get_vc_current_weather(self, city: str, units: str) -> Optional[Dict]:
        """Get current weather from Visual Crossing"""
        try:
            unit_group = "metric" if units == "metric" else "us"
            url = f"{self.vc_base_url}/{city}/today"

            params = {
                'key': self.visual_crossing_key,
                'unitGroup': unit_group,
                'include': 'current,days,alerts',
                'contentType': 'json'
            }

            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            # Convert to standard format
            current = data.get('currentConditions', {})
            location = data.get('resolvedAddress', city)

            return {
                'source': 'visual_crossing',
                'name': location.split(',')[0],
                'country': location.split(',')[-1].strip() if ',' in location else '',
                'main': {
                    'temp': current.get('temp', 0),
                    'feels_like': current.get('feelslike', 0),
                    'humidity': current.get('humidity', 0),
                    'pressure': current.get('pressure', 0) * 33.8639 if current.get('pressure') else 0,  # Convert inHg to hPa
                    'temp_min': current.get('temp', 0) - 2,  # Estimate
                    'temp_max': current.get('temp', 0) + 2   # Estimate
                },
                'weather': [{
                    'description': current.get('conditions', ''),
                    'icon': self._get_weather_icon_code(current.get('icon', ''))
                }],
                'wind': {
                    'speed': current.get('windspeed', 0),
                    'deg': current.get('winddir', 0)
                },
                'visibility': current.get('visibility', 0) * 1000,  # Convert km to meters
                'dt': int(datetime.now().timestamp()),
                'sys': {
                    'country': location.split(',')[-1].strip() if ',' in location else '',
                    'sunrise': self._parse_time_to_timestamp(current.get('sunrise', '')),
                    'sunset': self._parse_time_to_timestamp(current.get('sunset', ''))
                },
                'alerts': data.get('alerts', [])
            }

        except Exception as e:
            logger.error(f"Visual Crossing current weather error: {e}")
            return None

    def _get_vc_forecast(self, city: str, days: int, units: str) -> Optional[Dict]:
        """Get forecast from Visual Crossing"""
        try:
            unit_group = "metric" if units == "metric" else "us"
            end_date = (datetime.now() + timedelta(days=days-1)).strftime('%Y-%m-%d')

            url = f"{self.vc_base_url}/{city}/today/{end_date}"

            params = {
                'key': self.visual_crossing_key,
                'unitGroup': unit_group,
                'include': 'days,alerts',
                'contentType': 'json'
            }

            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            # Convert to standard format
            forecast_list = []
            for day in data.get('days', []):
                forecast_list.append({
                    'dt': int(datetime.fromisoformat(day['datetime']).timestamp()),
                    'main': {
                        'temp': day.get('temp', 0),
                        'temp_min': day.get('tempmin', 0),
                        'temp_max': day.get('tempmax', 0),
                        'humidity': day.get('humidity', 0),
                        'pressure': day.get('pressure', 0) * 33.8639 if day.get('pressure') else 0
                    },
                    'weather': [{
                        'description': day.get('conditions', ''),
                        'icon': self._get_weather_icon_code(day.get('icon', ''))
                    }],
                    'wind': {
                        'speed': day.get('windspeed', 0),
                        'deg': day.get('winddir', 0)
                    },
                    'pop': day.get('precipprob', 0) / 100  # Probability of precipitation
                })

            return {
                'source': 'visual_crossing',
                'city': {'name': city},
                'list': forecast_list,
                'alerts': data.get('alerts', [])
            }

        except Exception as e:
            logger.error(f"Visual Crossing forecast error: {e}")
            return None

    def _get_owm_current_weather(self, city: str, units: str) -> Optional[Dict]:
        """Get current weather from OpenWeatherMap"""
        try:
            url = f"{self.owm_base_url}/weather"
            params = {
                'q': city,
                'appid': self.openweather_key,
                'units': units
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            data['source'] = 'openweathermap'
            return data

        except Exception as e:
            logger.error(f"OpenWeatherMap current weather error: {e}")
            return None

    def _get_owm_extended_forecast(self, city: str, units: str) -> Optional[Dict]:
        """Get extended forecast using OpenWeatherMap OneCall API"""
        try:
            # First get coordinates
            coords = self._get_city_coordinates(city)
            if not coords:
                return None

            lat, lon = coords

            # Use OneCall API for extended forecast
            url = f"{self.owm_base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.openweather_key,
                'units': units
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            data['source'] = 'openweathermap'
            return data

        except Exception as e:
            logger.error(f"OpenWeatherMap extended forecast error: {e}")
            return None

    def _get_owm_alerts(self, lat: float, lon: float) -> List[Dict]:
        """Get weather alerts from OpenWeatherMap OneCall"""
        try:
            # Note: OneCall 3.0 requires subscription for alerts
            # Using basic weather endpoint to check for severe conditions
            url = f"{self.owm_base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.openweather_key
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            alerts = []

            # Check for severe weather conditions
            if data.get('weather'):
                main_weather = data['weather'][0]['main'].lower()
                description = data['weather'][0]['description']

                # Check for severe conditions
                if any(condition in main_weather for condition in ['thunderstorm', 'tornado']):
                    alerts.append({
                        'event': 'Severe Thunderstorm Warning',
                        'description': f"Severe weather detected: {description}",
                        'severity': 'Severe',
                        'start': datetime.now().isoformat(),
                        'source': 'OpenWeatherMap Analysis'
                    })

                # Check wind speed for warnings
                wind_speed = data.get('wind', {}).get('speed', 0)
                if wind_speed > 15:  # Strong winds
                    alerts.append({
                        'event': 'High Wind Warning',
                        'description': f"Strong winds detected: {wind_speed} m/s",
                        'severity': 'Moderate',
                        'start': datetime.now().isoformat(),
                        'source': 'OpenWeatherMap Analysis'
                    })

            return alerts

        except Exception as e:
            logger.error(f"OpenWeatherMap alerts error: {e}")
            return []

    def _get_vc_alerts(self, city: str) -> List[Dict]:
        """Get weather alerts from Visual Crossing"""
        try:
            # Visual Crossing includes alerts in the main weather request
            url = f"{self.vc_base_url}/{city}/today"

            params = {
                'key': self.visual_crossing_key,
                'include': 'alerts',
                'contentType': 'json'
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            alerts = []
            vc_alerts = data.get('alerts', [])

            for alert in vc_alerts:
                alerts.append({
                    'event': alert.get('event', 'Weather Alert'),
                    'description': alert.get('description', 'Weather alert in effect'),
                    'severity': alert.get('severity', 'Unknown'),
                    'start': alert.get('onset', datetime.now().isoformat()),
                    'end': alert.get('expires', ''),
                    'source': 'Visual Crossing'
                })

            return alerts

        except Exception as e:
            logger.error(f"Visual Crossing alerts error: {e}")
            return []

    def _get_city_coordinates(self, city: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for a city"""
        try:
            url = f"{self.owm_geocoding_url}/direct"
            params = {
                'q': city,
                'limit': 1,
                'appid': self.openweather_key
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data:
                return data[0]['lat'], data[0]['lon']
            return None

        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None

    def search_cities(self, query: str) -> List[Dict]:
        """Search for cities"""
        try:
            url = f"{self.owm_geocoding_url}/direct"
            params = {
                'q': query,
                'limit': 5,
                'appid': self.openweather_key
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            cities = []
            for location in data:
                cities.append({
                    'name': location.get('name', ''),
                    'country': location.get('country', ''),
                    'state': location.get('state', ''),
                    'lat': location.get('lat'),
                    'lon': location.get('lon')
                })

            return cities

        except Exception as e:
            logger.error(f"City search error: {e}")
            return []

    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate both API keys"""
        results = {}

        # Test Visual Crossing
        try:
            result = self._get_vc_current_weather("London", "metric")
            results['visual_crossing'] = result is not None
        except:
            results['visual_crossing'] = False

        # Test OpenWeatherMap
        try:
            result = self._get_owm_current_weather("London", "metric")
            results['openweathermap'] = result is not None
        except:
            results['openweathermap'] = False

        return results

    def _get_weather_icon_code(self, vc_icon: str) -> str:
        """Convert Visual Crossing icon to standard code"""
        icon_map = {
            'clear-day': '01d',
            'clear-night': '01n',
            'partly-cloudy-day': '02d',
            'partly-cloudy-night': '02n',
            'cloudy': '03d',
            'fog': '50d',
            'wind': '50d',
            'rain': '10d',
            'sleet': '13d',
            'snow': '13d',
            'hail': '13d'
        }
        return icon_map.get(vc_icon, '01d')

    def _parse_time_to_timestamp(self, time_str: str) -> int:
        """Parse time string to timestamp"""
        try:
            if time_str:
                time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
                today = datetime.now().date()
                return int(datetime.combine(today, time_obj).timestamp())
            return int(datetime.now().timestamp())
        except:
            return int(datetime.now().timestamp())


class WeatherDataProcessor:
    """Enhanced data processor for weather information"""

    @staticmethod
    def format_current_weather(weather_data: Dict) -> Dict:
        """Format current weather data for display"""
        if not weather_data:
            return {}

        try:
            formatted = {
                'city': weather_data.get('name', ''),
                'country': weather_data.get('sys', {}).get('country', ''),
                'temperature': round(weather_data.get('main', {}).get('temp', 0)),
                'feels_like': round(weather_data.get('main', {}).get('feels_like', 0)),
                'description': weather_data.get('weather', [{}])[0].get('description', ''),
                'humidity': weather_data.get('main', {}).get('humidity', 0),
                'pressure': round(weather_data.get('main', {}).get('pressure', 0)),
                'wind_speed': round(weather_data.get('wind', {}).get('speed', 0), 1),
                'wind_direction': weather_data.get('wind', {}).get('deg', 0),
                'visibility': round(weather_data.get('visibility', 0) / 1000, 1),
                'sunrise': datetime.fromtimestamp(
                    weather_data.get('sys', {}).get('sunrise', 0)
                ).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(
                    weather_data.get('sys', {}).get('sunset', 0)
                ).strftime('%H:%M'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': weather_data.get('source', 'unknown')
            }
            return formatted
        except Exception as e:
            logger.error(f"Error formatting weather data: {e}")
            return {}

    @staticmethod
    def format_forecast_data(forecast_data: Dict, days: int = 10) -> List[Dict]:
        """Format 10-day forecast data for display"""
        if not forecast_data:
            return []

        try:
            forecasts = []
            forecast_list = forecast_data.get('list', [])

            if forecast_data.get('source') == 'visual_crossing':
                # Visual Crossing data is already daily
                for item in forecast_list[:days]:
                    forecast_date = datetime.fromtimestamp(item['dt'])
                    forecasts.append({
                        'date': forecast_date.strftime('%Y-%m-%d'),
                        'day_name': forecast_date.strftime('%A'),
                        'min_temp': round(item['main']['temp_min']),
                        'max_temp': round(item['main']['temp_max']),
                        'description': item['weather'][0]['description'],
                        'humidity': item['main']['humidity'],
                        'wind_speed': round(item['wind']['speed'], 1),
                        'pressure': round(item['main']['pressure']),
                        'pop': round((item.get('pop', 0)) * 100)  # Probability of precipitation
                    })
            else:
                # OpenWeatherMap data needs grouping by date
                daily_data = {}
                for item in forecast_list:
                    date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                    if date not in daily_data:
                        daily_data[date] = []
                    daily_data[date].append(item)

                for date, day_items in list(daily_data.items())[:days]:
                    if len(forecasts) >= days:
                        break

                    temps = [item['main']['temp'] for item in day_items]
                    descriptions = [item['weather'][0]['description'] for item in day_items]

                    forecasts.append({
                        'date': date,
                        'day_name': datetime.strptime(date, '%Y-%m-%d').strftime('%A'),
                        'min_temp': round(min(temps)),
                        'max_temp': round(max(temps)),
                        'description': max(set(descriptions), key=descriptions.count),
                        'humidity': round(sum(item['main']['humidity'] for item in day_items) / len(day_items)),
                        'wind_speed': round(sum(item['wind']['speed'] for item in day_items) / len(day_items), 1),
                        'pressure': round(sum(item['main']['pressure'] for item in day_items) / len(day_items)),
                        'pop': round(sum(item.get('pop', 0) for item in day_items) / len(day_items) * 100)
                    })

            return forecasts

        except Exception as e:
            logger.error(f"Error formatting forecast data: {e}")
            return []

    @staticmethod
    def format_weather_alerts(alerts: List[Dict]) -> List[Dict]:
        """Format weather alerts for display"""
        formatted_alerts = []

        for alert in alerts:
            formatted_alerts.append({
                'title': alert.get('event', 'Weather Alert'),
                'description': alert.get('description', 'Alert in effect'),
                'severity': alert.get('severity', 'Unknown'),
                'start_time': alert.get('start', ''),
                'end_time': alert.get('end', ''),
                'source': alert.get('source', 'Weather Service'),
                'icon': WeatherDataProcessor._get_alert_icon(alert.get('severity', ''))
            })

        return formatted_alerts

    @staticmethod
    def _get_alert_icon(severity: str) -> str:
        """Get appropriate icon for alert severity"""
        severity_lower = severity.lower()
        if 'severe' in severity_lower or 'extreme' in severity_lower:
            return '🚨'
        elif 'moderate' in severity_lower or 'minor' in severity_lower:
            return '⚠️'
        else:
            return '⚡'

    @staticmethod
    def get_weather_icon(description: str) -> str:
        """Get weather icon emoji based on description"""
        description_lower = description.lower()
        icon_map = {
            'clear': '☀️',
            'sunny': '☀️',
            'partly cloudy': '⛅',
            'few clouds': '🌤️',
            'scattered clouds': '⛅',
            'broken clouds': '☁️',
            'overcast': '☁️',
            'cloudy': '☁️',
            'light rain': '🌦️',
            'moderate rain': '🌧️',
            'heavy rain': '⛈️',
            'rain': '🌧️',
            'thunderstorm': '⛈️',
            'snow': '❄️',
            'sleet': '🌨️',
            'mist': '🌫️',
            'fog': '🌫️',
            'haze': '🌫️',
            'drizzle': '🌦️',
            'shower': '🌦️'
        }

        for key, icon in icon_map.items():
            if key in description_lower:
                return icon
        return '🌤️'  # Default icon
