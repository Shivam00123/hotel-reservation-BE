
from ..utils.apiCall import postRequest
from typing import List
from datetime import date


async def checkRoomsAvailability(rooms:List[int],startDate:date,endDate:date):
    payload = {
        "room_ids":rooms,
        "startDate":startDate.isoformat(),
        "endDate":endDate.isoformat()
    }

    url = "http://localhost:8001/check-availability"

    response = await postRequest(url,payload)

    return {"response":response}

