import pandas as pd
import sys

# Load advanced metrics dataset
try:
    df = pd.read_csv("../outputs/advanced_wnba_metrics.csv")
except FileNotFoundError:
    print("ERROR: Could not find ../outputs/advanced_wnba_metrics.csv")
    print("Please run advanced_metrics.py first.")
    sys.exit(1)

# Validate required columns exist
required_columns = [
    "game_id", "team", "opponent",
    "offensive_rating", "shot_value", "offensive_flow",
    "ball_security", "turnover_pct", "possessions"
]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    print(f"ERROR: Missing required columns in advanced_wnba_metrics.csv: {missing_columns}")
    print(f"Available columns: {df.columns.tolist()}")
    sys.exit(1)

# Create opponent metrics lookup
# This contains each team's stats, labeled by their opponent reference point
opponent_df = df[[
    "game_id",
    "team",
    "offensive_rating",
    "shot_value",
    "offensive_flow",
    "ball_security",
    "turnover_pct",
    "possessions"
]].copy()

# Rename columns: team becomes opp_team (for merge key), stats become opp_*
opponent_df = opponent_df.rename(columns={
    "team": "opp_team",  # Temporary name for merge
    "offensive_rating": "opp_offensive_rating",
    "shot_value": "opp_shot_value",
    "offensive_flow": "opp_offensive_flow",
    "ball_security": "opp_ball_security",
    "turnover_pct": "opp_turnover_pct",
    "possessions": "opp_possessions"
})

# CRITICAL FIX: Merge on game_id AND opponent=opp_team
# This correctly matches each team's row with their opponent's stats from the same game
# Example:
#   df row: game_id=20260510, team=Dallas, opponent=Indiana
#   opponent_df row: game_id=20260510, opp_team=Indiana, opp_offensive_rating=104.0
#   Match on: game_id AND (df.opponent = opponent_df.opp_team)
df = df.merge(
    opponent_df,
    left_on=["game_id", "opponent"],
    right_on=["game_id", "opp_team"],
    how="left"
)

# Remove the temporary opp_team column (we already have opponent)
df = df.drop(columns=["opp_team"])

# Validate merge succeeded (opponent stats should not be NaN)
nan_counts = df[["opp_offensive_rating", "opp_shot_value", "opp_offensive_flow", 
                  "opp_ball_security", "opp_turnover_pct", "opp_possessions"]].isna().sum()

if nan_counts.sum() > 0:
    print("WARNING: Opponent stats contain NaN values after merge:")
    print(nan_counts[nan_counts > 0])
    print(f"\nTotal rows with ANY missing opponent data: {df[['opp_offensive_rating', 'opp_shot_value', 'opp_offensive_flow', 'opp_ball_security', 'opp_turnover_pct', 'opp_possessions']].isna().any(axis=1).sum()} / {len(df)}")

    problematic = df[df[["opp_offensive_rating", "opp_shot_value"]].isna().any(axis=1)]
    if len(problematic) > 0:
        print("\nSample of rows with missing opponent data:")
        print(problematic[["game_id", "team", "opponent", "opp_offensive_rating", "opp_shot_value"]].head())

    # ADD THIS BLOCK
    before = len(df)

    df = df.dropna(
        subset=[
            "opp_offensive_rating",
            "opp_shot_value",
            "opp_offensive_flow",
            "opp_ball_security",
            "opp_turnover_pct",
            "opp_possessions"
        ]
    ).copy()

    after = len(df)

    print(f"\nDropped {before - after} rows with incomplete opponent data.")

else:
    print("[PASS] Merge validation passed: All opponent stats populated successfully")

# ============================================================
# DEFENSIVE METRICS CALCULATION
# ============================================================