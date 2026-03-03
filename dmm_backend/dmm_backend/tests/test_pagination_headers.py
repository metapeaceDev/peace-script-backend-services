import pytest

@pytest.mark.asyncio
async def test_dreams_pagination_headers(async_client):
    # Seed more than default limit to test headers
    for i in range(3):
        r = await async_client.post(
            "/api/v1/dream-journals/",
            json={
                "model_id": "test_model_001",
                "dream_text": f"dream {i}",
                "tags": ["peaceful"],
            },
        )
        assert r.status_code == 201

    # Request with small limit
    resp = await async_client.get("/api/v1/dream-journals/?limit=2")
    assert resp.status_code == 200
    assert resp.headers.get("x-page-skip") == "0"
    assert resp.headers.get("x-page-limit") == "2"
    assert resp.headers.get("x-returned") == "2"
    assert resp.headers.get("x-next-skip") == "2"
    assert "x-total-count" in resp.headers
    assert "x-has-more" in resp.headers
    assert "x-next-after-id" in resp.headers

    first_page = resp.json()
    assert isinstance(first_page, list)
    assert len(first_page) == 2

    next_after_id = resp.headers.get("x-next-after-id")
    # Request next page using cursor
    resp2 = await async_client.get(f"/api/v1/dream-journals/?limit=2&after_id={next_after_id}")
    assert resp2.status_code == 200
    assert resp2.headers.get("x-page-skip") == "0"  # skip is independent of cursor
    assert resp2.headers.get("x-page-limit") == "2"
    assert resp2.headers.get("x-returned") in {"1", "2"}


@pytest.mark.asyncio
async def test_timelines_pagination_headers(async_client):
    # Seed timelines
    for i in range(3):
        r = await async_client.post(
            
            "/api/v1/simulation-timelines/",
            json={
                "model_id": "test_model_001",
                "simulation_id": f"sim{i}",
                "timeline_type": "physical",
                "events": [{"type": "start", "payload": {}}],
            },
        )
        assert r.status_code == 201

    # First page with limit 2
    resp = await async_client.get("/api/v1/simulation-timelines/?limit=2")
    assert resp.status_code == 200
    assert resp.headers.get("x-page-skip") == "0"
    assert resp.headers.get("x-page-limit") == "2"
    assert resp.headers.get("x-returned") == "2"
    assert resp.headers.get("x-next-skip") == "2"
    assert "x-total-count" in resp.headers
    assert "x-has-more" in resp.headers
    assert "x-next-after-id" in resp.headers

    next_after_id = resp.headers.get("x-next-after-id")
    resp2 = await async_client.get(f"/api/v1/simulation-timelines/?limit=2&after_id={next_after_id}")
    assert resp2.status_code == 200
    assert resp2.headers.get("x-page-limit") == "2"
    assert resp2.headers.get("x-returned") in {"1", "2"}
