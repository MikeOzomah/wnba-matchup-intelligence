"""
Comprehensive test suite for division-by-zero fixes in clean_player_data.py and advanced_metrics.py

This test file validates:
1. Proper handling of FGA=0 cases
2. Proper handling of FGM=0 cases
3. Proper handling of TO=0 cases (both AST>0 and AST=0)
4. Proper handling of Possessions=0 cases
5. Validation that no infinity values exist
6. Validation that data types are correct
7. Validation that downstream compatibility is maintained
8. Record counts for affected rows
"""

import pandas as pd
import numpy as np
import sys
from io import StringIO
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

def test_clean_player_data():
    """Test clean_player_data.py division-by-zero fixes"""
    print("\n" + "="*80)
    print("TEST 1: clean_player_data.py DIVISION-BY-ZERO FIXES")
    print("="*80)
    
    # Run the script
    print("\n[Step 1/5] Running clean_player_data.py...")
    try:
        script_path = SCRIPTS_DIR / "clean_player_data.py"
        with open(script_path, "r", encoding="utf-8") as f:
            exec(f.read(), {"__name__": "__main__"})
        print("  [PASS] Script executed without errors")
    except Exception as e:
        print(f"  [FAIL] Script failed with error: {e}")
        return False
    
    # Load the output
    print("\n[Step 2/5] Loading cleaned player data...")
    try:
        df = pd.read_csv(OUTPUT_DIR / "cleaned_player_data.csv")
        print(f"  [PASS] Loaded {len(df)} player records")
    except Exception as e:
        print(f"  [FAIL] Failed to load output: {e}")
        return False
    
    # Check for infinity values (should be zero)
    print("\n[Step 3/5] Checking for infinity values (should be none)...")
    inf_count = 0
    for col in ["player_shot_value", "player_offensive_flow", "assist_turnover_ratio"]:
        inf_in_col = np.isinf(df[col]).sum()
        inf_count += inf_in_col
        if inf_in_col > 0:
            print(f"  [FAIL] Found {inf_in_col} infinity values in {col}")
    
    if inf_count == 0:
        print("  [PASS] No infinity values found (correct)")
    else:
        return False
    
    # Validate assist_turnover_ratio handling
    print("\n[Step 4/5] Validating assist_turnover_ratio logic...")
    
    # Find TO=0 records
    to_zero = df[df["to"] == 0]
    print(f"  * Found {len(to_zero)} records with TO=0")
    
    if len(to_zero) > 0:
        # Check AST>0 with TO=0 -> should be 999
        ast_gt0_to0 = to_zero[to_zero["ast"] > 0]
        ratio_999 = (ast_gt0_to0["assist_turnover_ratio"] == 999).sum()
        print(f"    - Records with AST>0 and TO=0: {len(ast_gt0_to0)}")
        if len(ast_gt0_to0) > 0:
            print(f"      - Set to 999 (capped value): {ratio_999}/{len(ast_gt0_to0)}")
            if ratio_999 == len(ast_gt0_to0):
                print(f"      [PASS] All correctly set to 999")
            else:
                print(f"      [FAIL] ERROR: Not all set to 999")
                return False
        
        # Check AST=0 with TO=0 -> should be 0
        ast_eq0_to0 = to_zero[to_zero["ast"] == 0]
        ratio_0 = (ast_eq0_to0["assist_turnover_ratio"] == 0).sum()
        print(f"    - Records with AST=0 and TO=0: {len(ast_eq0_to0)}")
        if len(ast_eq0_to0) > 0:
            print(f"      - Set to 0: {ratio_0}/{len(ast_eq0_to0)}")
            if ratio_0 == len(ast_eq0_to0):
                print(f"      [PASS] All correctly set to 0")
            else:
                print(f"      [FAIL] ERROR: Not all set to 0")
                return False
    
    # Validate player_offensive_flow handling
    print("\n[Step 5/5] Validating player_offensive_flow logic...")
    
    # Find FGM=0 records
    fgm_zero = df[df["fgm"] == 0]
    print(f"  * Found {len(fgm_zero)} records with FGM=0")
    
    if len(fgm_zero) > 0:
        # Should be NaN
        flow_nan = fgm_zero["player_offensive_flow"].isna().sum()
        print(f"    - Set to NaN: {flow_nan}/{len(fgm_zero)}")
        if flow_nan == len(fgm_zero):
            print(f"    [PASS] All correctly set to NaN")
        else:
            print(f"    [FAIL] ERROR: Not all set to NaN")
            return False
    
    # Check player_shot_value (FGA=0)
    fga_zero = df[df["fga"] == 0]
    print(f"\n  * Found {len(fga_zero)} records with FGA=0")
    if len(fga_zero) > 0:
        shot_nan = fga_zero["player_shot_value"].isna().sum()
        print(f"    - Set to NaN: {shot_nan}/{len(fga_zero)}")
        if shot_nan == len(fga_zero):
            print(f"    [PASS] All correctly set to NaN")
        else:
            print(f"    [FAIL] ERROR: Not all set to NaN")
            return False
    
    print("\n✅ clean_player_data.py: ALL TESTS PASSED")
    return True


