#!/usr/bin/env python3
"""
Weather Forecast Fetcher.

This script fetches weather forecasts from multiple sources:
- Open-Meteo: Free weather API with 3-day forecasts
- OpenWeatherMap: Weather API with 3-day forecasts (requires API key)
- Meteo France: Current observations (D0 forecasts)

Data is saved in an organized folder structure: weather-data/YYYY/MM/DD/SOURCE-D#/
"""

import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from meteofrance_api import MeteoFranceClient
from meteofrance_api.model import Place

load_dotenv()

# Configuration
CITY = "Lyon, France"
DATA_DIR = "weather-data"

OWM_API_KEY = os.getenv("OPENWEATHER_API_KEY")
METEOFRANCE_API_KEY = os.getenv("METEOFRANCE_API_KEY")


def get_source_prefix(source):
    """
    Returns the prefix for the source.
    """
    match source:
        case "open-meteo":
            return "OM"
        case "openweathermap":
            return "OWM"
        case "meteofrance":
            return "MF"
        case _:
            raise ValueError(f"Unknown source: {source}") 

def save_forecast_data(target_date, fetch_date, forecast_horizon_days, source, city, lat, lon, temperature, description=None):
    """
    Saves forecast data in an organized folder structure.
    
    Args:
        target_date: Target forecast date (datetime.date)
        fetch_date: Fetch date (datetime.date)
        forecast_horizon_days: Forecast horizon in days (1, 2, 3)
        source: Forecast source ("open-meteo" or "openweathermap")
        city: City name
        lat: Latitude
        lon: Longitude
        temperature: Temperature in Celsius
        description: Optional description (for OWM)
    """
    try:
        # Create folder path: weather-data/YYYY/MM/DD/SOURCE-D#/
        source_prefix = get_source_prefix(source)
        folder_name = f"{source_prefix}-D{forecast_horizon_days}"
        
        folder_path = os.path.join(
            DATA_DIR,
            str(target_date.year),
            f"{target_date.month:02d}",
            f"{target_date.day:02d}",
            folder_name
        )
        
        # Create folders if they don't exist
        os.makedirs(folder_path, exist_ok=True)
        
        # Create JSON data
        forecast_data = {
            "fetch_date": fetch_date.isoformat(),
            "fetch_datetime": datetime.now().isoformat(),
            "target_date": target_date.isoformat(),
            "target_datetime": datetime.combine(target_date, datetime.min.time().replace(hour=12)).isoformat(),
            "forecast_horizon_days": forecast_horizon_days,
            "source": source,
            "city": city,
            "latitude": lat,
            "longitude": lon,
            "temperature_celsius": temperature
        }
        
        if description:
            forecast_data["description"] = description
        
        # Save JSON file
        file_path = os.path.join(folder_path, "forecast.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(forecast_data, f, indent=2, ensure_ascii=False)
        
        print(f"  → Saved: {file_path}")
        
    except Exception as e:
        print(f"Error during save: {e}")

def geocode_city(city_name, provider="open-meteo", api_key=None):
    """
    Geocode a city to get its latitude and longitude.
    
    Args:
        city_name: Name of the city to geocode
        provider: Geocoding service to use ("open-meteo" or "openweathermap")
        api_key: API key (required for OpenWeatherMap)
    
    Returns:
        tuple: (latitude, longitude) or (None, None) if city is not found
    """
    try:
        if provider == "open-meteo":
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
            geo_res = requests.get(geo_url, params=geo_params).json()
            
            if not geo_res.get("results"):
                print("City not found.")
                return None, None
            
            lat = geo_res["results"][0]["latitude"]
            lon = geo_res["results"][0]["longitude"]
            
        elif provider == "openweathermap":
            if not api_key:
                print("API key required for OpenWeatherMap.")
                return None, None
            
            url_geocoding = "http://api.openweathermap.org/geo/1.0/direct"
            params_geocoding = {
                "q": city_name,
                "appid": api_key
            }
            
            response = requests.get(url_geocoding, params=params_geocoding)
            data = response.json()
            
            if response.status_code != 200 or not data:
                print(f"Geocoding error: {data.get('message', 'City not found')}")
                return None, None
            
            lat = data[0]["lat"]
            lon = data[0]["lon"]
        
        else:
            print(f"Unknown provider: {provider}")
            return None, None
        
        print(f"Coordinates of {city_name}: Latitude: {lat}, Longitude: {lon}")
        return lat, lon
        
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None

def get_forecast_open_meteo(city_name):
    """
    Fetches weather via Open-Meteo (No API key required).
    Requires a geocoding step beforehand.
    """
    print(f"--- Open-Meteo Forecasts for {city_name} ---")
    
    try:
        # Step 1: Geocoding to get latitude/longitude
        lat, lon = geocode_city(city_name, provider="open-meteo")
        
        if lat is None or lon is None:
            return

        # Step 2: Weather Retrieval
        meteo_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m",
            "timezone": "auto",
            "forecast_days": 4
        }
        
        response = requests.get(meteo_url, params=params)
        data = response.json()
        
        hourly_times = data["hourly"]["time"]
        hourly_temps = data["hourly"]["temperature_2m"]
        
        count = 0
        fetch_date = datetime.now().date()

        for i, time_str in enumerate(hourly_times):
            dt = datetime.fromisoformat(time_str)

            if dt.hour == 12 and dt.date() > fetch_date:
                temp = hourly_temps[i]
                target_date = dt.date()
                forecast_horizon = (target_date - fetch_date).days
                
                print(f"Date: {dt.strftime('%m/%d/%Y')} at 12:00 PM | Temp: {temp}°C")
                
                # Save data
                save_forecast_data(
                    target_date=target_date,
                    fetch_date=fetch_date,
                    forecast_horizon_days=forecast_horizon,
                    source="open-meteo",
                    city=city_name,
                    lat=lat,
                    lon=lon,
                    temperature=temp
                )
                
                count += 1
                if count == 3: break

    except Exception as e:
        print(f"Open-Meteo Error: {e}")

