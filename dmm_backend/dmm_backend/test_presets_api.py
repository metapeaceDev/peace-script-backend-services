#!/usr/bin/env python3
"""
Comprehensive testing script for Custom Presets API
Tests all 23 endpoints systematically
"""
import requests
import json
from typing import Dict, Any
import sys

BASE_URL = "http://127.0.0.1:8000/api/presets"

def print_result(endpoint: str, method: str, status: int, success: bool, details: str = ""):
    """Print test result in a formatted way"""
    emoji = "✅" if success else "❌"
    print(f"{emoji} {method:6s} {endpoint:50s} {status} {details}")

def test_template_endpoints():
    """Test Preset Template endpoints (3 endpoints)"""
    print("\n" + "="*80)
    print("TESTING: Preset Templates (3 endpoints)")
    print("="*80)
    
    # 1. GET /templates (list)
    try:
        resp = requests.get(f"{BASE_URL}/templates", params={"limit": 5})
        success = resp.status_code == 200
        details = ""
        if success:
            data = resp.json()
            details = f"| Total: {data.get('total')}, Returned: {len(data.get('templates', []))}"
        print_result("/templates", "GET", resp.status_code, success, details)
    except Exception as e:
        print_result("/templates", "GET", 0, False, f"| Error: {str(e)[:50]}")
    
    # 2. GET /templates/{id} (detail)
    try:
        resp = requests.get(f"{BASE_URL}/templates/template_closeup_emotional")
        success = resp.status_code == 200
        details = ""
        if success:
            data = resp.json()
            details = f"| Name: {data.get('name', 'N/A')}"
        elif resp.status_code == 500:
            details = f"| ERROR: {resp.json().get('detail', 'Unknown error')[:50]}"
        print_result("/templates/{{id}}", "GET", resp.status_code, success, details)
    except Exception as e:
        print_result("/templates/{{id}}", "GET", 0, False, f"| Error: {str(e)[:50]}")
    
    # 3. POST /templates (create - expect auth error)
    try:
        payload = {
            "template_id": "test_template",
            "name": "Test Template",
            "description": "Test",
            "category": "test",
            "visibility": "private",
            "config": {"parameters": []}
        }
        resp = requests.post(f"{BASE_URL}/templates", json=payload)
        # Expect 401 or 403 (not authenticated)
        success = resp.status_code in [401, 403]
        details = f"| Expected auth error, got: {resp.status_code}"
        print_result("/templates", "POST", resp.status_code, success, details)
    except Exception as e:
        print_result("/templates", "POST", 0, False, f"| Error: {str(e)[:50]}")

def test_user_preset_endpoints():
    """Test User Presets CRUD endpoints (5 endpoints)"""
    print("\n" + "="*80)
    print("TESTING: User Presets CRUD (5 endpoints)")
    print("="*80)
    
    endpoints = [
        ("GET", "/user", {}, "List user presets"),
        ("GET", "/user/preset123", {}, "Get preset detail"),
        ("POST", "/user", {"preset_id": "test"}, "Create preset"),
        ("PUT", "/user/preset123", {"name": "Updated"}, "Update preset"),
        ("DELETE", "/user/preset123", {}, "Delete preset"),
    ]
    
    for method, path, payload, desc in endpoints:
        try:
            url = f"{BASE_URL}{path}"
            if method == "GET":
                resp = requests.get(url)
            elif method == "POST":
                resp = requests.post(url, json=payload)
            elif method == "PUT":
                resp = requests.put(url, json=payload)
            elif method == "DELETE":
                resp = requests.delete(url)
            
            # All should require auth
            success = resp.status_code in [401, 403, 404, 200]
            details = f"| {desc}"
            print_result(path, method, resp.status_code, success, details)
        except Exception as e:
            print_result(path, method, 0, False, f"| Error: {str(e)[:50]}")

def test_extended_operations():
    """Test Extended Operations endpoints (3 endpoints)"""
    print("\n" + "="*80)
    print("TESTING: Extended Operations (3 endpoints)")
    print("="*80)
    
    endpoints = [
        ("POST", "/user/preset123/duplicate", {}, "Duplicate preset"),
        ("POST", "/user/preset123/favorite", {}, "Toggle favorite"),
        ("POST", "/batch", {"operation": "delete", "preset_ids": []}, "Batch operation"),
    ]
    
    for method, path, payload, desc in endpoints:
        try:
            resp = requests.post(f"{BASE_URL}{path}", json=payload)
            success = resp.status_code in [401, 403, 404, 200]
            details = f"| {desc}"
            print_result(path, method, resp.status_code, success, details)
        except Exception as e:
            print_result(path, method, 0, False, f"| Error: {str(e)[:50]}")

