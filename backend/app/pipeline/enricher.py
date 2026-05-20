import json
from pathlib import Path
from typing import Dict
from app.config import Config


class DataEnricher:
    def __init__(self):
        freezing_path = Path(Config.PROCESSED_DATA_DIR) / "freezing_map.json"
        loads_path = Path(Config.PROCESSED_DATA_DIR) / "loads.json"

        with open(freezing_path, "r", encoding="utf-8") as f:
            self.freezing_map = json.load(f)

        with open(loads_path, "r", encoding="utf-8") as f:
            self.loads_table = json.load(f)

    def enrich(self, params: Dict) -> Dict:
        result = params.copy()

        city = params.get("city")
        if city and city in self.freezing_map:
            result["freezing_depth"] = self.freezing_map[city]
        else:
            result["freezing_depth"] = 1.5

        material = params.get("material")
        floors = params.get("floors", 1)
        width = params.get("width", 10)
        length = params.get("length", 10)

        if material and material in self.loads_table:
            load_per_sqm = self.loads_table[material].get(str(floors), 120)
            area = width * length
            result["total_load_tons"] = round((load_per_sqm * area) / 1000, 1)
        else:
            result["total_load_tons"] = 0

        if not params.get("soil"):
            result["soil"] = "суглинок"

        region_map = {
            "москва": "москва",
            "сургут": "сургут",
            "калуга": "калуга",
            "тверь": "тверь",
            "рязань": "рязань",
            "краснодар": "краснодар",
            "спб": "санкт-петербург",
            "санкт-петербург": "санкт-петербург",
            "новосибирск": "новосибирск",
            "псков": "псков",
            "петрозаводск": "петрозаводск",
            "ярославль": "ярославль",
            "кострома": "кострома"
        }

        city_lower = params.get("city", "").lower()
        result["region"] = region_map.get(city_lower, "москва")

        return result