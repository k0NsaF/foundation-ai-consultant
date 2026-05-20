from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, List

from app.pipeline.extractor import ParameterExtractor
from app.pipeline.enricher import DataEnricher
from app.rag.retriever import RAGRetriever
from app.pipeline.cost_calc import CostCalculator
from app.pipeline.weather import WeatherAdvisor
from app.pipeline.geocoding import GeocodingService
from app.pipeline.store_locator import StoreLocator
from app.pipeline.generator import AnswerGenerator
from app.config import Config

router = APIRouter()

extractor = ParameterExtractor()
enricher = DataEnricher()
retriever = RAGRetriever()
cost_calc = CostCalculator()
weather_advisor = WeatherAdvisor()
geocoding = GeocodingService()
store_locator = StoreLocator()
generator = AnswerGenerator()


class ConsultationRequest(BaseModel):
    user_input: str
    city: str
    address: Optional[str] = None
    desired_month: Optional[str] = None
    budget: Optional[str] = None
    self_build: bool = False


class ConsultationResponse(BaseModel):
    foundation_type: str
    cost_estimate: Dict
    weather_recommendation: Dict
    stores: List[Dict]
    answer: str
    sources: List[str]


def determine_foundation_type(docs: list, params: dict) -> str:
    soil = params.get("soil", "не указан").lower()
    load = params.get("total_load_tons", 0)
    material = params.get("material", "не указан").lower()
    freezing_depth = params.get("freezing_depth", 1.5)
    
    print(f"=== ОТЛАДКА routes: soil={soil}, load={load}, material={material}, freezing_depth={freezing_depth} ===")
    
    # 1. Свайный фундамент (СП 24.13330.2011)
    if "сильнопучинистая" in soil or soil in ["торф", "болото"]:
        return "Свайно-винтовой фундамент (по СП 24.13330.2011)"
    
    if soil in ["глина", "суглинок"] and freezing_depth > 2.0:
        return "Свайно-винтовой фундамент (по СП 24.13330.2011)"
    
    # 2. Непучинистые грунты
    if soil in ["песок", "супесь", "скальный", "крупный песок", "скала"]:
        if material in ["дерево", "брус", "каркас"] and load < 8:
            return "Столбчатый фундамент"
        return "Ленточный фундамент (по СП 22.13330.2016)"
    
    # 3. Пучинистые грунты (глина, суглинок)
    if soil in ["глина", "суглинок"]:
        if material in ["дерево", "брус", "каркас"] and load <= 15:
            return "Мелкозаглубленная лента (СП 22.13330.2016)"
        elif load > 15:
            return "УШП утепленная шведская плита"
        else:
            return "Мелкозаглубленная лента (СП 22.13330.2016)"
    
    # 4. Столбчатый для очень лёгких
    if material in ["дерево", "брус", "каркас"] and load < 8:
        return "Столбчатый фундамент"
    
    return "Ленточный фундамент (по СП 22.13330.2016)"


@router.post("/consult", response_model=ConsultationResponse)
async def consult(request: ConsultationRequest):
    params = extractor.extract(request.user_input)
    params["city"] = request.city
    params["address"] = request.address
    params["desired_month"] = request.desired_month
    params["self_build"] = request.self_build

    enriched = enricher.enrich(params)

    coords = None
    if request.city:
        coords = geocoding.get_coordinates(request.city, request.address)

    if coords:
        print(f"Координаты для {request.city}: широта={coords[0]}, долгота={coords[1]}")
    else:
        print(f"Не удалось получить координаты для города: {request.city}")

    docs = retriever.retrieve(request.user_input, enriched)

    foundation_type = determine_foundation_type(docs, enriched)

    cost = cost_calc.calculate(foundation_type, enriched)

    weather = weather_advisor.get_recommendation(
        region=request.city,
        desired_month=request.desired_month,
        lat=coords[0] if coords else None,
        lon=coords[1] if coords else None
    )

    stores = []
    if coords:
        stores = store_locator.find_nearby_stores(coords[0], coords[1])
    
    print(f"Найдено магазинов: {len(stores)}")

    store_links = store_locator.get_search_links("бетон", stores)
    if not store_links:
        store_links = store_locator.get_fallback_links(
            "бетон", request.city
        )

    answer = generator.generate(
        request.user_input, docs, cost, weather, store_links, enriched
    )

    sources = list(set([
        doc.get("source", "") for doc in docs if doc.get("source")
    ]))

    return ConsultationResponse(
        foundation_type=foundation_type,
        cost_estimate=cost,
        weather_recommendation=weather,
        stores=store_links,
        answer=answer,
        sources=sources
    )