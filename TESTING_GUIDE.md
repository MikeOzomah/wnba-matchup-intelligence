# Quick Test Guide for Defensive Metrics Fix

## One-Minute Summary

**Problem:** The merge logic was trying to match `df.opponent` with `opponent_df.opponent`, which are unrelated.

**Solution:** Changed to merge on `df.opponent` with `opponent_df.opp_team` (which is the team column).

**Result:** Opponent stats now populate correctly instead of being all NaN.

---

## Step-by-Step Testing

### Step 1: Run Advanced Metrics First
```bash
cd c:\Users\ozoma\PycharmProjects\PythonProject1
python scripts/advanced_metrics.py
```

**Expected:** Creates `outputs/advanced_wnba_metrics.csv`

---

### Step 2: Run Validation Test
```bash
python test_defensive_metrics_fix.py
```

**Expected Output:**
```
======================================================================
DEFENSIVE METRICS FIX - VALIDATION TEST
======================================================================

[TEST 1] Loading required files...
[PASS] Loaded advanced_wnba_metrics.csv: 30 rows

[TEST 2] Validating data structure...
[PASS] All required columns present

[TEST 3] Analyzing data structure...
   Total rows: 30
   Unique games: 15
   Unique teams: 15
   Expected rows: 30 (15 games × 2 teams)
[PASS] Row count matches expected structure (2 rows per game)

[TEST 4] Simulating correct merge logic...
[PASS] Merge completed: 30 rows

[TEST 5] Checking if opponent stats are populated...
[PASS] All 180 opponent stat cells populated (0 NaN)

[TEST 6] Validating bidirectional merge (data symmetry)...
[PASS] Sample game 20260510:
     Seattle Storm vs Connecticut Sun
     Seattle Storm ORating: 102.500
     Connecticut Sun ORating (from Seattle's perspective): 95.200
     Connecticut Sun ORating (from Connecticut's perspective): 102.500
   [PASS] Bidirectional merge is correct!

[TEST 7] Spot-checking merge quality...
[PASS] All 15 games have both team records

[TEST 8] Validating defensive metrics calculations...
[PASS] All calculated metrics valid (no NaN)

   Sample defensive metrics:
           team         opponent  defensive_pressure  opponent_offensive_rating_allowed  opponent_shot_value_allowed
0  Seattle Storm  Connecticut Sun           0.092                            95.200                       0.620
1  Connecticut Sun  Seattle Storm           0.118                           102.500                       0.540
...

======================================================================
ALL TESTS PASSED [PASS]
======================================================================
```

---

### Step 3: Run Fixed Script
```bash
python scripts/defensive_metrics.py
```

**Expected Output:**
```
[PASS] Merge validation passed: All opponent stats populated successfully

============================================================
DEFENSIVE METRICS CALCULATION COMPLETE
============================================================

Sample output (first 5 rows):
       game_id             team         opponent  defensive_pressure  opponent_offensive_rating_allowed  opponent_shot_value_allowed opponent_offensive_flow_allowed
0  20260508  Seattle Storm  Connecticut Sun            0.092                            95.200                       0.620                             0.580
1  20260508  Connecticut Sun  Seattle Storm           0.118                           102.500                       0.540                             0.650
...

Rows processed: 30
Teams in dataset: 15
Games in dataset: 15

Defensive metrics saved to: ../outputs/defensive_metrics.csv
```

---

### Step 4: Verify Output File
```bash
# Check file exists
ls -la outputs/defensive_metrics.csv

# Check row count (should match input)
python -c "import pandas as pd; df=pd.read_csv('outputs/defensive_metrics.csv'); print(f'Rows: {len(df)}, Columns: {len(df.columns)}')"

# Check for NaN in opponent stats
python -c "import pandas as pd; df=pd.read_csv('outputs/defensive_metrics.csv'); cols=['opp_offensive_rating','opp_shot_value','opp_offensive_flow']; print(f'NaN count: {df[cols].isna().sum().sum()}')"
```

**Expected:** No NaN values, same row count as input

---

## Common Issues & Solutions

### Issue: "FileNotFoundError: advanced_wnba_metrics.csv"
**Solution:** Run `python scripts/advanced_metrics.py` first

### Issue: "WARNING: Opponent stats contain NaN values"
**Diagnosis:** The merge didn't work
**Check:**
```python
# In Python terminal
import pandas as pd
df = pd.read_csv('outputs/advanced_wnba_metrics.csv')
print("Unique teams:", df['team'].nunique())
print("Unique opponents:", df['opponent'].nunique())
# Should be equal
print(df[['team', 'opponent']].drop_duplicates())
```

### Issue: Merge produces fewer rows than input
**Check:** 
```python
import pandas as pd
df = pd.read_csv('outputs/advanced_wnba_metrics.csv')
print(f"Input rows: {len(df)}")
# If teams/opponents don't match perfectly, merge might lose rows
```

---

## Verification Checklist

- [ ] `advanced_metrics.py` runs successfully
- [ ] `test_defensive_metrics_fix.py` shows "ALL TESTS PASSED"
- [ ] `defensive_metrics.py` shows "Merge validation passed"
- [ ] `outputs/defensive_metrics.csv` exists
- [ ] `offensive_rating_allowed` columns have no NaN
- [ ] Row count is same as input (30 for test data)
- [ ] Can read output file: `import pandas as pd; pd.read_csv('outputs/defensive_metrics.csv')`

---

## Success Indicators

[PASS] Test passes all 8 validation checks
[PASS] Script runs without errors
[PASS] Output file created with same row count
[PASS] Opponent stats are populated (no NaN)
[PASS] Calculations are valid (defensive_pressure is between 0 and 1)

---

## What's Different from Before

**Before:** Merge joined on two "opponent" columns that didn't relate to each other
**After:** Merge correctly joins on game_id + opponent team name relationship

**Before:** All opponent stats were NaN
**After:** All opponent stats are populated with correct values

**Before:** No validation of merge success
**After:** Comprehensive checks at merge and calculation stages
