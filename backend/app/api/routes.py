from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from ..models import ConsultRequest, ConsultResponse
from ..pipeline.extractor import ParameterExtractor
from ..pipeline.enricher import DataEnricher
from ..pipeline.cost_calc import CostCalculator
from ..pipeline.weather import WeatherAdvisor
from ..pipeline.geocoding import GeocodingService
from ..pipeline.store_locator import StoreLocator
from ..pipeline.generator import AnswerGenerator
from ..rag.retriever import RAGRetriever
import os

router = APIRouter()

templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
templates = Jinja2Templates(directory=templates_dir)

extractor = ParameterExtractor()
enricher = DataEnricher()
retriever = RAGRetriever()
cost_calc = CostCalculator()
weather_advisor = WeatherAdvisor()
geocoding = GeocodingService()
store_locator = StoreLocator()
generator = AnswerGenerator()

@router.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/consult", response_model=ConsultResponse)
async def consult(request: ConsultRequest):
    params = extractor.extract(request.user_input)
    params["city"] = request.city
    params["address"] = request.address
    params["desired_month"] = request.desired_month
    params["self_build"] = request.self_build

    enriched = enricher.enrich(params)

    coords = None
    if request.city:
        coords = geocoding.get_coordinates(request.city, request.address)

    # RAG поиск
    docs = retriever.retrieve(request.user_input, enriched)

    # Определяем тип фундамента (пока заглушка)
    foundation_type = "Ленточный фундамент"
    if docs:
        for doc in docs:
            if "свайный" in doc["text"].lower():
                foundation_type = "Свайно-винтовой фундамент"
            elif "УШП" in doc["text"]:
                foundation_type = "УШП утепленная шведская плита"

    cost = cost_calc.calculate(foundation_type, enriched)

    weather = weather_advisor.get_recommendation(
        region=enriched.get("region", "подмосковье"),
        desired_month=request.desired_month,
        lat=coords[0] if coords else None,
        lon=coords[1] if coords else None
    )

    stores = []
    if coords:
        stores = store_locator.find_nearby_stores(coords[0], coords[1])

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