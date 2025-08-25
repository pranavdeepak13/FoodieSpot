from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Restaurant(BaseModel):
    id: int
    name: str
    cuisine: str
    location: str
    price_range: str
    rating: float
    capacity: int
    available_times: List[str]
    features: List[str]

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    intent: str
    data: Optional[dict] = None

class BookingRequest(BaseModel):
    restaurant_name: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    party_size: Optional[int] = None

class Booking(BaseModel):
    id: str
    restaurant_name: str
    date: str
    time: str
    party_size: int
    status: str
    created_at: datetime