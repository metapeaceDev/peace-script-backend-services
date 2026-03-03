import httpx
import asyncio

async def main():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("http://localhost:8003/chat", json={"text": "Search for the latest OpenAI Sora news."})
            if resp.status_code == 200:
                print(f"Success! Reply: {resp.json().get('reply')[:200]}...")  # Print first 200 chars
            else:
                print(f"Error: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())