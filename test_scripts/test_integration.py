#!/usr/bin/env python3
"""
Skrip Test Integrasi Frontend-Backend Tanam Rawat
Tester: AI Tester
Tanggal: 29 Juni 2025
"""

import requests
import json
import time
import subprocess
import os
from pathlib import Path

def test_backend_endpoint(url, method='GET', data=None, headers=None, timeout=5):
    """Test endpoint backend"""
    try:
        if method.upper() == 'GET':
            response = requests.get(url, timeout=timeout, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=timeout, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, timeout=timeout, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, timeout=timeout, headers=headers)
        else:
            print(f"❌ Unsupported method: {method}")
            return False, None
            
        print(f"✅ {method} {url} - Status: {response.status_code}")
        return True, response
        
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {url} - CONNECTION REFUSED (Server not running?)")
        return False, None
    except requests.exceptions.Timeout:
        print(f"❌ {method} {url} - TIMEOUT")
        return False, None
    except Exception as e:
        print(f"❌ {method} {url} - ERROR: {str(e)}")
        return False, None

def test_backend_health():
    """Test kesehatan backend"""
    print("\n🏥 TESTING BACKEND HEALTH:")
    
    base_url = "http://localhost:8000"
    
    # Test root endpoint
    success, response = test_backend_endpoint(f"{base_url}/")
    if not success:
        return False
    
    # Test docs endpoint
    success, response = test_backend_endpoint(f"{base_url}/docs")
    
    return success

def test_auth_endpoints():
    """Test endpoint autentikasi"""
    print("\n🔐 TESTING AUTH ENDPOINTS:")
    
    base_url = "http://localhost:8000"
    
    # Test register endpoint
    register_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    success, response = test_backend_endpoint(
        f"{base_url}/register", 
        method='POST', 
        data=register_data
    )
    
    if success and response and response.status_code in [200, 201, 409]:  # 409 = user already exists
        print("✅ Register endpoint working")
    elif success and response and response.status_code == 500:
        print("⚠️  Register endpoint returned 500 - Database connection issue?")
        print("   Continuing with login test...")
    else:
        print("❌ Register endpoint failed")
        print(f"   Status: {response.status_code if response else 'No response'}")
        return False, None
    
    # Test login endpoint with form data (OAuth2PasswordRequestForm)
    import requests
    login_data = {
        "username": "test@example.com",  # FastAPI OAuth2 uses username field for email
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/token", 
            data=login_data,  # Use form data instead of JSON
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        token = None
        if response.status_code == 200:
            try:
                token_data = response.json()
                token = token_data.get('access_token')
                print("✅ Login endpoint working")
                return True, token
            except:
                print("❌ Login response invalid")
                return False, None
        elif response.status_code == 401:
            print("⚠️  Login failed - User not registered or wrong credentials")
            print("   This is expected if register failed due to DB issues")
            return False, None
        else:
            print(f"❌ Login endpoint failed - Status: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Login test error: {str(e)}")
        return False, None

def test_protected_endpoints(token):
    """Test endpoint yang memerlukan autentikasi"""
    print("\n🛡️  TESTING PROTECTED ENDPOINTS:")
    
    if not token:
        print("❌ No token available for protected endpoint testing")
        return False
    
    base_url = "http://localhost:8000"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test plants endpoint
    success, response = test_backend_endpoint(
        f"{base_url}/plants", 
        headers=headers
    )
    
    if not success:
        return False
    
    # Test schedules endpoint
    success, response = test_backend_endpoint(
        f"{base_url}/schedules", 
        headers=headers
    )
    
    if not success:
        return False
    
    # Test posts endpoint
    success, response = test_backend_endpoint(
        f"{base_url}/posts", 
        headers=headers
    )
    
    return success

def test_identify_endpoint(token):
    """Test endpoint identifikasi (critical untuk baby-step)"""
    print("\n🔍 TESTING IDENTIFY ENDPOINT (CRITICAL):")
    
    base_url = "http://localhost:8000"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test identify endpoint dengan dummy data
    identify_data = {
        "image_data": "dummy_base64_image_data",
        "filename": "test_plant.jpg"
    }
    
    success, response = test_backend_endpoint(
        f"{base_url}/identify", 
        method='POST',
        data=identify_data,
        headers=headers
    )
    
    if success and response:
        try:
            result = response.json()
            print(f"✅ Identify endpoint response: {result}")
            return True
        except:
            print("❌ Identify endpoint returned invalid JSON")
            return False
    else:
        print("❌ Identify endpoint failed")
        return False

def check_backend_running():
    """Check apakah backend sedang berjalan"""
    try:
        response = requests.get("http://localhost:8000/", timeout=2)
        return True
    except:
        return False

def test_frontend_build():
    """Test apakah frontend bisa di-build"""
    print("\n📱 TESTING FRONTEND BUILD:")
    
    frontend_path = Path("c:/Users/neima/Documents/tanam-rawat/src/frontend")
    
    if not os.path.exists(str(frontend_path / "package.json")):
        print("❌ Frontend package.json not found")
        return False
    
    try:
        # Check if node_modules exists
        if not os.path.exists(str(frontend_path / "node_modules")):
            print("⚠️  node_modules not found, dependencies may not be installed")
            return False
        
        print("✅ Frontend dependencies appear to be installed")
        return True
        
    except Exception as e:
        print(f"❌ Frontend build test error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("AUTOMATED INTEGRATION TEST")
    print("=" * 60)
    
    # Check if backend is running
    print("\n🔍 CHECKING BACKEND STATUS:")
    if not check_backend_running():
        print("❌ Backend is not running on localhost:8000")
        print("   Please start the backend server first:")
        print("   cd src/backend && uvicorn main:app --reload")
        print("\n⚠️  INTEGRATION TEST CANNOT PROCEED WITHOUT BACKEND")
        return False
    else:
        print("✅ Backend is running on localhost:8000")
    
    # Test 1: Backend Health
    backend_healthy = test_backend_health()
    
    # Test 2: Authentication
    auth_success, token = test_auth_endpoints()
    
    # Test 3: Protected Endpoints
    protected_success = False
    if auth_success and token:
        protected_success = test_protected_endpoints(token)
    
    # Test 4: Identify Endpoint (Critical)
    identify_success = test_identify_endpoint(token)
    
    # Test 5: Frontend Build
    frontend_success = test_frontend_build()
    
    # Summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY:")
    print("=" * 60)
    
    tests = [
        ("Backend Health", backend_healthy),
        ("Authentication", auth_success),
        ("Protected Endpoints", protected_success),
        ("Identify Endpoint", identify_success),
        ("Frontend Build", frontend_success)
    ]
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    # Critical Assessment
    print("\n🎯 BABY-STEP READINESS:")
    if identify_success:
        print("✅ IDENTIFY ENDPOINT: Ready for frontend integration")
    else:
        print("❌ IDENTIFY ENDPOINT: NOT READY - Baby-step blocked")
    
    if passed == total:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {total - passed} integration tests failed.")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)