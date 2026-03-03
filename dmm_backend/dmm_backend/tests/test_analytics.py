import pytest


@pytest.mark.asyncio
async def test_kamma_by_status_empty(async_client):
    resp = await async_client.get("/api/v1/analytics/kamma/by_status", params={"model_id": "test_model_001"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)