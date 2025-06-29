#!/usr/bin/env python3
"""
Skrip Test Otomatis untuk Frontend Tanam Rawat
Tester: AI Tester
Tanggal: 29 Juni 2025
"""

import os
import json
from pathlib import Path

def test_file_exists(file_path, description):
    """Test apakah file ada"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - FILE NOT FOUND")
        return False

def test_package_json_dependencies(file_path, required_deps):
    """Test dependencies dalam package.json"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
            
        dependencies = package_data.get('dependencies', {})
        dev_dependencies = package_data.get('devDependencies', {})
        all_deps = {**dependencies, **dev_dependencies}
        
        results = []
        for dep in required_deps:
            if dep in all_deps:
                print(f"✅ Dependency: {dep} found in package.json")
                results.append(True)
            else:
                print(f"❌ Dependency: {dep} NOT found in package.json")
                results.append(False)
        
        return results
    except Exception as e:
        print(f"❌ Package.json Test Error: {str(e)}")
        return [False] * len(required_deps)

def test_screen_component_exists(file_path, screen_name):
    """Test apakah screen component ada dan memiliki export default"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for React component patterns
        has_react_import = 'import React' in content or 'from "react"' in content
        has_export_default = 'export default' in content
        has_component_name = screen_name.replace('.tsx', '') in content
        
        if has_react_import and has_export_default and has_component_name:
            print(f"✅ Screen Component: {screen_name} - Valid React component")
            return True
        else:
            print(f"❌ Screen Component: {screen_name} - Invalid or incomplete component")
            return False
            
    except Exception as e:
        print(f"❌ Screen Component Test Error for {screen_name}: {str(e)}")
        return False

def test_navigation_setup(app_tsx_path):
    """Test apakah navigation setup ada di App.tsx"""
    try:
        with open(app_tsx_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        navigation_indicators = [
            '@react-navigation/native',
            'NavigationContainer',
            'createNativeStackNavigator',
            'Stack.Navigator',
            'Stack.Screen'
        ]
        
        results = []
        for indicator in navigation_indicators:
            if indicator in content:
                print(f"✅ Navigation: {indicator} found in App.tsx")
                results.append(True)
            else:
                print(f"❌ Navigation: {indicator} NOT found in App.tsx")
                results.append(False)
        
        return results
        
    except Exception as e:
        print(f"❌ Navigation Test Error: {str(e)}")
        return [False] * 5

def test_identify_feature_exists(base_path):
    """Test apakah fitur identifikasi ada"""
    print("\n🔍 TESTING IDENTIFY FEATURE:")
    
    # Check for IdentifyScreen
    identify_screen_path = base_path / "screens" / "IdentifyScreen.tsx"
    identify_screen_exists = test_file_exists(str(identify_screen_path), "IdentifyScreen Component")
    
    # Check for identify button in other screens
    screens_to_check = [
        base_path / "App.tsx",
        base_path / "screens" / "PlantListScreen.tsx"
    ]
    
    identify_button_found = False
    for screen_path in screens_to_check:
        if os.path.exists(str(screen_path)):
            try:
                with open(str(screen_path), 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if 'identifikasi' in content or 'identify' in content:
                        print(f"✅ Identify Feature: Found identify-related code in {screen_path.name}")
                        identify_button_found = True
                        break
            except Exception as e:
                print(f"❌ Error checking {screen_path.name}: {str(e)}")
    
    if not identify_button_found:
        print("❌ Identify Feature: No identify button or feature found in any screen")
    
    return identify_screen_exists, identify_button_found

def main():
    print("=" * 60)
    print("AUTOMATED FRONTEND STRUCTURE TEST")
    print("=" * 60)
    
    # Base path
    base_path = Path("c:/Users/neima/Documents/tanam-rawat/src/frontend")
    
    # Test 1: Core Files
    print("\n📁 TESTING CORE FILES:")
    core_files = [
        (base_path / "App.tsx", "Main App Component"),
        (base_path / "package.json", "Package Configuration"),
        (base_path / "index.js", "Entry Point"),
        (base_path / "tsconfig.json", "TypeScript Configuration")
    ]
    
    core_results = []
    for file_path, description in core_files:
        result = test_file_exists(str(file_path), description)
        core_results.append(result)
    
    # Test 2: Screen Components
    print("\n📱 TESTING SCREEN COMPONENTS:")
    screens_dir = base_path / "screens"
    expected_screens = [
        "AuthScreen.tsx",
        "PlantListScreen.tsx",
        "PlantDetailScreen.tsx",
        "ScheduleListScreen.tsx",
        "ScheduleDetailScreen.tsx",
        "PestDiseaseListScreen.tsx",
        "PestDiseaseDetailScreen.tsx",
        "PostListScreen.tsx",
        "PostDetailScreen.tsx",
        "PostCreateScreen.tsx"
    ]
    
    screen_results = []
    for screen in expected_screens:
        screen_path = screens_dir / screen
        if test_file_exists(str(screen_path), f"Screen: {screen}"):
            result = test_screen_component_exists(str(screen_path), screen)
            screen_results.append(result)
        else:
            screen_results.append(False)
    
    # Test 3: Dependencies
    print("\n📦 TESTING DEPENDENCIES:")
    package_json_path = str(base_path / "package.json")
    required_deps = [
        "react",
        "react-native",
        "@react-navigation/native",
        "@react-navigation/native-stack",
        "typescript"
    ]
    
    dep_results = []
    if os.path.exists(package_json_path):
        dep_results = test_package_json_dependencies(package_json_path, required_deps)
    
    # Test 4: Navigation Setup
    print("\n🧭 TESTING NAVIGATION SETUP:")
    app_tsx_path = str(base_path / "App.tsx")
    nav_results = []
    if os.path.exists(app_tsx_path):
        nav_results = test_navigation_setup(app_tsx_path)
    
    # Test 5: Identify Feature (Critical for current baby-step)
    identify_screen_exists, identify_button_found = test_identify_feature_exists(base_path)
    identify_results = [identify_screen_exists, identify_button_found]
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print("=" * 60)
    
    all_results = core_results + screen_results + dep_results + nav_results + identify_results
    total_tests = len(all_results)
    passed_tests = sum(all_results)
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Critical Assessment for Baby-Step
    print("\n🎯 BABY-STEP ASSESSMENT:")
    if identify_screen_exists and identify_button_found:
        print("✅ IDENTIFY FEATURE: Ready for testing")
    elif identify_screen_exists or identify_button_found:
        print("⚠️  IDENTIFY FEATURE: Partially implemented")
    else:
        print("❌ IDENTIFY FEATURE: NOT IMPLEMENTED - Baby-step cannot proceed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Frontend structure is complete.")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Frontend needs attention.")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)