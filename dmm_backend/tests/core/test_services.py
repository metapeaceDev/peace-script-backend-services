import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")

from dmm_backend.core.services import transform_dmm_to_editor_profile


@pytest.fixture
def sample_dmm_data():
    """Provides a sample DigitalMindModel data dictionary for testing."""
    return {
        "_id": "507f1f77bcf86cd799439011",
        "model_id": "DM-001",
        "name": "Metta",
        "status_label": "Operational",
        "overall_level": 5,
        "level_progress_percent": 35.0,
        "image_url": "https://firebasestorage.googleapis.com/v0/b/meta-peace.appspot.com/o/Metta_Peace_Alchemist_v2_upscaled.png?alt=media&token=402d4f2e-6f03-453c-8145-4246352fce03",
        "core_state": {
            "level_progress": 350,
            "level_up_threshold": 1000,
        },
        "conscious_profile": {
            "citta": "Observing",
            "sati_power": 85,
            "panna_power": 75,
            "parami_potentials": [
                {"name": "Metta", "value": 90},
                {"name": "Karuna", "value": 80}
            ]
        },
        "kamma_profile": {
            "latent_tendencies": [
                {"name": "Greed", "value": 20},
                {"name": "Aversion", "value": 15},
                {"name": "Delusion", "value": 10}
            ]
        },
        "core_profile": {
            "LatentTendencies_Anusaya": {
                "Greed": 20,
                "Aversion": 15,
                "Delusion": 10
            }
        }
    }

def test_transform_dmm_to_editor_profile_structure(sample_dmm_data):
    """
    Tests that the transformed profile has the correct top-level structure.
    """
    transformed_data = transform_dmm_to_editor_profile(sample_dmm_data)
    
    assert transformed_data["_id"] == "507f1f77bcf86cd799439011"
    assert "model_id" in transformed_data
    assert "character_card" in transformed_data
    assert "core_stats" in transformed_data
    assert "training_module" in transformed_data
    # Ensure original attributes are preserved for UI consumers
    assert transformed_data["name"] == "Metta"
    assert transformed_data["core_profile"]["LatentTendencies_Anusaya"]["Greed"] == 20

def test_transform_dmm_character_card(sample_dmm_data):
    """
    Tests the contents of the 'character_card' section.
    """
    transformed_data = transform_dmm_to_editor_profile(sample_dmm_data)
    card = transformed_data["character_card"]
    
    assert card["name"] == "Metta"
    assert card["status_label"] == "Operational"
    assert card["overall_level"] == 5
    assert card["level_progress_percent"] == 35.0
    assert card["image_url"] == "https://firebasestorage.googleapis.com/v0/b/meta-peace.appspot.com/o/Metta_Peace_Alchemist_v2_upscaled.png?alt=media&token=402d4f2e-6f03-453c-8145-4246352fce03"

def test_transform_dmm_core_stats(sample_dmm_data):
    """
    Tests the contents of the 'core_stats' section.
    """
    transformed_data = transform_dmm_to_editor_profile(sample_dmm_data)
    stats = transformed_data["core_stats"]
    
    # Test latent tendencies
    assert stats["latent_tendencies"]["labels"] == ["Greed", "Aversion", "Delusion"]
    assert stats["latent_tendencies"]["values"] == [20, 15, 10]
    
    # Test summary metrics (parami potentials)
    summary_metrics = stats["summary_metrics"]
    assert len(summary_metrics) == 2
    assert summary_metrics["metta"]["label"] == "Metta"
    assert summary_metrics["metta"]["value"] == 90
    assert summary_metrics["karuna"]["label"] == "Karuna"
    assert summary_metrics["karuna"]["value"] == 80


def test_transform_normalizes_object_id(sample_dmm_data):
    """Ensures that numeric or ObjectId-style identifiers are stringified."""
    payload = dict(sample_dmm_data)
    payload.pop("_id")
    payload["id"] = 123456789

    transformed = transform_dmm_to_editor_profile(payload)

    assert transformed["_id"] == "123456789"