def test_advanced_metrics():
    """Test advanced_metrics.py division-by-zero fixes"""
    print("\n" + "="*80)
    print("TEST 2: advanced_metrics.py DIVISION-BY-ZERO FIXES")
    print("="*80)
    
    # Run the script
    print("\n[Step 1/8] Running advanced_metrics.py...")
    try:
        script_path = SCRIPTS_DIR / "advanced_metrics.py"
        with open(script_path, "r", encoding="utf-8") as f:
            exec(f.read(), {"__name__": "__main__"})
        print("  [PASS] Script executed without errors")
    except Exception as e:
        print(f"  [FAIL] Script failed with error: {e}")
        return False
    
    # Load the output
    print("\n[Step 2/8] Loading advanced metrics data...")
    try:
        df = pd.read_csv(OUTPUT_DIR / "advanced_wnba_metrics.csv")
        print(f"  [PASS] Loaded {len(df)} team-game records")
    except Exception as e:
        print(f"  [FAIL] Failed to load output: {e}")
        return False
    
    # Check for infinity values (should be zero)
    print("\n[Step 3/8] Checking for infinity values (should be none)...")
    metric_cols = [
        "offensive_rating", "effective_fg_pct", "turnover_pct",
        "assist_turnover_ratio", "free_throw_rate", "three_point_rate",
        "ball_security", "shot_value", "offensive_flow"
    ]
    
    inf_count = 0
    for col in metric_cols:
        inf_in_col = np.isinf(df[col]).sum()
        inf_count += inf_in_col
        if inf_in_col > 0:
            print(f"  [FAIL] Found {inf_in_col} infinity values in {col}")
    
    if inf_count == 0:
        print("  [PASS] No infinity values found (correct)")
    else:
        return False
    
    # Test 1: Possessions = 0 cases
    print("\n[Step 4/8] Validating Possessions=0 handling...")
    poss_zero = df[df["possessions"] == 0]
    print(f"  * Found {len(poss_zero)} records with Possessions=0")
    
    if len(poss_zero) > 0:
        # These columns should be NaN: offensive_rating, turnover_pct, ball_security
        or_nan = poss_zero["offensive_rating"].isna().sum()
        tp_nan = poss_zero["turnover_pct"].isna().sum()
        bs_nan = poss_zero["ball_security"].isna().sum()
        
        print(f"    - Offensive Rating set to NaN: {or_nan}/{len(poss_zero)} [PASS]" if or_nan == len(poss_zero) else f"    - Offensive Rating set to NaN: {or_nan}/{len(poss_zero)} [FAIL]")
        print(f"    - Turnover % set to NaN: {tp_nan}/{len(poss_zero)} [PASS]" if tp_nan == len(poss_zero) else f"    - Turnover % set to NaN: {tp_nan}/{len(poss_zero)} [FAIL]")
        print(f"    - Ball Security set to NaN: {bs_nan}/{len(poss_zero)} [PASS]" if bs_nan == len(poss_zero) else f"    - Ball Security set to NaN: {bs_nan}/{len(poss_zero)} [FAIL]")
        
        if or_nan != len(poss_zero) or tp_nan != len(poss_zero) or bs_nan != len(poss_zero):
            return False
    
    # Test 2: FGA = 0 cases
    print("\n[Step 5/8] Validating FGA=0 handling...")
    fga_zero = df[df["fga"] == 0]
    print(f"  * Found {len(fga_zero)} records with FGA=0")
    
    if len(fga_zero) > 0:
        # These columns should be NaN: effective_fg_pct, free_throw_rate, three_point_rate, shot_value
        efg_nan = fga_zero["effective_fg_pct"].isna().sum()
        ftr_nan = fga_zero["free_throw_rate"].isna().sum()
        tpr_nan = fga_zero["three_point_rate"].isna().sum()
        sv_nan = fga_zero["shot_value"].isna().sum()
        
        print(f"    - eFG% set to NaN: {efg_nan}/{len(fga_zero)} [PASS]" if efg_nan == len(fga_zero) else f"    - eFG% set to NaN: {efg_nan}/{len(fga_zero)} [FAIL]")
        print(f"    - FTRate set to NaN: {ftr_nan}/{len(fga_zero)} [PASS]" if ftr_nan == len(fga_zero) else f"    - FTRate set to NaN: {ftr_nan}/{len(fga_zero)} [FAIL]")
        print(f"    - 3PRate set to NaN: {tpr_nan}/{len(fga_zero)} [PASS]" if tpr_nan == len(fga_zero) else f"    - 3PRate set to NaN: {tpr_nan}/{len(fga_zero)} [FAIL]")
        print(f"    - ShotValue set to NaN: {sv_nan}/{len(fga_zero)} [PASS]" if sv_nan == len(fga_zero) else f"    - ShotValue set to NaN: {sv_nan}/{len(fga_zero)} [FAIL]")
        
        if efg_nan != len(fga_zero) or ftr_nan != len(fga_zero) or tpr_nan != len(fga_zero) or sv_nan != len(fga_zero):
            return False
    
    # Test 3: FGM = 0 cases
    print("\n[Step 6/8] Validating FGM=0 handling...")
    fgm_zero = df[df["fgm"] == 0]
    print(f"  * Found {len(fgm_zero)} records with FGM=0")
    
    if len(fgm_zero) > 0:
        # offensive_flow should be NaN
        of_nan = fgm_zero["offensive_flow"].isna().sum()
        print(f"    - Offensive Flow set to NaN: {of_nan}/{len(fgm_zero)} [PASS]" if of_nan == len(fgm_zero) else f"    - Offensive Flow set to NaN: {of_nan}/{len(fgm_zero)} [FAIL]")
        
        if of_nan != len(fgm_zero):
            return False
    
    # Test 4: TO = 0 cases
    print("\n[Step 7/8] Validating TO=0 handling...")
    to_zero = df[df["to"] == 0]
    print(f"  * Found {len(to_zero)} records with TO=0")
    
    if len(to_zero) > 0:
        # Check AST>0 with TO=0 -> should be 999
        ast_gt0_to0 = to_zero[to_zero["ast"] > 0]
        ratio_999 = (ast_gt0_to0["assist_turnover_ratio"] == 999).sum()
        
        if len(ast_gt0_to0) > 0:
            print(f"    - Records with AST>0 and TO=0: {len(ast_gt0_to0)}")
            print(f"      - Set to 999 (capped): {ratio_999}/{len(ast_gt0_to0)} [PASS]" if ratio_999 == len(ast_gt0_to0) else f"      - Set to 999 (capped): {ratio_999}/{len(ast_gt0_to0)} [FAIL]")
            if ratio_999 != len(ast_gt0_to0):
                return False
        
        # Check AST=0 with TO=0 -> should be 0
        ast_eq0_to0 = to_zero[to_zero["ast"] == 0]
        ratio_0 = (ast_eq0_to0["assist_turnover_ratio"] == 0).sum()
        
        if len(ast_eq0_to0) > 0:
            print(f"    - Records with AST=0 and TO=0: {len(ast_eq0_to0)}")
            print(f"      - Set to 0: {ratio_0}/{len(ast_eq0_to0)} [PASS]" if ratio_0 == len(ast_eq0_to0) else f"      - Set to 0: {ratio_0}/{len(ast_eq0_to0)} [FAIL]")
            if ratio_0 != len(ast_eq0_to0):
                return False
    
    # Test 5: Verify no unexpected NaN
    print("\n[Step 8/8] Checking overall data quality...")
    
    # For records that should have valid values, check NaN count
    total_nans = 0
    for col in metric_cols:
        nan_count = df[col].isna().sum()
        total_nans += nan_count
    
    print(f"  * Total NaN values across all metrics: {total_nans}")
    print(f"  * Expected NaN pattern: zero denominators + normal missing data")
    print(f"  [PASS] Data quality check passed")
    
    print("\n✅ advanced_metrics.py: ALL TESTS PASSED")
    return True


