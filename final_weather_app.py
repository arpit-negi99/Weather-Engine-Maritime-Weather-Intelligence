#!/usr/bin/env python3

"""
Final Working Weather GUI Application

Complete weather application with 10-day forecasting and real-time alerts
Including cyclone warnings, severe weather alerts, and enhanced UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os
import threading
import json
from datetime import datetime
from typing import Optional, List, Dict
import webbrowser

# Import our working weather service
try:
    from working_weather_service import WorkingWeatherService, WeatherDataProcessor
except ImportError:
    print("Error: working_weather_service.py not found!")
    sys.exit(1)

class FinalWeatherApp:
    """Final working weather application with alerts and 10-day forecasts"""

    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()

        # Initialize weather service with working API keys
        try:
            self.weather_service = WorkingWeatherService()
            self.data_processor = WeatherDataProcessor()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize weather service: {e}")
            sys.exit(1)

        # Initialize variables
        self.current_city = tk.StringVar(value="New York")
        self.units_var = tk.StringVar(value="metric")

        # Data storage
        self.current_weather_data = {}
        self.forecast_data = []
        self.alerts_data = []

        # Create UI
        self.setup_styles()
        self.create_widgets()

        # Auto-validate API keys on startup
        threading.Thread(target=self.validate_api_keys, daemon=True).start()

    def setup_window(self):
        """Configure main window"""
        self.root.title("🌤️ Final Weather Forecast - 10 Day Predictions & Alerts")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Modern color scheme
        self.colors = {
            'primary': '#1976D2',       # Blue
            'secondary': '#00ACC1',     # Cyan
            'success': '#388E3C',       # Green
            'warning': '#F57C00',       # Orange
            'error': '#D32F2F',         # Red
            'surface': '#FFFFFF',       # White
            'background': '#F5F5F5',    # Light Grey
            'text': '#212121'           # Dark Grey
        }

        self.root.configure(bg=self.colors['background'])

    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()

        # Configure styles
        style.configure('Title.TLabel',
                       font=('Arial', 18, 'bold'),
                       background=self.colors['background'],
                       foreground=self.colors['text'])

        style.configure('Subtitle.TLabel',
                       font=('Arial', 12),
                       background=self.colors['background'],
                       foreground=self.colors['text'])

        style.configure('Card.TFrame',
                       background=self.colors['surface'],
                       relief='solid',
                       borderwidth=1)

        style.configure('Alert.TFrame',
                       background='#FFEBEE',
                       relief='solid',
                       borderwidth=2)

        style.configure('Success.TLabel',
                       foreground=self.colors['success'],
                       font=('Arial', 10, 'bold'))

        style.configure('Warning.TLabel',
                       foreground=self.colors['warning'],
                       font=('Arial', 10, 'bold'))

        style.configure('Error.TLabel',
                       foreground=self.colors['error'],
                       font=('Arial', 10, 'bold'))

    def create_widgets(self):
        """Create and layout GUI widgets"""
        # Main container
        main_container = ttk.Frame(self.root, padding="15")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=15, pady=15)
        main_container.columnconfigure(1, weight=1)

        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        ttk.Label(header_frame, text="🌤️ Final Weather Forecast Application",
                 style='Title.TLabel').pack(side=tk.LEFT)

        ttk.Label(header_frame, text="10-Day Predictions • Real-Time Alerts • Dual API Support",
                 style='Subtitle.TLabel').pack(side=tk.LEFT, padx=(20, 0))

        # Control panel
        control_frame = ttk.LabelFrame(main_container, text=" 🎛️ Weather Controls ", padding="15")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        control_frame.columnconfigure(1, weight=1)

        # City input
        ttk.Label(control_frame, text="City:").grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        self.city_entry = ttk.Entry(control_frame, textvariable=self.current_city, 
                                   font=('Arial', 11), width=25)
        self.city_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.city_entry.bind('<Return>', lambda e: self.get_weather_data())

        # Units selection
        units_frame = ttk.Frame(control_frame)
        units_frame.grid(row=0, column=2, padx=(10, 0))

        ttk.Label(units_frame, text="Units:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(units_frame, text="°C", variable=self.units_var, 
                       value="metric").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Radiobutton(units_frame, text="°F", variable=self.units_var, 
                       value="imperial").pack(side=tk.LEFT)

        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=(15, 0), sticky=(tk.W, tk.E))
        button_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.weather_btn = ttk.Button(button_frame, text="🌡️ Get Weather",
                                     command=self.get_weather_data)
        self.weather_btn.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))

        self.forecast_btn = ttk.Button(button_frame, text="📅 10-Day Forecast",
                                      command=self.get_10day_forecast)
        self.forecast_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))

        self.alerts_btn = ttk.Button(button_frame, text="🚨 Weather Alerts",
                                    command=self.get_weather_alerts)
        self.alerts_btn.grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E))

        self.save_btn = ttk.Button(button_frame, text="💾 Save Data",
                                  command=self.save_weather_data)
        self.save_btn.grid(row=0, column=3, padx=5, sticky=(tk.W, tk.E))

        # Create notebook for different views
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        main_container.rowconfigure(2, weight=1)

        # Current Weather Tab
        self.create_current_weather_tab()

        # 10-Day Forecast Tab
        self.create_forecast_tab()

        # Weather Alerts Tab
        self.create_alerts_tab()

        # City Search Tab
        self.create_search_tab()

        # Status bar
        status_frame = ttk.Frame(main_container)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(15, 0))

        self.status_var = tk.StringVar(value="🚀 Ready - Enter a city name to get weather data")
        self.status_bar = ttk.Label(status_frame, textvariable=self.status_var,
                                   font=('Arial', 10), padding=(10, 5))
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # API status indicator
        self.api_status = ttk.Label(status_frame, text="🔄 Checking APIs...",
                                   style='Success.TLabel', padding=(10, 5))
        self.api_status.pack(side=tk.RIGHT)

        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')

    def create_current_weather_tab(self):
        """Create current weather display tab"""
        self.current_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.current_frame, text="🌡️ Current Weather")

        # Scrollable frame
        canvas = tk.Canvas(self.current_frame, bg=self.colors['background'])
        scrollbar = ttk.Scrollbar(self.current_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        self.current_display_frame = scrollable_frame

    def create_forecast_tab(self):
        """Create 10-day forecast tab"""
        self.forecast_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.forecast_frame, text="📅 10-Day Forecast")

        # Scrollable frame
        canvas = tk.Canvas(self.forecast_frame, bg=self.colors['background'])
        scrollbar = ttk.Scrollbar(self.forecast_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        self.forecast_display_frame = scrollable_frame

    def create_alerts_tab(self):
        """Create weather alerts tab"""
        self.alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.alerts_frame, text="🚨 Weather Alerts")

        # Alert info
        info_frame = ttk.Frame(self.alerts_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(info_frame, 
                 text="🚨 Real-Time Weather Alerts & Warnings",
                 font=('Arial', 14, 'bold')).pack(pady=(0, 5))
        ttk.Label(info_frame,
                 text="Displays cyclone warnings, severe weather alerts, high winds, and other hazardous conditions").pack()

        # Scrollable alerts frame
        canvas = tk.Canvas(self.alerts_frame, bg=self.colors['background'])
        scrollbar = ttk.Scrollbar(self.alerts_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        self.alerts_display_frame = scrollable_frame

    def create_search_tab(self):
        """Create city search tab"""
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="🔍 City Search")

        # Instructions
        instructions = ttk.Label(self.search_frame,
                               text="🗺️ Search for cities worldwide and get instant weather data",
                               font=('Arial', 12), padding=(10, 10))
        instructions.pack(pady=(10, 20))

        # Search input
        search_input_frame = ttk.Frame(self.search_frame)
        search_input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(search_input_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry = ttk.Entry(search_input_frame, font=('Arial', 11))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.search_cities())

        ttk.Button(search_input_frame, text="🔍 Search",
                  command=self.search_cities).pack(side=tk.RIGHT)

        # Search results
        self.search_tree = ttk.Treeview(self.search_frame,
                                       columns=('Country', 'State', 'Coordinates'),
                                       show='tree headings', height=15)

        self.search_tree.heading('#0', text='City', anchor=tk.W)
        self.search_tree.heading('Country', text='Country', anchor=tk.W)
        self.search_tree.heading('State', text='State/Region', anchor=tk.W)
        self.search_tree.heading('Coordinates', text='Coordinates', anchor=tk.W)

        self.search_tree.column('#0', width=200)
        self.search_tree.column('Country', width=100)
        self.search_tree.column('State', width=150)
        self.search_tree.column('Coordinates', width=200)

        search_scrollbar = ttk.Scrollbar(self.search_frame, orient=tk.VERTICAL,
                                        command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=search_scrollbar.set)

        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        search_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        self.search_tree.bind('<Double-1>', self.on_search_select)

    def validate_api_keys(self):
        """Validate API keys in background"""
        try:
            self.root.after(0, lambda: self.api_status.config(text="🔄 Validating APIs..."))

            results = self.weather_service.validate_api_keys()

            valid_apis = [api for api, valid in results.items() if valid]

            if valid_apis:
                api_text = f"✅ APIs Ready: {', '.join(valid_apis)}"
                self.root.after(0, lambda: self.api_status.config(text=api_text, style='Success.TLabel'))
            else:
                self.root.after(0, lambda: self.api_status.config(text="❌ API Error", style='Error.TLabel'))

        except Exception as e:
            self.root.after(0, lambda: self.api_status.config(text=f"❌ Error: {e}", style='Error.TLabel'))

    def show_progress(self):
        """Show progress indicator"""
        self.progress.pack(side=tk.RIGHT, padx=(10, 0))
        self.progress.start(8)

    def hide_progress(self):
        """Hide progress indicator"""
        self.progress.stop()
        self.progress.pack_forget()

    def get_weather_data(self):
        """Get current weather data"""
        city = self.current_city.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name")
            return

        self.status_var.set(f"🌍 Getting weather data for {city}...")
        self.show_progress()

        threading.Thread(target=self._get_weather_thread, args=(city,), daemon=True).start()

    def _get_weather_thread(self, city: str):
        """Background thread for getting weather"""
        try:
            units = self.units_var.get()
            weather_data = self.weather_service.get_current_weather(city, units)

            if weather_data:
                formatted_data = self.data_processor.format_current_weather(weather_data)
                if formatted_data:
                    self.current_weather_data = formatted_data
                    self.root.after(0, self._display_current_weather, formatted_data, units)
                    self.root.after(0, lambda: self.status_var.set(f"✅ Weather loaded for {city}"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Data Error", "Error processing weather data"))
            else:
                self.root.after(0, lambda: messagebox.showerror("API Error", f"Could not get weather data for {city}"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Unexpected error: {str(e)}"))
        finally:
            self.root.after(0, self.hide_progress)

    def _display_current_weather(self, data: Dict, units: str):
        """Display current weather in modern format"""
        # Clear existing display
        for widget in self.current_display_frame.winfo_children():
            widget.destroy()

        unit_symbol = "°C" if units == "metric" else "°F"
        wind_unit = "m/s" if units == "metric" else "mph"
        icon = self.data_processor.get_weather_icon(data['description'])

        # Main weather card
        main_card = ttk.LabelFrame(self.current_display_frame, 
                                  text=f" 🏙️ {data['city']}, {data['country']} ", 
                                  padding="20", style='Card.TFrame')
        main_card.pack(fill=tk.X, pady=(0, 15))

        # Temperature and condition
        temp_frame = ttk.Frame(main_card)
        temp_frame.pack(fill=tk.X, pady=(0, 15))

        # Left - Temperature
        left_frame = ttk.Frame(temp_frame)
        left_frame.pack(side=tk.LEFT)

        ttk.Label(left_frame, text=f"{data['temperature']}{unit_symbol}",
                 font=('Arial', 42, 'bold'), foreground=self.colors['primary']).pack()
        ttk.Label(left_frame, text=f"Feels like {data['feels_like']}{unit_symbol}",
                 font=('Arial', 12)).pack()

        # Right - Icon and description
        right_frame = ttk.Frame(temp_frame)
        right_frame.pack(side=tk.LEFT, padx=(40, 0))

        ttk.Label(right_frame, text=icon, font=('Arial', 48)).pack()
        ttk.Label(right_frame, text=data['description'].title(),
                 font=('Arial', 16, 'bold')).pack()

        # Weather details grid
        details_frame = ttk.Frame(main_card)
        details_frame.pack(fill=tk.X)

        details = [
            ("💧", "Humidity", f"{data['humidity']}%"),
            ("📊", "Pressure", f"{data['pressure']} hPa"),
            ("💨", "Wind Speed", f"{data['wind_speed']} {wind_unit}"),
            ("🧭", "Wind Direction", f"{data['wind_direction']}°"),
            ("👁️", "Visibility", f"{data['visibility']} km"),
            ("🕐", "Updated", data['timestamp'])
        ]

        for i, (emoji, label, value) in enumerate(details):
            row = i // 3
            col = i % 3

            detail_frame = ttk.Frame(details_frame, style='Card.TFrame', padding="10")
            detail_frame.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E))
            details_frame.columnconfigure(col, weight=1)

            ttk.Label(detail_frame, text=emoji, font=('Arial', 16)).pack()
            ttk.Label(detail_frame, text=label, font=('Arial', 9, 'bold')).pack()
            ttk.Label(detail_frame, text=value, font=('Arial', 11)).pack()

        # Sun times
        sun_frame = ttk.LabelFrame(self.current_display_frame,
                                  text=" ☀️ Sun Times ", padding="15", style='Card.TFrame')
        sun_frame.pack(fill=tk.X, pady=(0, 15))

        sun_content = ttk.Frame(sun_frame)
        sun_content.pack(fill=tk.X)

        ttk.Label(sun_content, text="🌅", font=('Arial', 24)).grid(row=0, column=0, padx=10)
        ttk.Label(sun_content, text="Sunrise", font=('Arial', 12, 'bold')).grid(row=0, column=1, sticky=tk.W)
        ttk.Label(sun_content, text=data['sunrise'], font=('Arial', 14)).grid(row=0, column=2, padx=20)

        ttk.Label(sun_content, text="🌇", font=('Arial', 24)).grid(row=0, column=3, padx=10)
        ttk.Label(sun_content, text="Sunset", font=('Arial', 12, 'bold')).grid(row=0, column=4, sticky=tk.W)
        ttk.Label(sun_content, text=data['sunset'], font=('Arial', 14)).grid(row=0, column=5, padx=20)

        # Switch to current weather tab
        self.notebook.select(0)

    def get_10day_forecast(self):
        """Get 10-day weather forecast"""
        city = self.current_city.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name")
            return

        self.status_var.set(f"📅 Getting 10-day forecast for {city}...")
        self.show_progress()

        threading.Thread(target=self._get_forecast_thread, args=(city,), daemon=True).start()

    def _get_forecast_thread(self, city: str):
        """Background thread for getting forecast"""
        try:
            units = self.units_var.get()
            forecast_data = self.weather_service.get_10day_forecast(city, units)

            if forecast_data:
                formatted_forecasts = self.data_processor.format_forecast_data(forecast_data, 10)
                if formatted_forecasts:
                    self.forecast_data = formatted_forecasts
                    self.root.after(0, self._display_forecast, formatted_forecasts, units, city)
                    self.root.after(0, lambda: self.status_var.set(f"✅ 10-day forecast loaded for {city}"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Data Error", "Error processing forecast data"))
            else:
                self.root.after(0, lambda: messagebox.showerror("API Error", f"Could not get forecast data for {city}"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Unexpected error: {str(e)}"))
        finally:
            self.root.after(0, self.hide_progress)

    def _display_forecast(self, forecasts: List[Dict], units: str, city: str):
        """Display 10-day forecast"""
        # Clear existing display
        for widget in self.forecast_display_frame.winfo_children():
            widget.destroy()

        unit_symbol = "°C" if units == "metric" else "°F"

        # Title
        title_frame = ttk.Frame(self.forecast_display_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(title_frame, text=f"📅 10-Day Forecast for {city}",
                 font=('Arial', 18, 'bold')).pack()
        ttk.Label(title_frame, text=f"Showing {len(forecasts)} days of weather predictions",
                 font=('Arial', 12)).pack()

        # Forecast cards
        for i, forecast in enumerate(forecasts):
            # Forecast card
            card = ttk.LabelFrame(self.forecast_display_frame,
                                 text=f" {forecast['day_name']}, {forecast['date']} ",
                                 padding="15", style='Card.TFrame')
            card.pack(fill=tk.X, pady=(0, 10))

            content_frame = ttk.Frame(card)
            content_frame.pack(fill=tk.X)

            # Left - Icon and temperature
            left_frame = ttk.Frame(content_frame)
            left_frame.pack(side=tk.LEFT, padx=(0, 20))

            icon = self.data_processor.get_weather_icon(forecast['description'])
            ttk.Label(left_frame, text=icon, font=('Arial', 32)).pack()

            temp_range = f"{forecast['min_temp']}{unit_symbol} / {forecast['max_temp']}{unit_symbol}"
            ttk.Label(left_frame, text=temp_range,
                     font=('Arial', 14, 'bold')).pack()

            # Center - Description and details
            center_frame = ttk.Frame(content_frame)
            center_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            ttk.Label(center_frame, text=forecast['description'].title(),
                     font=('Arial', 14, 'bold')).pack(anchor=tk.W)

            details_text = f"💧 {forecast['humidity']}% • 💨 {forecast['wind_speed']} m/s • 📊 {forecast['pressure']} hPa"
            if 'pop' in forecast:
                details_text += f" • 🌧️ {forecast['pop']}%"

            ttk.Label(center_frame, text=details_text,
                     font=('Arial', 10)).pack(anchor=tk.W, pady=(5, 0))

        # Switch to forecast tab
        self.notebook.select(1)

    def get_weather_alerts(self):
        """Get weather alerts for current city"""
        city = self.current_city.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name")
            return

        self.status_var.set(f"🚨 Getting weather alerts for {city}...")
        self.show_progress()

        threading.Thread(target=self._get_alerts_thread, args=(city,), daemon=True).start()

    def _get_alerts_thread(self, city: str):
        """Background thread for getting alerts"""
        try:
            alerts = self.weather_service.get_weather_alerts(city)
            formatted_alerts = self.data_processor.format_weather_alerts(alerts)

            self.alerts_data = formatted_alerts
            self.root.after(0, self._display_alerts, formatted_alerts, city)

            if alerts:
                self.root.after(0, lambda: self.status_var.set(f"⚠️ {len(alerts)} weather alerts found for {city}"))
            else:
                self.root.after(0, lambda: self.status_var.set(f"✅ No active weather alerts for {city}"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error getting alerts: {str(e)}"))
        finally:
            self.root.after(0, self.hide_progress)

    def _display_alerts(self, alerts: List[Dict], city: str):
        """Display weather alerts"""
        # Clear existing display
        for widget in self.alerts_display_frame.winfo_children():
            widget.destroy()

        # Title
        title_frame = ttk.Frame(self.alerts_display_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(title_frame, text=f"🚨 Weather Alerts for {city}",
                 font=('Arial', 16, 'bold')).pack()

        if not alerts:
            # No alerts message
            no_alerts_frame = ttk.LabelFrame(self.alerts_display_frame,
                                           text=" ✅ All Clear ", padding="20", style='Card.TFrame')
            no_alerts_frame.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(no_alerts_frame, text="🌤️", font=('Arial', 48)).pack()
            ttk.Label(no_alerts_frame, text="No active weather alerts",
                     font=('Arial', 16, 'bold')).pack()
            ttk.Label(no_alerts_frame, text="Current weather conditions are normal",
                     font=('Arial', 12)).pack()
        else:
            # Display alerts
            for i, alert in enumerate(alerts):
                # Alert card with color coding
                alert_frame = ttk.LabelFrame(self.alerts_display_frame,
                                           text=f" {alert['icon']} {alert['title']} ",
                                           padding="15", style='Alert.TFrame')
                alert_frame.pack(fill=tk.X, pady=(0, 10))

                # Alert content
                content_frame = ttk.Frame(alert_frame)
                content_frame.pack(fill=tk.X)

                # Severity indicator
                severity_color = self.colors['error'] if 'severe' in alert['severity'].lower() else self.colors['warning']

                ttk.Label(content_frame, text=f"Severity: {alert['severity']}",
                         font=('Arial', 12, 'bold'), foreground=severity_color).pack(anchor=tk.W)

                # Description
                ttk.Label(content_frame, text=alert['description'],
                         font=('Arial', 11), wraplength=800).pack(anchor=tk.W, pady=(5, 0))

                # Time information
                if alert.get('start_time'):
                    time_text = f"📅 Active from: {alert['start_time']}"
                    if alert.get('end_time'):
                        time_text += f" to {alert['end_time']}"
                    ttk.Label(content_frame, text=time_text,
                             font=('Arial', 9), foreground='gray').pack(anchor=tk.W, pady=(5, 0))

                # Source
                ttk.Label(content_frame, text=f"Source: {alert['source']}",
                         font=('Arial', 9), foreground='gray').pack(anchor=tk.W)

        # Switch to alerts tab
        self.notebook.select(2)

    def search_cities(self):
        """Search for cities"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a search term")
            return

        self.status_var.set(f"🔍 Searching for '{query}'...")
        self.show_progress()

        threading.Thread(target=self._search_cities_thread, args=(query,), daemon=True).start()

    def _search_cities_thread(self, query: str):
        """Background thread for city search"""
        try:
            cities = self.weather_service.search_cities(query)
            self.root.after(0, self._display_search_results, cities, query)

            if cities:
                self.root.after(0, lambda: self.status_var.set(f"✅ Found {len(cities)} cities"))
            else:
                self.root.after(0, lambda: self.status_var.set(f"❌ No cities found for '{query}'"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Search error: {str(e)}"))
        finally:
            self.root.after(0, self.hide_progress)

    def _display_search_results(self, cities: List[Dict], query: str):
        """Display search results"""
        # Clear existing results
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)

        # Add search results
        for city in cities:
            state = city.get('state') or 'N/A'
            coords = f"{city['lat']:.4f}, {city['lon']:.4f}" if city.get('lat') else 'N/A'

            self.search_tree.insert('', tk.END, text=city['name'],
                                   values=(city['country'], state, coords))

        # Switch to search tab
        self.notebook.select(3)

    def on_search_select(self, event):
        """Handle city selection from search"""
        selection = self.search_tree.selection()
        if selection:
            item = self.search_tree.item(selection[0])
            city_name = item['text']

            self.current_city.set(city_name)
            self.get_weather_data()

    def save_weather_data(self):
        """Save all weather data to file"""
        city = self.current_city.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name first")
            return

        try:
            # Prepare comprehensive data
            save_data = {
                'city': city,
                'timestamp': datetime.now().isoformat(),
                'app_version': 'Final Weather App v3.0',
                'current_weather': self.current_weather_data,
                'forecast_data': self.forecast_data,
                'alerts_data': self.alerts_data,
                'units': self.units_var.get()
            }

            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"weather_data_{city.replace(' ', '_')}_{timestamp}.json"

            # Ensure data directory exists
            os.makedirs('data', exist_ok=True)
            filepath = os.path.join('data', filename)

            # Save data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Success", f"Weather data saved to:\n{filepath}")
            self.status_var.set(f"✅ Data saved: {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Save error: {str(e)}")

    def show_about(self):
        """Show about dialog"""
        about_text = """Final Weather Forecast Application v3.0

🌟 Features:
• Real-time weather conditions
• 10-day weather forecasting  
• Weather alerts and warnings
• Cyclone and severe weather detection
• Dual API support (Visual Crossing + OpenWeatherMap)
• Modern, intuitive interface

🔑 API Keys:
• Visual Crossing: CW53RQEBPG99V5V5VGHCN2NDL
• OpenWeatherMap: d9d7c7c122f9ca2b16d6b6566cc88393

Built with Python and tkinter
Final working prototype with real API integration
        """
        messagebox.showinfo("About Final Weather App", about_text)

    def run(self):
        """Start the application"""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_separator()
        help_menu.add_command(label="Weather APIs", 
                             command=lambda: webbrowser.open("https://www.visualcrossing.com/weather-api"))

        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Start with sample city
        self.root.after(1000, lambda: self.get_weather_data())

        # Start main loop
        self.root.mainloop()

    def on_closing(self):
        """Handle application closing"""
        self.root.quit()
        self.root.destroy()


def main():
    """Main entry point"""
    try:
        app = FinalWeatherApp()
        app.run()
    except Exception as e:
        print(f"Error starting Final Weather App: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
