from pydantic import BaseModel
from datetime import date
from typing import List


class HotelIDSQuery(BaseModel):
    hotel_id:int
    room_id:int
    available:bool
    startDate:date
    endDate:date


class AvailabilityQuery(BaseModel):
    room_ids:List[int]
    startDate:date
    endDate:date