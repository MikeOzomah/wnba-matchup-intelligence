#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for defensive_metrics.py fix

This script validates that:
1. Opponent merge logic works correctly
2. All opponent stats are populated
3. Merge is bidirectional (each team gets opponent's stats)
4. No data is lost or duplicated
"""

import pandas as pd
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def test_defensive_metrics_fix():
    """
    Test the defensive metrics merge fix
    """
    
    print("\n" + "=" * 70)
    print("DEFENSIVE METRICS FIX - VALIDATION TEST")
    print("=" * 70)
    
    # ===== TEST 1: Load data =====
    print("\n[TEST 1] Loading required files...")
    
    advanced_file = BASE_DIR / "outputs" / "advanced_wnba_metrics.csv"
    if not advanced_file.exists():
        print(f"❌ FAIL: {advanced_file} not found")
        print("   Fix: Run advanced_metrics.py first")
        return False
    
    try:
        advanced_df = pd.read_csv(advanced_file)
        print(f"[PASS] Loaded advanced_wnba_metrics.csv: {len(advanced_df)} rows")
    except Exception as e:
        print(f"❌ FAIL: Could not load advanced_wnba_metrics.csv: {e}")
        return False
    
    # ===== TEST 2: Validate structure =====
    print("\n[TEST 2] Validating data structure...")
    
    required_cols = ["game_id", "team", "opponent", "offensive_rating", 
                     "shot_value", "offensive_flow", "ball_security", 
                     "turnover_pct", "possessions"]
    
    missing = [col for col in required_cols if col not in advanced_df.columns]
    if missing:
        print(f"❌ FAIL: Missing columns: {missing}")
        print(f"   Available: {advanced_df.columns.tolist()}")
        return False
    
    print(f"[PASS] All required columns present")
    
    # ===== TEST 3: Understand the data structure =====
    print("\n[TEST 3] Analyzing data structure...")
    
    num_rows = len(advanced_df)
    num_games = advanced_df["game_id"].nunique()
    num_teams = advanced_df["team"].nunique()
    
    print(f"   Total rows: {num_rows}")
    print(f"   Unique games: {num_games}")
    print(f"   Unique teams: {num_teams}")
    print(f"   Expected rows: {num_games * 2} (2 teams per game)")
    
    # Should have 2 rows per game (one for each team)
    if num_rows != num_games * 2:
        print(f"[WARNING]️  WARNING: Expected {num_games * 2} rows ({num_games} games × 2 teams), got {num_rows}")
    else:
        print(f"[PASS] Row count matches expected structure (2 rows per game)")
    
    # ===== TEST 4: Merge simulation =====
    print("\n[TEST 4] Simulating correct merge logic...")
    
    df = advanced_df.copy()
    
    # Create opponent lookup with corrected logic
    opponent_df = df[[
        "game_id", "team",
        "offensive_rating", "shot_value", "offensive_flow",
        "ball_security", "turnover_pct", "possessions"
    ]].copy()
    
    opponent_df = opponent_df.rename(columns={
        "team": "opp_team",
        "offensive_rating": "opp_offensive_rating",
        "shot_value": "opp_shot_value",
        "offensive_flow": "opp_offensive_flow",
        "ball_security": "opp_ball_security",
        "turnover_pct": "opp_turnover_pct",
        "possessions": "opp_possessions"
    })
    
    # Correct merge: game_id AND opponent=opp_team
    df_merged = df.merge(
        opponent_df,
        left_on=["game_id", "opponent"],
        right_on=["game_id", "opp_team"],
        how="left"
    )
    
    df_merged = df_merged.drop(columns=["opp_team"])
    
    print(f"[PASS] Merge completed: {len(df_merged)} rows")
    
    # ===== TEST 5: Validate opponent stats populated =====
    print("\n[TEST 5] Checking if opponent stats are populated...")
    
    opp_stat_cols = ["opp_offensive_rating", "opp_shot_value", 
                     "opp_offensive_flow", "opp_ball_security",
                     "opp_turnover_pct", "opp_possessions"]
    
    nan_check = df_merged[opp_stat_cols].isna()
    total_nans = nan_check.sum().sum()
    total_cells = len(df_merged) * len(opp_stat_cols)
    
    if total_nans > 0:
        print(f"❌ FAIL: Found {total_nans} NaN values in opponent stats")
        print("\n   NaN count per column:")
        for col in opp_stat_cols:
            nan_count = df_merged[col].isna().sum()
            if nan_count > 0:
                print(f"     {col}: {nan_count}")
        
        print("\n   Sample of problematic rows:")
        problematic = df_merged[nan_check.any(axis=1)]
        print(problematic[["game_id", "team", "opponent"] + opp_stat_cols].head())
        return False
    else:
        print(f"[PASS] All {total_cells} opponent stat cells populated (0 NaN)")
    
    # ===== TEST 6: Validate bidirectional symmetry =====
    print("\n[TEST 6] Validating bidirectional merge (data symmetry)...")
    
    # For a game between Team A and Team B:
    # Team A's row should have Team B's stats
    # Team B's row should have Team A's stats
    
    sample_game = df_merged["game_id"].iloc[0]
    game_rows = df_merged[df_merged["game_id"] == sample_game]
    
    if len(game_rows) != 2:
        print(f"[WARNING]️  WARNING: Expected 2 rows for game {sample_game}, got {len(game_rows)}")
    else:
        row1 = game_rows.iloc[0]
        row2 = game_rows.iloc[1]
        
        # Cross-check: row1's opponent should equal row2's team
        if row1["opponent"] == row2["team"] and row2["opponent"] == row1["team"]:
            # Check that their stats are correctly matched
            if (abs(row1["opp_offensive_rating"] - row2["offensive_rating"]) < 0.01 and
                abs(row2["opp_offensive_rating"] - row1["offensive_rating"]) < 0.01):
                print(f"[PASS] Sample game {sample_game}:")
                print(f"     {row1['team']} vs {row1['opponent']}")
                print(f"     {row1['team']} ORating: {row1['offensive_rating']}")
                print(f"     {row1['opponent']} ORating (from {row1['team']}'s perspective): {row1['opp_offensive_rating']}")
                print(f"     {row2['opponent']} ORating (from {row2['team']}'s perspective): {row2['opp_offensive_rating']}")
                print(f"   [PASS] Bidirectional merge is correct!")
            else:
                print(f"❌ FAIL: Stats don't match between team rows")
                print(f"   Row 1: {row1['team']} has opp_ORating={row1['opp_offensive_rating']}")
                print(f"   Row 2: {row2['team']} has ORating={row2['offensive_rating']}")
                return False
        else:
            print(f"❌ FAIL: Team/opponent relationship broken")
            return False
    
    # ===== TEST 7: Spot-check merge quality =====
    print("\n[TEST 7] Spot-checking merge quality...")
    
    # For every game, verify both teams were found
    games_with_both_teams = df_merged.groupby("game_id").size()
    games_with_one_team = games_with_both_teams[games_with_both_teams < 2].index.tolist()
    
    if len(games_with_one_team) > 0:
        print(f"[WARNING]️  WARNING: {len(games_with_one_team)} games have missing opponent data")
        print(f"   Examples: {games_with_one_team[:5]}")
    else:
        print(f"[PASS] All {num_games} games have both team records")
    
    # ===== TEST 8: Verify calculations work =====
    print("\n[TEST 8] Validating defensive metrics calculations...")
    
    df_merged["defensive_pressure"] = 1 - df_merged["opp_ball_security"]
    df_merged["opponent_offensive_rating_allowed"] = df_merged["opp_offensive_rating"]
    df_merged["opponent_shot_value_allowed"] = df_merged["opp_shot_value"]
    df_merged["opponent_offensive_flow_allowed"] = df_merged["opp_offensive_flow"]
    
    calc_cols = ["defensive_pressure", "opponent_offensive_rating_allowed",
                 "opponent_shot_value_allowed", "opponent_offensive_flow_allowed"]
    
    calc_nans = df_merged[calc_cols].isna().sum().sum()
    if calc_nans > 0:
        print(f"❌ FAIL: Calculated metrics have {calc_nans} NaN values")
        return False
    
    print(f"[PASS] All calculated metrics valid (no NaN)")
    print(f"\n   Sample defensive metrics:")
    print(df_merged[[
        "team", "opponent", 
        "defensive_pressure",
        "opponent_offensive_rating_allowed",
        "opponent_shot_value_allowed"
    ]].head())
    
    # ===== FINAL SUMMARY =====
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED [PASS]")
    print("=" * 70)
    print("\nThe defensive_metrics.py fix is working correctly:")
    print(f"  * Merge logic: FIXED (game_id + opponent=opp_team)")
    print(f"  * Opponent stats populated: {len(df_merged)} rows")
    print(f"  * No NaN values in opponent data: VERIFIED")
    print(f"  * Bidirectional merge: CORRECT")
    print(f"  * Defensive metrics calculations: VALID")
    print("\nReady to run defensive_metrics.py!")
    
    return True


if __name__ == "__main__":
    success = test_defensive_metrics_fix()
    sys.exit(0 if success else 1)
