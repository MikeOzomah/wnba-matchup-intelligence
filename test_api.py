#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for the WNBA Matchup API
"""
import requests
import json
import time
import subprocess
import sys
import os
from pathlib import Path

# Fix encoding for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add scripts to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

from matchup_api import get_report


def test_direct_function():
    """Test the get_report function directly"""
    print("=" * 70)
    print("TEST 1: Direct Function Call")
    print("=" * 70)
    
    result = get_report("Dallas Wings vs Indiana Fever")
    
    if "error" in result:
        print(f"[ERROR] {result['error']}")
        return False
    
    print(f"[OK] Matchup: {result['matchup']}")
    print(f"[OK] Team Stats: {len(result['team_stats'])} teams")
    print(f"[OK] Insights: {len(result['matchup_insights'])} insights")
    print(f"[OK] Lineups: {len(result['lineups'])} lineups analyzed")
    print()
    
    return True


def test_available_teams():
    """Show available teams"""
    print("=" * 70)
    print("TEST 2: Available Teams")
    print("=" * 70)
    
    result = get_report("InvalidTeam vs AnotherInvalidTeam")
    
    if "available_teams" in result:
        teams = result["available_teams"]
        print(f"[OK] Found {len(teams)} teams:")
        for team in sorted(teams):
            print(f"   - {team}")
    print()


def test_api_endpoint():
    """Test the FastAPI endpoint (requires server running)"""
    print("=" * 70)
    print("TEST 3: FastAPI Endpoint")
    print("=" * 70)
    print("(Note: Server must be running on http://localhost:8000)")
    print()
    
    try:
        # Test with URL-encoded team names
        url = "http://localhost:8000/report/Dallas%20Wings_vs_Indiana%20Fever"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] API Status: {response.status_code}")
            print(f"[OK] Matchup: {data['matchup']}")
            print(f"[OK] Response keys: {list(data.keys())}")
        else:
            print(f"[ERROR] API returned status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("[WARN] Could not connect to API on http://localhost:8000")
        print("   Start the server with: uvicorn fastapi_app:app --port 8000")
    except Exception as e:
        print(f"[ERROR] Error testing API: {e}")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("WNBA MATCHUP API - TEST SUITE")
    print("=" * 70 + "\n")
    
    # Test 1: Direct function
    success1 = test_direct_function()
    
    # Test 2: Available teams
    test_available_teams()
    
    # Test 3: API endpoint
    test_api_endpoint()
    
    print("=" * 70)
    print("Tests complete!")
    print("=" * 70)
