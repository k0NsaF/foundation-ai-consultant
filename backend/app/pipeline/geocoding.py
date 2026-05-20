import json
from pathlib import Path
from typing import Optional, Tuple
import requests
from app.config import Config


class GeocodingService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.fallback_coords = self._load_fallback_coords()

    def _load_fallback_coords(self) -> dict:
        coords_path = Path(Config.PROCESSED_DATA_DIR) / "city_coords.json"
        if coords_path.exists():
            with open(coords_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_coordinates(self, city: str, street: Optional[str] = None) -> Optional[Tuple[float, float]]:
        city_lower = city.lower().strip()
        
        if city_lower in self.fallback_coords:
            coords = self.fallback_coords[city_lower]
            print(f"Координаты из fallback для {city}: {coords['lat']}, {coords['lon']}")
            return coords["lat"], coords["lon"]
        
        query = f"{city}, Россия"
        if street:
            query = f"{street}, {city}, Россия"
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": query, "format": "json", "limit": 1}
        headers = {"User-Agent": "FoundationConsultant/1.0"}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            data = response.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                print(f"Координаты из Nominatim для {city}: {lat}, {lon}")
                return lat, lon
        except Exception as e:
            print(f"Ошибка геокодинга для {city}: {e}")
        
        return None