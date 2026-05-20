from typing import Dict


class CostCalculator:
    PRICES = {
        "concrete_m3": 5500,
        "rebar_ton": 60000,
        "formwork_m2": 800,
        "pile_108mm": 4500,
        "pile_installation": 2500,
        "concrete_pouring_m3": 4000,
        "delivery_percent": 0.05,
        "overhead_percent": 0.15
    }

    def _determine_foundation_type(self, params: Dict) -> str:
        soil = params.get("soil", "не указан").lower()
        load = params.get("total_load_tons", 0)
        material = params.get("material", "не указан").lower()
        freezing_depth = params.get("freezing_depth", 1.5)
        
        print(f"=== ОТЛАДКА cost_calc: soil={soil}, load={load}, material={material}, freezing_depth={freezing_depth} ===")
        
        if "сильнопучинистая" in soil or soil in ["торф", "болото"]:
            return "Свайно-винтовой фундамент (по СП 24.13330.2011)"
        
        if soil in ["глина", "суглинок"] and freezing_depth > 2.0:
            return "Свайно-винтовой фундамент (по СП 24.13330.2011)"
        
        if soil in ["песок", "супесь", "скальный", "крупный песок", "скала"]:
            if material in ["дерево", "брус", "каркас"] and load < 8:
                return "Столбчатый фундамент"
            return "Ленточный фундамент (по СП 22.13330.2016)"
        
        if soil in ["глина", "суглинок"]:
            if material in ["дерево", "брус", "каркас"] and load <= 15:
                return "Мелкозаглубленная лента (СП 22.13330.2016)"
            elif load > 15:
                return "УШП утепленная шведская плита"
            else:
                return "Мелкозаглубленная лента (СП 22.13330.2016)"
        
        if material in ["дерево", "брус", "каркас"] and load < 8:
            return "Столбчатый фундамент"
        
        return "Ленточный фундамент (по СП 22.13330.2016)"

    def calculate_slab(self, width: float, length: float, thickness: float = 0.3) -> Dict:
        area = width * length
        volume = area * thickness

        materials = {
            "concrete": volume * self.PRICES["concrete_m3"],
            "rebar": (area * 0.1) * self.PRICES["rebar_ton"],
            "formwork": (width + length) * 2 * self.PRICES["formwork_m2"]
        }
        materials_total = sum(materials.values())

        work = {
            "concrete_pouring": volume * self.PRICES["concrete_pouring_m3"],
            "rebar_work": materials["rebar"] * 0.3
        }
        work_total = sum(work.values())

        delivery = materials_total * self.PRICES["delivery_percent"]
        overhead = (materials_total + work_total) * self.PRICES["overhead_percent"]

        return {
            "type": "УШП утепленная шведская плита",
            "materials": round(materials_total, 0),
            "work": round(work_total, 0),
            "delivery": round(delivery, 0),
            "overhead": round(overhead, 0),
            "total": round(materials_total + work_total + delivery + overhead, 0),
            "breakdown": materials
        }

    def calculate_piles(self, width: float, length: float, pile_count: int = None) -> Dict:
        perimeter = (width + length) * 2
        if not pile_count:
            pile_count = max(4, int(perimeter / 2))

        materials = {"piles": pile_count * self.PRICES["pile_108mm"]}
        materials_total = sum(materials.values())

        work = {"pile_installation": pile_count * self.PRICES["pile_installation"]}
        work_total = sum(work.values())

        delivery = materials_total * self.PRICES["delivery_percent"]
        overhead = (materials_total + work_total) * self.PRICES["overhead_percent"]

        return {
            "type": "Свайно-винтовой фундамент",
            "pile_count": pile_count,
            "materials": round(materials_total, 0),
            "work": round(work_total, 0),
            "delivery": round(delivery, 0),
            "overhead": round(overhead, 0),
            "total": round(materials_total + work_total + delivery + overhead, 0),
            "breakdown": materials
        }

    def calculate_shallow_strip(self, width: float, length: float) -> Dict:
        perimeter = (width + length) * 2
        volume = perimeter * 0.4 * 0.5
        
        materials = {
            "concrete": volume * self.PRICES["concrete_m3"],
            "rebar": (volume * 0.08) * self.PRICES["rebar_ton"],
            "formwork": perimeter * 0.8 * self.PRICES["formwork_m2"]
        }
        materials_total = sum(materials.values())

        work = {
            "concrete_pouring": volume * self.PRICES["concrete_pouring_m3"],
            "rebar_work": materials["rebar"] * 0.3
        }
        work_total = sum(work.values())

        delivery = materials_total * self.PRICES["delivery_percent"]
        overhead = (materials_total + work_total) * self.PRICES["overhead_percent"]

        return {
            "type": "Мелкозаглубленная лента",
            "materials": round(materials_total, 0),
            "work": round(work_total, 0),
            "delivery": round(delivery, 0),
            "overhead": round(overhead, 0),
            "total": round(materials_total + work_total + delivery + overhead, 0),
            "breakdown": materials
        }

    def calculate_strip(self, width: float, length: float) -> Dict:
        perimeter = (width + length) * 2
        volume = perimeter * 0.5 * 1.5
        
        materials = {
            "concrete": volume * self.PRICES["concrete_m3"],
            "rebar": (volume * 0.1) * self.PRICES["rebar_ton"],
            "formwork": perimeter * 2 * self.PRICES["formwork_m2"]
        }
        materials_total = sum(materials.values())

        work = {
            "concrete_pouring": volume * self.PRICES["concrete_pouring_m3"],
            "rebar_work": materials["rebar"] * 0.3
        }
        work_total = sum(work.values())

        delivery = materials_total * self.PRICES["delivery_percent"]
        overhead = (materials_total + work_total) * self.PRICES["overhead_percent"]

        return {
            "type": "Ленточный фундамент",
            "materials": round(materials_total, 0),
            "work": round(work_total, 0),
            "delivery": round(delivery, 0),
            "overhead": round(overhead, 0),
            "total": round(materials_total + work_total + delivery + overhead, 0),
            "breakdown": materials
        }

    def calculate(self, foundation_type: str, params: Dict) -> Dict:
        print(f"=== ОТЛАДКА calculate: foundation_type на входе={foundation_type} ===")
        
        width = params.get("width", 10)
        length = params.get("length", 10)
        self_build = params.get("self_build", False)
        
        actual_type = self._determine_foundation_type(params)
        print(f"=== ОТЛАДКА calculate: actual_type после определения={actual_type} ===")
        
        if "УШП" in actual_type:
            result = self.calculate_slab(width, length)
        elif "Свайно" in actual_type:
            result = self.calculate_piles(width, length)
        elif "Мелкозаглубленная" in actual_type:
            result = self.calculate_shallow_strip(width, length)
        else:
            result = self.calculate_strip(width, length)
        
        if self_build:
            result["work"] = 0
            result["total"] = (
                result["materials"] + result["delivery"] + result["overhead"]
            )
            result["self_build"] = True
        
        return result