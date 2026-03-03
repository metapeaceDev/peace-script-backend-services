import pytest
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_dream_journals_filters(async_client):
    # Seed sample dreams via API
    base = datetime.utcnow().replace(microsecond=0)
    dreams = [
        {"model_id": "m1", "dream_text": "calm sea", "tags": ["peaceful", "joyful"], "emotion_score": 0.9, "date": (base - timedelta(days=2)).isoformat()},
        {"model_id": "m1", "dream_text": "storm sky", "tags": ["anxious"], "emotion_score": 0.1, "date": (base - timedelta(days=1)).isoformat()},
        {"model_id": "m2", "dream_text": "forest", "tags": ["nature"], "emotion_score": 0.5, "date": base.isoformat()},
    ]
    for d in dreams:
        r = await async_client.post("/api/v1/dream-journals/", json=d)
        assert r.status_code == 201

    # Filter by model_id
    r = await async_client.get("/api/v1/dream-journals/", params={"model_id": "m1"})
    assert r.status_code == 200
    data = r.json()
    assert all(d["model_id"] == "m1" for d in data)

    # Filter by tags (must include all)
    r = await async_client.get("/api/v1/dream-journals/", params={"tags": "peaceful,joyful"})
    assert r.status_code == 200
    data = r.json()
    assert any(d["dream_text"] == "calm sea" for d in data)

    # Filter by emotion_gte
    r = await async_client.get("/api/v1/dream-journals/", params={"emotion_gte": 0.5})
    assert r.status_code == 200
    data = r.json()
    # Some legacy docs may not have emotion_score; ensure none with explicit value violate the threshold
    assert all((d.get("emotion_score") is None) or (float(d.get("emotion_score")) >= 0.5) for d in data)

    # Filter by date range
    start = (base - timedelta(days=1)).date().isoformat()
    end = base.date().isoformat()
    r = await async_client.get("/api/v1/dream-journals/", params={"from_": start, "to": end})
    assert r.status_code == 200
    data = r.json()
    # Should include the last two entries (storm sky, forest)
    texts = [d["dream_text"] for d in data]
    assert "storm sky" in texts and "forest" in texts


@pytest.mark.asyncio
async def test_simulation_timelines_filters(async_client):
    # Seed sample timelines via API
    for t in [
        {"model_id": "m1", "simulation_id": "s1", "timeline_type": "physical", "events": []},
        {"model_id": "m1", "simulation_id": "s2", "timeline_type": "mental", "events": []},
    ]:
        r = await async_client.post("/api/v1/simulation-timelines/", json=t)
        assert r.status_code == 201

    # Filter by model and type
    r = await async_client.get("/api/v1/simulation-timelines/", params={"model_id": "m1", "type": "mental"})
    assert r.status_code == 200
    data = r.json()
    assert all(d.get("timeline_type") == "mental" for d in data)
