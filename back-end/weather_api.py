import requests

# Tu API KEY original
API_KEY = "44f6f5e71b85bbcd05354bd8507831dc"  
URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(lat, lon):
    try:
        # 1. Configurar parámetros para COORDENADAS (lat, lon)
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric"
        }

        response = requests.get(URL, params=params)
        data = response.json()

        # 2. Verificar si hubo error en la respuesta de OpenWeather
        if response.status_code != 200:
            print(f"Error OpenWeatherMap: {data.get('message', 'Desconocido')}")
            # Retornar valores promedio por defecto para que no falle la App
            return {"temperature": 25.0, "humidity": 60.0, "rainfall": 50.0}

        # 3. Extraer datos (con manejo seguro de lluvias)
        # Nota: OpenWeather a veces devuelve 'rain': {'1h': 0.5} o no devuelve nada si no llueve.
        rain_value = 0.0
        if "rain" in data:
            # Intentamos obtener lluvia de la última 1 hora, si no, de las 3 horas
            rain_value = data["rain"].get("1h", data["rain"].get("3h", 0.0))

        weather = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "rainfall": rain_value
        }

        return weather

    except Exception as e:
        print(f"Error conectando al clima: {e}")
        # Valores de emergencia si se va el internet
        return {"temperature": 25.0, "humidity": 60.0, "rainfall": 50.0}