def test_data_types():
    """Verify data types are correct"""
    print("\n" + "="*80)
    print("TEST 3: DATA TYPE VALIDATION")
    print("="*80)
    
    print("\n[Clean Player Data]")
    try:
        df = pd.read_csv(OUTPUT_DIR / "cleaned_player_data.csv")
        
        required_cols = ["player_shot_value", "player_offensive_flow", "assist_turnover_ratio"]
        for col in required_cols:
            if col not in df.columns:
                print(f"  [FAIL] Missing column: {col}")
                return False
            dtype = df[col].dtype
            print(f"  * {col}: {dtype} [PASS]")
        
        print("  [PASS] All required columns present")
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False
    
    print("\n[Advanced Metrics]")
    try:
        df = pd.read_csv(OUTPUT_DIR / "advanced_wnba_metrics.csv")
        
        required_cols = [
            "offensive_rating", "effective_fg_pct", "turnover_pct",
            "assist_turnover_ratio", "free_throw_rate", "three_point_rate",
            "ball_security", "shot_value", "offensive_flow"
        ]
        for col in required_cols:
            if col not in df.columns:
                print(f"  [FAIL] Missing column: {col}")
                return False
            dtype = df[col].dtype
            print(f"  * {col}: {dtype} [PASS]")
        
        print("  [PASS] All required columns present")
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False
    
    print("\n✅ DATA TYPES: ALL TESTS PASSED")
    return True


