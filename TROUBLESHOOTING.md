# 🔧 Troubleshooting Guide

## Common Issues & Solutions

### "ImportError: No module named 'working_weather_service'"
**Solution**: Ensure all files are in the same directory
```bash
# Check files are present
ls -la
# Should see: working_weather_service.py, final_weather_app.py, etc.
```

### "ModuleNotFoundError: No module named 'requests'"  
**Solution**: Install the requests library
```bash
pip install requests
# or
pip install -r requirements.txt
```

### "API Error" or "Could not get weather data"
**Possible Causes**:
1. No internet connection
2. API temporarily unavailable
3. City name not recognized

**Solutions**:
1. Check internet connectivity
2. Try a different city name (use major cities like "London" or "New York")
3. Wait a few minutes and try again
4. Check the status bar for specific error messages

### Application Window Too Small/Large
**Solution**: Edit config.ini
```ini
[GUI]
window_width = 1400  # Adjust as needed
window_height = 900  # Adjust as needed
```

### No Weather Alerts Showing
**Note**: This is normal for many locations
- Try cities in active weather regions: Miami, Oklahoma City, Manila
- Alerts appear only when there are active severe weather conditions
- Check different seasons (hurricane season, winter storm season)

### Forecast Shows Less Than 10 Days
**Possible Causes**:
1. Using OpenWeatherMap fallback (limited to 5 days)
2. Visual Crossing API temporary issue

**Check**: Status bar shows which API is being used
- ✅ "Visual Crossing" = 10+ days available
- ⚠️ "OpenWeatherMap" = 5 days maximum

### Python Version Issues
**Requirements**: Python 3.7 or higher
**Check version**: `python --version`
**Update if needed**: Download from python.org

### Firewall/Security Software Blocking
**Symptoms**: "Connection timeout" errors
**Solution**: 
1. Temporarily disable firewall
2. Add Python to firewall exceptions
3. Check corporate network restrictions

## Advanced Troubleshooting

### Enable Debug Mode
Add to config.ini:
```ini
[SETTINGS]
enable_logging = true
```

### Check API Key Status
The app validates API keys on startup. Check the status bar:
- ✅ "APIs Ready" = All working
- ⚠️ "API Error" = Check internet connection

### Manual API Testing
Test Visual Crossing directly:
```bash
curl "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London?key=CW53RQEBPG99V5V5VGHCN2NDL"
```

## Getting Additional Help

1. **Check README.md** for complete documentation
2. **Try sample cities** from sample_cities.txt
3. **Check API_INFO.md** for API-specific details
4. **Restart the application** - often solves temporary issues

## Performance Tips

1. **Close unused tabs** in the application
2. **Use major cities** for faster responses
3. **Avoid rapid repeated requests** (APIs have rate limits)
4. **Save weather data** locally using the Save button

Most issues are resolved by ensuring all files are present and installing the requests library!
