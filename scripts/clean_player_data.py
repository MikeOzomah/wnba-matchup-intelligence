import pandas as pd

# Load raw player box score data
df = pd.read_csv("../data/player_box_scores.csv")

# Standardize column names
df.columns = df.columns.str.lower().str.strip()

# Split made-attempt columns
df[["fgm", "fga"]] = df["fg"].str.split("-", expand=True)
df[["3pm", "3pa"]] = df["3pt"].str.split("-", expand=True)
df[["ftm", "fta"]] = df["ft"].str.split("-", expand=True)

# Convert numeric columns
numeric_cols = [
    "fgm", "fga", "3pm", "3pa", "ftm", "fta",
    "oreb", "dreb", "reb", "ast", "stl", "blk",
    "to", "pf", "pts", "plus_minus"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Calculate player metrics with explicit zero-handling

# 1. Player Shot Value: ((3PM*3) + FTM) / FGA
#    If FGA = 0: return null (player has no field goal attempts)
df["player_shot_value"] = df.apply(
    lambda row: (row["3pm"] * 3 + row["ftm"]) / row["fga"] 
                if row["fga"] > 0 else pd.NA,
    axis=1
)

# 2. Player Offensive Flow: AST / FGM
#    If FGM = 0: return null (player has no field goals made)
#    This indicates a player with no scoring output, so can't measure flow
df["player_offensive_flow"] = df.apply(
    lambda row: row["ast"] / row["fgm"]
                if row["fgm"] > 0 else pd.NA,
    axis=1
)

# 3. Assist/Turnover Ratio: AST / TO
#    If TO = 0 and AST > 0: return 999 (exceptional ball handling, capped value)
#    If TO = 0 and AST = 0: return 0 (neither assists nor turnovers)
#    If TO > 0: return normal ratio
df["assist_turnover_ratio"] = df.apply(
    lambda row: (999 if row["ast"] > 0 else 0) if row["to"] == 0 
                else row["ast"] / row["to"],
    axis=1
)

# Track and report records affected by zero denominators
zero_fga_count = (df["fga"] == 0).sum()
zero_fgm_count = (df["fgm"] == 0).sum()
zero_to_count = (df["to"] == 0).sum()

if zero_fga_count > 0 or zero_fgm_count > 0 or zero_to_count > 0:
    print("\n[DIVISION-BY-ZERO HANDLING REPORT]")
    print(f"  * Records with FGA=0 (shot_value set to NaN): {zero_fga_count}")
    print(f"  * Records with FGM=0 (offensive_flow set to NaN): {zero_fgm_count}")
    print(f"  * Records with TO=0 (A/TO handled specially): {zero_to_count}")
    ast_gt0_to0_count = ((df["to"] == 0) & (df["ast"] > 0)).sum()
    print(f"    - AST>0 with TO=0 (set to 999): {ast_gt0_to0_count} records")
    print("  * All metrics now have explicit handling (no silent NaN from division by zero)")
    print()

# Round metrics
metric_cols = [
    "player_shot_value",
    "player_offensive_flow",
    "assist_turnover_ratio"
]

df[metric_cols] = df[metric_cols].round(3)

# Save cleaned player data
df.to_csv("../outputs/cleaned_player_data.csv", index=False)

print(df.head())
print("\nCleaned player data saved successfully.")