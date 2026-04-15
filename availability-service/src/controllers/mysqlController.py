from ..models.query import HotelIDSQuery,AvailabilityQuery
from ..db_connector.mysql import get_connection

def addHotelBookingToInventory(request:HotelIDSQuery):
    pass

def checkHotelAvailability(request:AvailabilityQuery):
    if not request.room_ids:
        return {"available_room_ids": []}
    

    conn = get_connection()
    cursor = conn.cursor()
    startDate = request.startDate
    endDate = request.endDate
    room_ids = list(set(request.room_ids))
    placeholders = ",".join(["%s"] * len(room_ids))

    # Fetch overlapping bookings for requested room IDs.
    # Any room with an overlap is unavailable for this search window.
    query = f"""
        SELECT DISTINCT hi.hotel_id
        FROM hotel_inventory hi
        WHERE hi.room_id IN ({placeholders})
        AND NOT (
            hi.endDate <= %s
            OR hi.startDate >= %s
        );
    """
    values = [*room_ids, startDate, endDate]

    cursor.execute(query,values)
    rows = cursor.fetchall()
    booked_room_ids = {row[0] for row in rows}
    available_room_ids = [room_id for room_id in room_ids if room_id not in booked_room_ids]

    conn.close()
    cursor.close()

    return {"available_room_ids": available_room_ids}