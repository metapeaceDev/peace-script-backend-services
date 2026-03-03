import pytest


@pytest.mark.asyncio
async def test_list_dream_journals(async_client):
	resp = await async_client.get("/api/v1/dream-journals/")
	assert resp.status_code == 200
	data = resp.json()
	assert isinstance(data, list)
