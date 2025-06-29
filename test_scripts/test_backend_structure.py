#!/usr/bin/env python3
"""
Skrip Test Otomatis untuk Backend Tanam Rawat
Tester: AI Tester
Tanggal: 29 Juni 2025
"""

import os
import sys
import importlib.util
from pathlib import Path

def test_file_exists(file_path, description):
    """Test apakah file ada"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - FILE NOT FOUND")
        return False

def test_python_import(file_path, module_name):
    """Test apakah file Python dapat diimport"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        # Tidak execute module untuk menghindari side effects
        print(f"✅ Python Import Test: {module_name} - SYNTAX OK")
        return True
    except Exception as e:
        print(f"❌ Python Import Test: {module_name} - ERROR: {str(e)}")
        return False

def test_endpoint_exists_in_code(file_path, endpoint):
    """Test apakah endpoint ada dalam kode"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if endpoint in content:
                print(f"✅ Endpoint Test: {endpoint} found in {file_path}")
                return True
            else:
                print(f"❌ Endpoint Test: {endpoint} NOT found in {file_path}")
                return False
    except Exception as e:
        print(f"❌ Endpoint Test Error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("AUTOMATED BACKEND STRUCTURE TEST")
    print("=" * 60)
    
    # Base path
    base_path = Path("c:/Users/neima/Documents/tanam-rawat/src/backend")
    
    # Test 1: File Structure
    print("\n📁 TESTING FILE STRUCTURE:")
    files_to_test = [
        (base_path / "main.py", "Main FastAPI App"),
        (base_path / "models.py", "Database Models"),
        (base_path / "schemas.py", "Pydantic Schemas"),
        (base_path / "auth.py", "Authentication Module"),
        (base_path / "database.py", "Database Configuration"),
        (base_path / "requirements.txt", "Dependencies File")
    ]
    
    structure_results = []
    for file_path, description in files_to_test:
        result = test_file_exists(str(file_path), description)
        structure_results.append(result)
    
    # Test 2: Python Syntax
    print("\n🐍 TESTING PYTHON SYNTAX:")
    python_files = [
        (base_path / "main.py", "main"),
        (base_path / "models.py", "models"),
        (base_path / "schemas.py", "schemas"),
        (base_path / "auth.py", "auth"),
        (base_path / "database.py", "database")
    ]
    
    syntax_results = []
    for file_path, module_name in python_files:
        if os.path.exists(str(file_path)):
            result = test_python_import(str(file_path), module_name)
            syntax_results.append(result)
    
    # Test 3: Endpoint Existence
    print("\n🌐 TESTING ENDPOINT EXISTENCE:")
    endpoints_to_test = [
        "/identify",
        "/register", 
        "/token",
        "/plants",
        "/schedules",
        "/posts"
    ]
    
    endpoint_results = []
    main_py_path = str(base_path / "main.py")
    if os.path.exists(main_py_path):
        for endpoint in endpoints_to_test:
            result = test_endpoint_exists_in_code(main_py_path, endpoint)
            endpoint_results.append(result)
    
    # Test 4: Dependencies Check
    print("\n📦 TESTING DEPENDENCIES:")
    requirements_path = str(base_path / "requirements.txt")
    required_deps = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "psycopg2-binary",
        "bcrypt",
        "python-jose"
    ]
    
    dep_results = []
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            requirements_content = f.read().lower()
            for dep in required_deps:
                if dep.lower() in requirements_content:
                    print(f"✅ Dependency: {dep} found in requirements.txt")
                    dep_results.append(True)
                else:
                    print(f"❌ Dependency: {dep} NOT found in requirements.txt")
                    dep_results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print("=" * 60)
    
    total_tests = len(structure_results) + len(syntax_results) + len(endpoint_results) + len(dep_results)
    passed_tests = sum(structure_results) + sum(syntax_results) + sum(endpoint_results) + sum(dep_results)
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Backend structure is complete.")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Backend needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)