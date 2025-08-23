# 📡 API Information & Configuration

## Configured API Keys

### Visual Crossing Weather API (Primary)
**API Key**: CW53RQEBPG99V5V5VGHCN2NDL
**Status**: ✅ Active and configured
**Capabilities**:
- 15-day weather forecasts
- Real-time weather alerts
- Global weather coverage
- Severe weather notifications
- Free tier: 1,000 calls/day

**Endpoint Used**: https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline
**Documentation**: https://www.visualcrossing.com/weather-api

### OpenWeatherMap API (Fallback)
**API Key**: d9d7c7c122f9ca2b16d6b6566cc88393  
**Status**: ✅ Active and configured
**Capabilities**:
- 5-day weather forecasts
- Current weather conditions
- Global city search
- Basic weather alerts
- Free tier: 1,000 calls/day, 60 calls/minute

**Endpoints Used**:
- Current Weather: https://api.openweathermap.org/data/2.5/weather
- 5-Day Forecast: https://api.openweathermap.org/data/2.5/forecast
- Geocoding: http://api.openweathermap.org/geo/1.0/direct

## How the App Uses Both APIs

1. **Primary**: Visual Crossing for 10+ day forecasts and detailed alerts
2. **Fallback**: OpenWeatherMap if Visual Crossing fails
3. **City Search**: OpenWeatherMap geocoding for accurate location data
4. **Alerts**: Combined data from both APIs for comprehensive warnings

## API Rate Limits

**Visual Crossing**: 1,000 calls per day (resets at midnight UTC)
**OpenWeatherMap**: 1,000 calls per day, 60 per minute

The app is designed to stay well within these limits for normal usage.

## Monitoring Usage

Both APIs provide usage statistics in their dashboards:
- Visual Crossing: Account dashboard shows daily usage
- OpenWeatherMap: API Statistics tab shows current usage

## Backup Plan

If API limits are reached:
1. App will show cached data if available
2. Fallback API will be used automatically  
3. Error messages will guide user on next steps
4. Data export feature preserves previous weather data
