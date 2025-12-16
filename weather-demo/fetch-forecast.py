import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
VILLE = "Lyon, France"

OWM_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def geocode_city(ville_name, provider="open-meteo", api_key=None):
    """
    Géocode une ville pour obtenir sa latitude et longitude.
    
    Args:
        ville_name: Nom de la ville à géocoder
        provider: Service de géocodage à utiliser ("open-meteo" ou "openweathermap")
        api_key: Clé API (requis pour OpenWeatherMap)
    
    Returns:
        tuple: (latitude, longitude) ou (None, None) si la ville n'est pas trouvée
    """
    try:
        if provider == "open-meteo":
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_params = {"name": ville_name, "count": 1, "language": "fr", "format": "json"}
            geo_res = requests.get(geo_url, params=geo_params).json()
            
            if not geo_res.get("results"):
                print("Ville non trouvée.")
                return None, None
            
            lat = geo_res["results"][0]["latitude"]
            lon = geo_res["results"][0]["longitude"]
            
        elif provider == "openweathermap":
            if not api_key:
                print("Clé API requise pour OpenWeatherMap.")
                return None, None
            
            url_geocoding = "http://api.openweathermap.org/geo/1.0/direct"
            params_geocoding = {
                "q": ville_name,
                "appid": api_key
            }
            
            response = requests.get(url_geocoding, params=params_geocoding)
            data = response.json()
            
            if response.status_code != 200 or not data:
                print(f"Erreur de géocodage : {data.get('message', 'Ville non trouvée')}")
                return None, None
            
            lat = data[0]["lat"]
            lon = data[0]["lon"]
        
        else:
            print(f"Provider inconnu: {provider}")
            return None, None
        
        print(f"Coordinates of {ville_name}: Latitude: {lat}, Longitude: {lon}")
        return lat, lon
        
    except Exception as e:
        print(f"Erreur de géocodage : {e}")
        return None, None

def get_forecast_open_meteo(ville_name):
    """
    Récupère la météo via Open-Meteo (Pas de clé API requise).
    Nécessite une étape de géocodage au préalable.
    """
    print(f"--- Prévisions Open-Meteo pour {ville_name} ---")
    
    try:
        # Étape 1 : Géocodage pour obtenir latitude/longitude
        lat, lon = geocode_city(ville_name, provider="open-meteo")
        
        if lat is None or lon is None:
            return

        # Étape 2 : Récupération Météo
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

        for i, time_str in enumerate(hourly_times):
            dt = datetime.fromisoformat(time_str)

            if dt.hour == 12 and dt.date() > datetime.now().date():
                print(f"Date : {dt.strftime('%d/%m/%Y')} à 12h00 | Temp : {hourly_temps[i]}°C")
                count += 1
                if count == 3: break

    except Exception as e:
        print(f"Erreur Open-Meteo : {e}")

def get_forecast_openweathermap(ville_name, api_key):
    """
    Récupère la météo via OpenWeatherMap (Clé API requise).
    """
    print(f"\n--- Prévisions OpenWeatherMap pour {ville_name} ---")

    try:
        lat, lon = geocode_city(ville_name, provider="openweathermap", api_key=api_key)

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
            print(f"Erreur API : {data.get('message', 'Inconnue')}")
            return

        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "APPID": api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            print(f"Erreur API : {data.get('message', 'Inconnue')}")
            return

        count = 0
        for item in data["list"]:
            dt_txt = item["dt_txt"] # Format: "2023-10-27 12:00:00"
            dt = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S")
            
            # OpenWeatherMap retourne des données toutes les 3 heures.
            # On cherche le créneau de 12:00:00
            if dt.hour == 12 and dt.date() > datetime.now().date():
                temp = item["main"]["temp"]
                desc = item["weather"][0]["description"]
                print(f"Date : {dt.strftime('%d/%m/%Y')} à 12h00 | Temp : {temp}°C | Ciel : {desc}")
                count += 1
                if count == 3: break
                
    except Exception as e:
        print(f"Erreur OWM : {e}")

# --- Exécution ---
if __name__ == "__main__":
    get_forecast_open_meteo(VILLE)
    get_forecast_openweathermap(VILLE, OWM_API_KEY)