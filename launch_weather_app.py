#!/usr/bin/env python3

"""
Final Weather App Launcher

Launch the complete weather application with 10-day forecasts and alerts
"""

import sys
import os

def main():
    """Launch the final weather application"""
    try:
        # Check if the weather service file exists
        if not os.path.exists('working_weather_service.py'):
            print("❌ Error: working_weather_service.py not found!")
            print("Please ensure all files are in the same directory.")
            return

        if not os.path.exists('final_weather_app.py'):
            print("❌ Error: final_weather_app.py not found!")
            print("Please ensure all files are in the same directory.")
            return

        # Import and run the final weather app
        from final_weather_app import main as run_weather_app

        print("🌤️ Starting Final Weather Application...")
        print("✨ Features: 10-Day Forecasts • Weather Alerts • Dual API Support")
        print("🔑 API Keys: Pre-configured and ready to use")
        print()

        run_weather_app()

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Please install required dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
