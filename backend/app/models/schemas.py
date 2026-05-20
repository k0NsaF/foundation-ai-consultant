from pydantic import BaseModel
from typing import Optional, List, Dict


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