"""
Locust Load Testing Configuration for DMM Backend.

Run with:
    locust -f locustfile.py --host=http://127.0.0.1:8000

Or web UI:
    locust -f locustfile.py --host=http://127.0.0.1:8000 --web-host=127.0.0.1
"""

from locust import HttpUser, task, between, events
import json
import random


class DMMUser(HttpUser):
    """
    Simulates a typical DMM Backend user.
    
    The user will:
    1. Access the root endpoint
    2. Check health status
    3. Make authenticated requests (if token available)
    """
    
    # Wait between 1-3 seconds between tasks
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts."""
        self.token = None
        self.user_id = None
    
    @task(10)
    def health_check(self):
        """Check API health - most common operation."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(8)
    def root_endpoint(self):
        """Access root endpoint."""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Root endpoint failed: {response.status_code}")
    
    @task(5)
    def api_docs(self):
        """Access API documentation."""
        with self.client.get("/docs", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"API docs failed: {response.status_code}")
    
    @task(3)
    def openapi_schema(self):
        """Access OpenAPI schema."""
        with self.client.get("/openapi.json", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"OpenAPI schema failed: {response.status_code}")


class AuthenticatedDMMUser(HttpUser):
    """
    Simulates an authenticated user making various API calls.
    """
    
    wait_time = between(1, 5)
    
    def on_start(self):
        """Login and get token."""
        self.token = None
        self.headers = {}
        
        # Try to register/login
        # Note: In real load test, you'd have test users
        test_email = f"loadtest_{random.randint(1000, 9999)}@example.com"
        test_password = "LoadTest123!@#"
        
        # Attempt registration (may fail if user exists)
        register_data = {
            "email": test_email,
            "password": test_password,
            "full_name": "Load Test User"
        }
        
        try:
            self.client.post("/api/auth/register", json=register_data)
        except:
            pass  # User may already exist
        
        # Login
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        try:
            with self.client.post("/api/auth/login", json=login_data) as response:
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get("access_token")
                    if self.token:
                        self.headers = {"Authorization": f"Bearer {self.token}"}
        except:
            pass  # Login failed, will use unauthenticated requests
    
    @task(5)
    def get_user_profile(self):
        """Get current user profile."""
        if not self.token:
            return
        
        with self.client.get("/api/auth/me", headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Unauthorized - token may have expired")
            else:
                response.failure(f"Profile fetch failed: {response.status_code}")
    
    @task(3)
    def list_characters(self):
        """List user's characters."""
        if not self.token:
            return
        
        with self.client.get("/api/actors", headers=self.headers, catch_response=True) as response:
            if response.status_code in [200, 404]:  # 404 if no characters
                response.success()
            else:
                response.failure(f"Character list failed: {response.status_code}")
    
    @task(2)
    def list_scenarios(self):
        """List available scenarios."""
        if not self.token:
            return
        
        with self.client.get("/api/scenarios", headers=self.headers, catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Scenario list failed: {response.status_code}")


class StressTestUser(HttpUser):
    """
    Aggressive user for stress testing.
    Minimal wait time, rapid requests.
    """
    
    wait_time = between(0.1, 0.5)  # Very short wait
    
    @task
    def rapid_health_checks(self):
        """Rapid-fire health checks."""
        self.client.get("/health")
    
    @task
    def rapid_root_access(self):
        """Rapid-fire root endpoint."""
        self.client.get("/")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    print("\n" + "="*60)
    print("DMM Backend Load Test Starting")
    print("="*60)
    print(f"Host: {environment.host}")
    print(f"Users: Will ramp up as configured")
    print("="*60 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops."""
    print("\n" + "="*60)
    print("DMM Backend Load Test Complete")
    print("="*60)
    
    # Print summary stats
    if environment.stats.total:
        print(f"\nTotal Requests: {environment.stats.total.num_requests}")
        print(f"Total Failures: {environment.stats.total.num_failures}")
        print(f"Average Response Time: {environment.stats.total.avg_response_time:.2f}ms")
        print(f"Max Response Time: {environment.stats.total.max_response_time:.2f}ms")
        print(f"Requests/sec: {environment.stats.total.total_rps:.2f}")
        
        if environment.stats.total.num_requests > 0:
            failure_rate = (environment.stats.total.num_failures / environment.stats.total.num_requests) * 100
            print(f"Failure Rate: {failure_rate:.2f}%")
        
        print("="*60 + "\n")


# Performance targets (for documentation)
"""
Performance Targets:
- P95 Response Time: < 200ms
- P99 Response Time: < 500ms
- Error Rate: < 0.1%
- Concurrent Users: 50+ without degradation
- Requests/sec: 100+ sustained

Load Test Scenarios:
1. Light Load: 10 users, 1 req/sec ramp
2. Normal Load: 50 users, 5 req/sec ramp
3. Stress Test: 100+ users, 10 req/sec ramp
4. Spike Test: Sudden jump to 200 users

Run Examples:
    # Light load test
    locust -f locustfile.py --host=http://127.0.0.1:8000 --users 10 --spawn-rate 1 --run-time 1m --headless
    
    # Normal load test
    locust -f locustfile.py --host=http://127.0.0.1:8000 --users 50 --spawn-rate 5 --run-time 5m --headless
    
    # Stress test
    locust -f locustfile.py --host=http://127.0.0.1:8000 --users 100 --spawn-rate 10 --run-time 2m --headless
    
    # Web UI for interactive testing
    locust -f locustfile.py --host=http://127.0.0.1:8000
"""
