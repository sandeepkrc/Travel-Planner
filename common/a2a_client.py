import httpx


async def call_agent(url, payload):

    async with httpx.AsyncClient() as client:

        response = await client.post(url, json=payload, timeout=60.0)
        if response.status_code == 404:
            raise ValueError(f"Agent not found at {url}")
        response.raise_for_status()
        return response.json()