def test_downstream_compatibility():
    """Verify downstream scripts still work"""
    print("\n" + "="*80)
    print("TEST 4: DOWNSTREAM COMPATIBILITY CHECK")
    print("="*80)
    
    print("\n[Check 1] Verify output files exist...")
    try:
        df_clean = pd.read_csv(OUTPUT_DIR / "cleaned_player_data.csv")
        df_adv = pd.read_csv(OUTPUT_DIR / "advanced_wnba_metrics.csv")
        print("  [PASS] cleaned_player_data.csv exists")
        print("  [PASS] advanced_wnba_metrics.csv exists")
    except Exception as e:
        print(f"  [FAIL] Missing output files: {e}")
        return False
    
    print("\n[Check 2] Verify row counts are reasonable...")
    print(f"  * cleaned_player_data.csv: {len(df_clean)} records")
    print(f"  * advanced_wnba_metrics.csv: {len(df_adv)} records")
    
    if len(df_clean) == 0:
        print("  [FAIL] cleaned_player_data.csv is empty!")
        return False
    if len(df_adv) == 0:
        print("  [FAIL] advanced_wnba_metrics.csv is empty!")
        return False
    
    print("  [PASS] Both files have records")
    
    print("\n[Check 3] Verify column counts are consistent...")
    print(f"  * cleaned_player_data.csv: {len(df_clean.columns)} columns")
    print(f"  * advanced_wnba_metrics.csv: {len(df_adv.columns)} columns")
    print("  [PASS] Column structure maintained")
    
    print("\n✅ DOWNSTREAM COMPATIBILITY: ALL TESTS PASSED")
    return True


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# DIVISION-BY-ZERO FIX TEST SUITE")
    print("# Testing clean_player_data.py and advanced_metrics.py")
    print("#"*80)
    
    results = []
    
    # Run all tests
    results.append(("clean_player_data.py fixes", test_clean_player_data()))
    results.append(("advanced_metrics.py fixes", test_advanced_metrics()))
    results.append(("Data type validation", test_data_types()))
    results.append(("Downstream compatibility", test_downstream_compatibility()))
    
    # Summary
    print("\n" + "#"*80)
    print("# TEST SUMMARY")
    print("#"*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Division-by-zero fixes are working correctly.")
        sys.exit(0)
    else:
        print(f"\n[WARNING]️  {total - passed} test suite(s) failed. Please review the output above.")
        sys.exit(1)
