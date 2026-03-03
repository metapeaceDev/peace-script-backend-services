"""
Phase 2: User Authentication Tests
Tests for FastAPI-Users authentication system with MindState integration

Test Coverage:
- User registration
- User login (JWT token)
- Protected endpoint access
- MindState auto-creation
- User data isolation
- Authorization checks
"""

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.fixture
async def test_user_credentials():
    """Generate unique test user credentials"""
    import time
    timestamp = int(time.time() * 1000)
    return {
        "email": f"test-auth-{timestamp}@peacescript.com",
        "password": "SecureTestPass123!",
        "display_name": f"Test Auth User {timestamp}",
        "preferred_language": "th"
    }


@pytest.fixture
async def registered_user(test_user_credentials):
    """Register a test user and return credentials + user data"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/auth/register", json=test_user_credentials)
        assert response.status_code == 201, f"Registration failed: {response.text}"
        
        user_data = response.json()
        return {
            **test_user_credentials,
            "user_id": user_data["id"],
            "user_data": user_data
        }


@pytest.fixture
async def auth_token(registered_user):
    """Get JWT token for registered user"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/jwt/login",
            data={
                "username": registered_user["email"],
                "password": registered_user["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        token_data = response.json()
        return token_data["access_token"]


# === Test Cases ===

@pytest.mark.asyncio
async def test_user_registration_success(test_user_credentials):
    """Test successful user registration"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/auth/register", json=test_user_credentials)
        
        assert response.status_code == 201
        data = response.json()
        
        # Check returned user data
        assert "id" in data
        assert data["email"] == test_user_credentials["email"]
        assert data["display_name"] == test_user_credentials["display_name"]
        assert data["preferred_language"] == "th"
        assert data["is_active"] is True
        assert data["is_verified"] is False
        assert data["is_superuser"] is False
        assert "hashed_password" not in data  # Password should not be exposed


@pytest.mark.asyncio
async def test_user_registration_duplicate_email(registered_user):
    """Test registration with duplicate email fails"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Try to register with same email
        response = await client.post("/api/auth/register", json={
            "email": registered_user["email"],
            "password": "AnotherPassword123!",
            "display_name": "Another User"
        })
        
        assert response.status_code == 400
        assert "REGISTER_USER_ALREADY_EXISTS" in response.text


@pytest.mark.asyncio
async def test_user_login_success(registered_user):
    """Test successful user login"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/jwt/login",
            data={
                "username": registered_user["email"],
                "password": registered_user["password"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 50  # JWT tokens are long


@pytest.mark.asyncio
async def test_user_login_wrong_password(registered_user):
    """Test login with wrong password fails"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/jwt/login",
            data={
                "username": registered_user["email"],
                "password": "WrongPassword123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 400
        assert "LOGIN_BAD_CREDENTIALS" in response.text


@pytest.mark.asyncio
async def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without token fails"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/users/me")
        
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_token(registered_user, auth_token):
    """Test accessing protected endpoint with valid token"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == registered_user["email"]
        assert data["id"] == registered_user["user_id"]


@pytest.mark.asyncio
async def test_mindstate_auto_creation(registered_user, auth_token):
    """Test that MindState is automatically created on registration"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Get user's MindState
        response = await client.get(
            f"/api/v1/mind-states/{registered_user['user_id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        mind_state = response.json()
        
        # Verify MindState was created
        assert mind_state["user_id"] == registered_user["user_id"]
        assert "sila" in mind_state
        assert "samadhi" in mind_state
        assert "panna" in mind_state
        
        # Check that user has mind_state_id linked
        user_response = await client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        user_data = user_response.json()
        assert user_data["mind_state_id"] is not None


@pytest.mark.asyncio
async def test_user_isolation_mindstate(registered_user, auth_token):
    """Test that users cannot access other users' MindState"""
    # Create another user
    import time
    other_user_data = {
        "email": f"other-user-{int(time.time() * 1000)}@peacescript.com",
        "password": "OtherUserPass123!",
        "display_name": "Other User"
    }
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register other user (MindState auto-created)
        reg_response = await client.post("/api/auth/register", json=other_user_data)
        assert reg_response.status_code == 201
        other_user_id = reg_response.json()["id"]
        
        # Wait a bit for MindState creation
        await asyncio.sleep(0.1)
        
        # Try to access other user's MindState with first user's token
        response = await client.get(
            f"/api/v1/mind-states/{other_user_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should be forbidden (403) not 200
        # If MindState doesn't exist yet, might get 404, both are acceptable here
        assert response.status_code in [403, 404], f"Expected 403 or 404, got {response.status_code}"
        if response.status_code == 403:
            assert "Cannot access other users" in response.text


@pytest.mark.asyncio
async def test_user_can_access_own_mindstate(registered_user, auth_token):
    """Test that users can access their own MindState"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/v1/mind-states/{registered_user['user_id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        mind_state = response.json()
        assert mind_state["user_id"] == registered_user["user_id"]


@pytest.mark.asyncio
async def test_user_can_update_own_mindstate(registered_user, auth_token):
    """Test that users can update their own MindState"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            f"/api/v1/mind-states/{registered_user['user_id']}",
            json={"sila": 7.5, "samadhi": 6.0},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        mind_state = response.json()
        assert mind_state["sila"] == 7.5
        assert mind_state["samadhi"] == 6.0


@pytest.mark.asyncio
async def test_simulation_history_requires_auth():
    """Test that creating simulation history requires authentication"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/simulation-history/",
            json={
                "simulation_id": "test-sim-123",
                "user_id": "fake-user-id",
                "scenario_id": "test-scenario",
                "choice_made": "test-choice",
                "choice_type": "kusala",
                "kamma_generated": 5.0
            }
        )
        
        # Should require authentication
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_simulation_history_user_id_forced(registered_user, auth_token):
    """Test that simulation history user_id is forced from token"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Try to create simulation with different user_id
        import time
        sim_id = f"test-sim-{int(time.time() * 1000)}"
        
        response = await client.post(
            "/api/v1/simulation-history/",
            json={
                "simulation_id": sim_id,
                "user_id": "fake-other-user-id",  # This should be ignored
                "scenario_id": "test-scenario",
                "choice_index": 0,
                "choice_id": "choice_test_001",
                "choice_type": "kusala",
                "choice_label": "Test Choice",
                "citta_generated": "kusala-citta",
                "citta_quality": "sobhana",
                "kamma_generated": 5.0,
                "sati_strength_at_choice": 5.0,
                "state_before": {"sila": 5.0},
                "state_after": {"sila": 6.0},
                "immediate_consequences": ["Immediate test"],
                "short_term_consequences": ["Short term test"],
                "long_term_consequences": ["Long term test"],
                "wisdom_gained": "Test wisdom",
                "practice_tip": "Test tip",
                "anusaya_before": {},
                "anusaya_after": {},
                "anusaya_changes": {}
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # user_id should be forced to authenticated user's ID
        assert data["user_id"] == registered_user["user_id"]
        assert data["user_id"] != "fake-other-user-id"