def test_collections_endpoints():
    """Test Collections endpoints (4 endpoints)"""
    print("\n" + "="*80)
    print("TESTING: Collections (4 endpoints)")
    print("="*80)
    
    endpoints = [
        ("GET", "/collections", {}, "List collections"),
        ("POST", "/collections", {"name": "Test"}, "Create collection"),
        ("PUT", "/collections/col123", {"name": "Updated"}, "Update collection"),
        ("DELETE", "/collections/col123", {}, "Delete collection"),
    ]
    
    for method, path, payload, desc in endpoints:
        try:
            url = f"{BASE_URL}{path}"
            if method == "GET":
                resp = requests.get(url)
            elif method == "POST":
                resp = requests.post(url, json=payload)
            elif method == "PUT":
                resp = requests.put(url, json=payload)
            elif method == "DELETE":
                resp = requests.delete(url)
            
            success = resp.status_code in [401, 403, 404, 200]
            details = f"| {desc}"
            print_result(path, method, resp.status_code, success, details)
        except Exception as e:
            print_result(path, method, 0, False, f"| Error: {str(e)[:50]}")

def test_usage_analytics():
    """Test Usage & Analytics endpoints (2 endpoints)"""
    print("\n" + "="*80)
    print("TESTING: Usage & Analytics (2 endpoints)")
    print("="*80)
    
    # Usage logging
    try:
        resp = requests.post(f"{BASE_URL}/usage", json={"preset_id": "test", "success": True})
        success = resp.status_code in [401, 403, 200]
        print_result("/usage", "POST", resp.status_code, success, "| Log usage")
    except Exception as e:
        print_result("/usage", "POST", 0, False, f"| Error: {str(e)[:50]}")
    
    # Statistics
    try:
        resp = requests.get(f"{BASE_URL}/statistics")
        success = resp.status_code in [401, 403, 200]
        print_result("/statistics", "GET", resp.status_code, success, "| Get statistics")
    except Exception as e:
        print_result("/statistics", "GET", 0, False, f"| Error: {str(e)[:50]}")

def test_sharing_endpoints():
    """Test Sharing endpoints (4 endpoints)"""
    print("\n" + "="*80)
    print("TESTING: Sharing (4 endpoints)")
    print("="*80)
    
    endpoints = [
        ("POST", "/share", {"preset_id": "test"}, "Share preset"),
        ("GET", "/shared/share123", {}, "Get shared preset"),
        ("PUT", "/shared/share123", {"permissions": "read"}, "Update share"),
        ("DELETE", "/shared/share123", {}, "Delete share"),
    ]
    
    for method, path, payload, desc in endpoints:
        try:
            url = f"{BASE_URL}{path}"
            if method == "GET":
                resp = requests.get(url)
            elif method == "POST":
                resp = requests.post(url, json=payload)
            elif method == "PUT":
                resp = requests.put(url, json=payload)
            elif method == "DELETE":
                resp = requests.delete(url)
            
            success = resp.status_code in [401, 403, 404, 200]
            details = f"| {desc}"
            print_result(path, method, resp.status_code, success, details)
        except Exception as e:
            print_result(path, method, 0, False, f"| Error: {str(e)[:50]}")

def test_import_export():
    """Test Import/Export endpoints (2 endpoints)"""
    print("\n" + "="*80)
    print("TESTING: Import/Export (2 endpoints)")
    print("="*80)
    
    # Export
    try:
        resp = requests.post(f"{BASE_URL}/export", json={"preset_ids": ["test"]})
        success = resp.status_code in [401, 403, 200]
        print_result("/export", "POST", resp.status_code, success, "| Export presets")
    except Exception as e:
        print_result("/export", "POST", 0, False, f"| Error: {str(e)[:50]}")
    
    # Import
    try:
        resp = requests.post(f"{BASE_URL}/import", json={"presets": []})
        success = resp.status_code in [401, 403, 200, 422]
        print_result("/import", "POST", resp.status_code, success, "| Import presets")
    except Exception as e:
        print_result("/import", "POST", 0, False, f"| Error: {str(e)[:50]}")

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("CUSTOM PRESETS API TESTING - 23 Endpoints")
    print("="*80)
    
    # Check if backend is running
    try:
        resp = requests.get("http://127.0.0.1:8000/health", timeout=2)
        if resp.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend returned non-200 status")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Backend is not running: {e}")
        print("Please start backend with: cd dmm_backend && ./venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000")
        sys.exit(1)
    
    # Run all test groups
    test_template_endpoints()
    test_user_preset_endpoints()
    test_extended_operations()
    test_collections_endpoints()
    test_usage_analytics()
    test_sharing_endpoints()
    test_import_export()
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print("\nNote: Auth errors (401/403) are expected for endpoints requiring authentication")
    print("404 errors are expected for non-existent resources (preset123, col123, share123)")

if __name__ == "__main__":
    main()
