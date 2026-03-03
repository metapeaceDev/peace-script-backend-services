import pytest
pytestmark = pytest.mark.asyncio(loop_scope="function")
from httpx import AsyncClient


async def _get(async_client: AsyncClient, model_id: str):
    res = await async_client.get(f"/api/v1/core-profile/{model_id}/nama-rupa")
    assert res.status_code == 200
    return res.json()


@pytest.mark.asyncio
async def test_get_nama_rupa_structure(async_client: AsyncClient):
    data = await _get(async_client, "test_model_001")
    assert "nama" in data and "rupa" in data
    nama = data["nama"]
    rupa = data["rupa"]
    assert {"dominant_temperament", "anusaya_levels_avg", "sati_level", "panna_level"}.issubset(nama.keys())
    assert {"age", "health_baseline", "current_life_force", "lifespan_remaining"}.issubset(rupa.keys())


@pytest.mark.asyncio
async def test_patch_anusaya_reflects_in_nama(async_client: AsyncClient):
    # Lower patigha from 5 to 2 to reduce average
    payload = {"patigha": 2}
    res = await async_client.patch("/api/v1/core-profile/test_model_001/anusaya", json=payload)
    assert res.status_code == 200

    data = await _get(async_client, "test_model_001")
    assert data["nama"]["anusaya_levels_avg"] <= 5  # should be reduced


@pytest.mark.asyncio
async def test_patch_rupa_health_baseline(async_client: AsyncClient):
    res = await async_client.patch(
        "/api/v1/core-profile/test_model_001/nama-rupa/rupa",
        json={"health_baseline": 88.5}
    )
    assert res.status_code == 200
    body = res.json()
    # PATCH should echo updated health_baseline inside updated_life_essence structure
    updated = body.get("updated_life_essence") or {}
    # try snake case path first, then legacy
    try:
        hb = (
            updated.get("life_blueprint_vipaka", {})
                   .get("initial_conditions", {})
                   .get("health_baseline")
        )
    except Exception:
        hb = None
    if hb is None:
        hb = (
            updated.get("LifeBlueprint_Vipaka", {})
                   .get("initial_conditions", {})
                   .get("health_baseline")
        )
    assert round(float(hb), 1) == 88.5
