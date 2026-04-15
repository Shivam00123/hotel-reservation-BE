from fastapi import FastAPI,Query as BaseModelQuery
from datetime import date
from .models.query import Query,RoomQuery,HotelRoomQuery
from .controllers.manage_hotels import addHotelToDB,getHotels,addRoomToHotel,getAllHotelsInLocation,getHotelsInlocation

app = FastAPI()

@app.post("/add-hotel")
def addHotel(request:Query):
    return addHotelToDB(request)

@app.get("/")
def read_hotels():
    return getHotels()

@app.post("/add-rooms")
def add_room(request:RoomQuery):
    return addRoomToHotel(request)


@app.get("/get-hotel-in-location")
def get_hotelsInLocation(state:str = BaseModelQuery(...,description="State"),city:str = BaseModelQuery(...,description="City")):
    return getAllHotelsInLocation(state,city)


@app.post("/get-available-hotel-rooms")
async def get_available_hotel_rooms(request:HotelRoomQuery):
    return await getHotelsInlocation(request)
