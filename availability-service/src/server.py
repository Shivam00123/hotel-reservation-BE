from fastapi import FastAPI
from .models.query import HotelIDSQuery,AvailabilityQuery
from .controllers.mysqlController import addHotelBookingToInventory,checkHotelAvailability

app = FastAPI()


@app.post("/check-hotel-availability")
def addHotelBooking(request:HotelIDSQuery):
    return addHotelBookingToInventory(request)


@app.post("/check-availability")
def checkAvailabilityOfHotel(request:AvailabilityQuery):
    return checkHotelAvailability(request)