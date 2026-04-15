import httpx


async def postRequest(url,payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(url,json=payload)

    response.raise_for_status()

    if not response.content:
        return {}

    try:
        return response.json()
    except ValueError:
        return {"raw_response": response.text}