import re
from typing import Dict


class ParameterExtractor:
    MATERIALS = {
        "газобетон": ["газобетон", "газоблок", "пеноблок", "ячеистый бетон"],
        "кирпич": ["кирпич", "кирпичный"],
        "брус": ["брус", "бревно", "сруб", "дерево"],
        "каркас": ["каркас", "каркасный", "щитовой"],
    }
    
    SOIL_TYPES = {
        "песок": ["песок", "песчаный", "песчаная"],
        "суглинок": ["суглинок", "суглинистый"],
        "глина": ["глина", "глинистый", "глинистая"],
        "торф": ["торф", "болото", "болотистый"],
        "скальный": ["скальный", "скала", "каменистый", "крупный песок"],
        "сильнопучинистая глина": ["сильнопучинистая глина", "сильнопучинистая", "сильно пучинистая"]
    }
    
    REGIONS = {
        "москва": ["москва", "подмосковье", "московская область"],
        "сургут": ["сургут", "хмао"],
        "калуга": ["калуга"],
        "тверь": ["тверь"],
        "рязань": ["рязань"],
        "краснодар": ["краснодар"],
    }
    
    def extract(self, text: str) -> Dict:
        text_lower = text.lower()
        result = {
            "material": None,
            "floors": None,
            "width": 10,
            "length": 10,
            "city": None,
            "soil": None,
            "budget": None,
            "self_build": False,
            "desired_month": None
        }
        
        for material, keywords in self.MATERIALS.items():
            if any(kw in text_lower for kw in keywords):
                result["material"] = material
                break
        
        floors_match = re.search(r'(\d+)\s*этаж', text_lower)
        if floors_match:
            result["floors"] = int(floors_match.group(1))
        
        size_match = re.search(r'(\d+)\s*[хx]\s*(\d+)', text_lower)
        if size_match:
            result["width"] = int(size_match.group(1))
            result["length"] = int(size_match.group(2))
        
        for region, keywords in self.REGIONS.items():
            if any(kw in text_lower for kw in keywords):
                result["city"] = region
                break
        
        # Сначала проверяем сильнопучинистую глину
        if any(kw in text_lower for kw in ["сильнопучинистая глина", "сильнопучинистая", "сильно пучинистая"]):
            result["soil"] = "сильнопучинистая глина"
        else:
            for soil, keywords in self.SOIL_TYPES.items():
                if any(kw in text_lower for kw in keywords):
                    result["soil"] = soil
                    break
        
        budget_match = re.search(r'бюджет\s*(\d+)', text_lower)
        if budget_match:
            result["budget"] = int(budget_match.group(1))
        
        if any(word in text_lower for word in ["сам", "своими руками", "без подрядчика"]):
            result["self_build"] = True
        
        months = ["январь", "февраль", "март", "апрель", "май", "июнь",
                  "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]
        for month in months:
            if month in text_lower:
                result["desired_month"] = month
                break
        
        return result