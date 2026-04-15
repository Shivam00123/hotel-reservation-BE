from pydantic import BaseModel
from datetime import date
from typing import Literal,Optional


class Capacity(BaseModel):
    adults:int
    children:Optional[int] = None



class HotelRoomQuery(BaseModel):
    country:str = "India"
    city:str
    state:str
    startDate:date
    endDate:date
    capacity:Capacity
    page:int = 1
    page_size:int = 20,
    cursor:Optional[int] = 0

class Query(BaseModel):
    country:str
    state:str
    city:str
    name:str
    total_rooms:int
    thumbnail:str
    rating:float
    status: Literal["Open","Closed"] = "Open"
    reserved_rooms:int


class RoomQuery(BaseModel):
    hotel_id:int
    floor:int
    max_adults:int
    max_children:int
    price:float


class HotelDetailQuery(BaseModel):
    hotel_id:int
    startDate:date
    endDate:date
    capacity:Capacity

    