def get_forecast_openweathermap(city_name, api_key):
    """
    Fetches weather via OpenWeatherMap (API key required).
    """
    print(f"\n--- OpenWeatherMap Forecasts for {city_name} ---")

    try:
        lat, lon = geocode_city(city_name, provider="openweathermap", api_key=api_key)

        if lat is None or lon is None:
            return

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "APPID": api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            print(f"API Error: {data.get('message', 'Unknown')}")
            return

        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            print(f"API Error: {data.get('message', 'Unknown')}")
            return

        count = 0
        fetch_date = datetime.now().date()
        
        for item in data["list"]:
            dt_txt = item["dt_txt"]
            dt = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
            
            if dt.hour == 12 and dt.date() > fetch_date:
                temp = item["main"]["temp"]
                desc = item["weather"][0]["description"]
                target_date = dt.date()
                forecast_horizon = (target_date - fetch_date).days
                
                print(f"Date: {dt.strftime('%m/%d/%Y')} at 12:00 PM | Temp: {temp}°C | Sky: {desc}")
                
                # Save data
                save_forecast_data(
                    target_date=target_date,
                    fetch_date=fetch_date,
                    forecast_horizon_days=forecast_horizon,
                    source="openweathermap",
                    city=city_name,
                    lat=lat,
                    lon=lon,
                    temperature=temp,
                    description=desc
                )
                
                count += 1
                if count == 3: break
                
    except Exception as e:
        print(f"OWM Error: {e}")

def get_observation_meteofrance(city_name):
    """
    Fetches current weather observations via Meteo France API.
    Stores the data in the current day folder.
    
    Args:
        city_name: Name of the city
    """
    print(f"\n--- Meteo France Observations for {city_name} ---")
    
    try:
        # Step 1: Geocode to get latitude/longitude
        lat, lon = geocode_city(city_name, provider="open-meteo")
        
        if lat is None or lon is None:
            return
        
        # Step 2: Initialize Meteo France client with access token
        client = MeteoFranceClient()
        
        # Step 3: Get current forecast
        forecast = client.get_forecast_for_place(place=Place({"lat": lat, "lon": lon}), language='en')
        current_forecast = forecast.current_forecast
        
        if not current_forecast:
            print("No forecast data available")
            return
        # Extract data from observation
        current_date = datetime.now().date()
        
        # Temperature
        temp = current_forecast.get('T', {}).get('value')
        if temp is None:
            print("Temperature data not available in forecast")
            return
        
        # Weather description
        weather_desc = current_forecast.get('weather', {}).get('desc')
        
        print(f"Date: {current_date.strftime('%m/%d/%Y')} | Temp: {temp}°C | Description: {weather_desc or 'N/A'}")
        
        # Save forecast data
        save_forecast_data(
            target_date=current_date,
            fetch_date=datetime.now().date(),
            forecast_horizon_days=0,
            source="meteofrance",
            city=city_name,
            lat=lat,
            lon=lon,
            temperature=temp,
            description=weather_desc
        )
        
    except Exception as e:
        print(f"Meteo France Error: {e}")

# --- Execution ---
if __name__ == "__main__":
    get_forecast_open_meteo(CITY)
    get_forecast_openweathermap(CITY, OWM_API_KEY)
    get_observation_meteofrance(CITY)