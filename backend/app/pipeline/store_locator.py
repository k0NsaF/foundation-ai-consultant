import requests
import math
import urllib.parse
from typing import List, Dict
import concurrent.futures


class StoreLocator:
    def __init__(self):
        # Альтернативные серверы Overpass API
        self.overpass_urls = [
            "https://overpass-api.de/api/interpreter",
            "https://overpass.openstreetmap.fr/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.osm.rambler.ru/cgi/interpreter"
        ]
        self.timeout = 10  # таймаут на каждый сервер (секунды)

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        return R * 2 * math.asin(math.sqrt(a))

    def _encode_url(self, text: str) -> str:
        return urllib.parse.quote(text, safe='')

    def _try_request(self, url: str, query: str, headers: dict) -> tuple:
        """Пытается выполнить запрос к одному серверу"""
        try:
            response = requests.post(
                url, 
                data=query, 
                headers=headers,
                timeout=self.timeout
            )
            if response.status_code == 200:
                return url, response.json()
            else:
                return url, None
        except Exception as e:
            print(f"StoreLocator: сервер {url} не ответил: {type(e).__name__}")
            return url, None

    def find_nearby_stores(self, lat: float, lon: float, radius_km: int = 10) -> List[Dict]:
        if not lat or not lon:
            print("StoreLocator: нет координат")
            return []

        radius_m = radius_km * 1000
        
        query = f"""
        [out:json][timeout:25];
        (
          node["shop"="doityourself"](around:{radius_m},{lat},{lon});
          node["shop"="hardware"](around:{radius_m},{lat},{lon});
          node["shop"="trade"](around:{radius_m},{lat},{lon});
          node["shop"="building_materials"](around:{radius_m},{lat},{lon});
        );
        out body;
        """
        
        headers = {
            "User-Agent": "FoundationConsultant/1.0",
            "Accept": "application/json"
        }

        print(f"StoreLocator: поиск магазинов вокруг {lat}, {lon} в радиусе {radius_km} км")

        # Параллельные запросы ко всем серверам (берём первый успешный)
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.overpass_urls)) as executor:
            futures = [
                executor.submit(self._try_request, url, query, headers)
                for url in self.overpass_urls
            ]
            
            for future in concurrent.futures.as_completed(futures):
                url, data = future.result()
                if data:
                    print(f"StoreLocator: успешный ответ от {url}")
                    stores = self._parse_stores(data, lat, lon)
                    if stores:
                        print(f"StoreLocator: найдено {len(stores)} уникальных магазинов")
                        return stores
                    else:
                        return []

        print("StoreLocator: все серверы Overpass API не ответили")
        return []

    def _parse_stores(self, data: dict, lat: float, lon: float) -> List[Dict]:
        unique_stores = {}
        
        for element in data.get("elements", []):
            store_lat = element.get("lat")
            store_lon = element.get("lon")
            
            if store_lat and store_lon:
                distance = self._calculate_distance(lat, lon, store_lat, store_lon)
                tags = element.get("tags", {})
                name = tags.get("name", "")
                website = tags.get("website", "")
                
                skip_words = ["авто", "запчасть", "шина", "мебель", "продукты", "супермаркет"]
                if any(word in name.lower() for word in skip_words):
                    continue
                
                key = name.lower() if name else f"{store_lat:.3f}_{store_lon:.3f}"
                
                if key in unique_stores:
                    if unique_stores[key]["distance_km"] > distance:
                        unique_stores[key] = {
                            "name": name if name else "Строительный магазин",
                            "address": tags.get("addr:full", "") or f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}".strip(),
                            "phone": tags.get("phone", ""),
                            "website": website,
                            "has_website": bool(website),
                            "lat": store_lat,
                            "lon": store_lon,
                            "distance_km": round(distance, 1)
                        }
                else:
                    unique_stores[key] = {
                        "name": name if name else "Строительный магазин",
                        "address": tags.get("addr:full", "") or f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}".strip(),
                        "phone": tags.get("phone", ""),
                        "website": website,
                        "has_website": bool(website),
                        "lat": store_lat,
                        "lon": store_lon,
                        "distance_km": round(distance, 1)
                    }
        
        stores = list(unique_stores.values())
        stores.sort(key=lambda x: (not x["has_website"], x["distance_km"]))
        
        return stores

    def get_search_links(self, material: str, stores: List[Dict]) -> List[Dict]:
        encoded_material = self._encode_url(material)
        links = []
        
        for store in stores:
            name = store["name"].lower()
            
            if store.get("website"):
                url = store["website"]
                if not url.startswith("http"):
                    url = "https://" + url
            else:
                if "леруа" in name or "leroy" in name:
                    url = f"https://leroymerlin.ru/search/?q={encoded_material}"
                elif "петрович" in name or "petrovich" in name:
                    url = f"https://www.petrovich.ru/catalog/search/?q={encoded_material}"
                elif "всеинструменты" in name or "vseinstrumenti" in name:
                    url = f"https://vseinstrumenti.ru/search/?q={encoded_material}"
                elif "оби" in name or "obi" in name:
                    url = f"https://obi.ru/search/?q={encoded_material}"
                elif "максидом" in name or "maxidom" in name:
                    url = f"https://maxidom.ru/catalog/search/?q={encoded_material}"
                elif "бауцентр" in name or "bauzentr" in name:
                    url = f"https://www.baucentr.ru/search/?q={encoded_material}"
                else:
                    search_query = f"{material} {store['name']}"
                    encoded_search = self._encode_url(search_query)
                    url = f"https://yandex.ru/search/?text={encoded_search}"
            
            links.append({
                "store_name": store["name"],
                "address": store.get("address", ""),
                "distance_km": store["distance_km"],
                "search_url": url,
                "has_website": store.get("has_website", False)
            })
        
        return links

    def get_fallback_links(self, material: str, city: str) -> List[Dict]:
        encoded_material = self._encode_url(material)
        
        return [
            {
                "store_name": "Яндекс.Маркет",
                "address": f"Доставка по городу {city}",
                "distance_km": None,
                "search_url": f"https://market.yandex.ru/search?text={encoded_material}",
                "has_website": True
            },
            {
                "store_name": "Леруа Мерлен (доставка)",
                "address": f"Доставка по городу {city}",
                "distance_km": None,
                "search_url": f"https://leroymerlin.ru/search/?q={encoded_material}",
                "has_website": True
            },
            {
                "store_name": "Петрович (доставка)",
                "address": f"Доставка по городу {city}",
                "distance_km": None,
                "search_url": f"https://www.petrovich.ru/catalog/search/?q={encoded_material}",
                "has_website": True
            },
            {
                "store_name": "OZON Стройка",
                "address": f"Доставка по городу {city}",
                "distance_km": None,
                "search_url": f"https://ozon.ru/search/?text={encoded_material}",
                "has_website": True
            },
            {
                "store_name": "ВсеИнструменты",
                "address": f"Доставка по городу {city}",
                "distance_km": None,
                "search_url": f"https://vseinstrumenti.ru/search/?q={encoded_material}",
                "has_website": True
            }
        ]