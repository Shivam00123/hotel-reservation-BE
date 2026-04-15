from ..models.query import Query,RoomQuery,HotelRoomQuery
from ..db_connector.mysql import get_connection
from ..db_connector.redis import redis_client
import json
from typing import List
from .availabilityCheck import checkRoomsAvailability

def addHotelToDB(request:Query):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
            INSERT INTO hotels(country,state,city,name,total_rooms,thumbnail,rating,status,reserved_rooms)
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s)    
            """
    
    values = (
        request.country,
        request.state,
        request.city,
        request.name,
        request.total_rooms,
        request.thumbnail,
        request.rating,
        request.status,
        request.reserved_rooms,
    )

    cursor.execute(query,values)
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": f"Hotel added successfully"}


def getHotels():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT * FROM hotels
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return {"hotels": rows, "message": "Hotels fetched successfully"}


def addRoomToHotel(request:RoomQuery):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO rooms(hotel_id,floor,max_adults,max_children,price) values (%s, %s, %s, %s, %s)
    """

    values = (
        request.hotel_id,
        request.floor,
        request.max_adults,
        request.max_children,
        request.price
    )

    cursor.execute(query,values)
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": f"Room added successfully"}


def getAllHotelsInLocation(state:str,city:str):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT *, COUNT(*) OVER() AS 'hotel_count' FROM hotels WHERE country = "INDIA" AND state = (%s) AND city = (%s)
        ORDER BY rating DESC
    """

    values = (state,city)

    cursor.execute(query,values)
    rows = cursor.fetchall()

    conn.close()
    cursor.close()
    return {"message":f"hotels fetched in {state}, {city} successfully", "hotels":rows}


async def getDataFromCache(key):
    data = await redis_client.get(key)
    if not data:
        return False
    value = json.loads(data)
    return value


async def getDataFromDB(request:HotelRoomQuery,key:str):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
            SELECT id
            FROM hotels
            WHERE country = 'India'
            AND state = (%s)
            AND city = (%s)
            LIMIT 20;
    """

    values = (
        request.state,
        request.city,
    )

    cursor.execute(query,values)
    rows = cursor.fetchall()
    await setDataToCache(rows,key);
    cursor.close()
    conn.close()
    return rows

async def setDataToCache(rows,key):
    await redis_client.set(key, json.dumps(rows), ex=6000000)
    return {
        "message": "Data stored successfully",
        "key": key,
        "value": rows
    }

def getRoomsByHotelId(ids: List[int], adults: int, children: int):
    if not ids:
        return []

    conn = get_connection()
    cursor = conn.cursor()

    flat_ids = list(set(_normalize_hotel_id(item) for item in ids))
    flat_ids = [hotel_id for hotel_id in flat_ids if hotel_id is not None]
    if not flat_ids:
        cursor.close()
        conn.close()
        return []
    placeholders = ','.join(['%s'] * len(flat_ids))

    query = f"""
        SELECT id, hotel_id
        FROM rooms
        WHERE hotel_id IN ({placeholders})
        AND max_adults >= %s
        AND max_children >= %s;
    """

    cursor.execute(query, [*flat_ids, adults, children])
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def _normalize_hotel_id(hotel):
    if isinstance(hotel, (list, tuple)):
        return hotel[0] if hotel else None
    return hotel


async def getDataInBatches(
    hotels: List[int],
    request,
    start=0,
    end=5,
    collected_hotels=None
):
    if collected_hotels is None:
        collected_hotels = []

    requested_adults = request.capacity.adults
    requested_children = request.capacity.children or 0
    startDate = request.startDate
    endDate = request.endDate

    batch = hotels[start:end]

    # 🚨 No more data
    if not batch:
        return {
            "hotels": collected_hotels,
            "next_cursor": None
        }

    # Normalize
    normalized_batch = [_normalize_hotel_id(hotel) for hotel in batch]
    normalized_batch = [h for h in normalized_batch if h is not None]

    if not normalized_batch:
        return await getDataInBatches(
            hotels, request, end, end + 5, collected_hotels
        )

    # Rooms
    rooms = getRoomsByHotelId(normalized_batch, requested_adults, requested_children)

    if not rooms:
        return await getDataInBatches(
            hotels, request, end, end + 5, collected_hotels
        )

    room_ids = [row[0] for row in rooms]
    room_to_hotel = {row[0]: row[1] for row in rooms}

    response = await checkRoomsAvailability(room_ids, startDate, endDate)

    available_room_ids = response.get("response", {}).get("available_room_ids", [])

    available_hotel_ids = {
        room_to_hotel[room_id]
        for room_id in available_room_ids
        if room_id in room_to_hotel
    }

    filtered_hotels = [
        hotel_id for hotel_id in normalized_batch
        if hotel_id in available_hotel_ids
    ]

    collected_hotels.extend(filtered_hotels)

    # ✅ STOP CONDITION
    if len(collected_hotels) >= 10:
        return {
            "hotels": collected_hotels[:10],
            "next_cursor": end   # 👈 next page starts from here
        }

    # 🔁 Continue recursion
    return await getDataInBatches(
        hotels,
        request,
        end,
        end + 5,
        collected_hotels
    )



async def getHotelsInlocation(request: HotelRoomQuery):
    key = f"India|{request.state}|{request.city}"

    hotels = await getDataFromCache(key)

    if not hotels:
        await getDataFromDB(request, key)
        hotels = await getDataFromCache(key)

    result = await getDataInBatches(hotels, request, request.cursor, request.cursor + 5)

    return {
        "message": "hotel fetched successfully",
        "hotels": result["hotels"],
        "next_cursor": result["next_cursor"]
    }
