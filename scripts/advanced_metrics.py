import pandas as pd

# Load extracted full team stats
df = pd.read_csv("../data/full_wnba_team_stats.csv")

# Split made-attempt columns like "39-66"
df[["fgm", "fga"]] = df["fg"].str.split("-", expand=True)
df[["3pm", "3pa"]] = df["3pt"].str.split("-", expand=True)
df[["ftm", "fta"]] = df["ft"].str.split("-", expand=True)

# Convert numeric columns
numeric_cols = [
    "fgm", "fga", "fg_pct",
    "3pm", "3pa", "3p_pct",
    "ftm", "fta", "ft_pct",
    "oreb", "dreb", "reb",
    "ast", "stl", "blk", "to", "pf", "pts"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Possessions estimate
df["possessions"] = df["fga"] - df["oreb"] + df["to"] + (0.44 * df["fta"])

# Advanced metrics with explicit zero-handling

# 1. Offensive Rating: (PTS / Possessions) * 100
#    If Possessions = 0: return null
df["offensive_rating"] = df.apply(
    lambda row: (row["pts"] / row["possessions"]) * 100 
                if row["possessions"] > 0 else pd.NA,
    axis=1
)

# 2. Effective FG%: (FGM + 0.5*3PM) / FGA
#    If FGA = 0: return null
df["effective_fg_pct"] = df.apply(
    lambda row: (row["fgm"] + (0.5 * row["3pm"])) / row["fga"]
                if row["fga"] > 0 else pd.NA,
    axis=1
)

# 3. Turnover %: TO / Possessions
#    If Possessions = 0: return null
df["turnover_pct"] = df.apply(
    lambda row: row["to"] / row["possessions"]
                if row["possessions"] > 0 else pd.NA,
    axis=1
)

# 4. Assist/Turnover Ratio: AST / TO
#    If TO = 0 and AST > 0: return 999 (exceptional ball handling, capped value)
#    If TO = 0 and AST = 0: return 0 (neither assists nor turnovers)
df["assist_turnover_ratio"] = df.apply(
    lambda row: (999 if row["ast"] > 0 else 0) if row["to"] == 0 
                else row["ast"] / row["to"],
    axis=1
)

# 5. Free Throw Rate: FTA / FGA
#    If FGA = 0: return null
df["free_throw_rate"] = df.apply(
    lambda row: row["fta"] / row["fga"]
                if row["fga"] > 0 else pd.NA,
    axis=1
)

# 6. Three Point Rate: 3PA / FGA
#    If FGA = 0: return null
df["three_point_rate"] = df.apply(
    lambda row: row["3pa"] / row["fga"]
                if row["fga"] > 0 else pd.NA,
    axis=1
)

# Your custom signal metrics

# 7. Ball Security: 1 - Turnover %
#    If Possessions = 0: return null
df["ball_security"] = df.apply(
    lambda row: 1 - row["turnover_pct"]
                if row["possessions"] > 0 else pd.NA,
    axis=1
)

# 8. Shot Value: ((3PM*3) + FTM) / FGA
#    If FGA = 0: return null
df["shot_value"] = df.apply(
    lambda row: ((row["3pm"] * 3) + row["ftm"]) / row["fga"]
                if row["fga"] > 0 else pd.NA,
    axis=1
)

# 9. Offensive Flow: AST / FGM
#    If FGM = 0: return null
df["offensive_flow"] = df.apply(
    lambda row: row["ast"] / row["fgm"]
                if row["fgm"] > 0 else pd.NA,
    axis=1
)

# Track and report records affected by zero denominators
zero_possessions = (df["possessions"] == 0).sum()
zero_fga = (df["fga"] == 0).sum()
zero_fgm = (df["fgm"] == 0).sum()
zero_to = (df["to"] == 0).sum()

if zero_possessions > 0 or zero_fga > 0 or zero_fgm > 0 or zero_to > 0:
    print("\n[DIVISION-BY-ZERO HANDLING REPORT]")
    print(f"  * Records with Possessions=0 (ORating, Turnover%, Ball Sec set to NaN): {zero_possessions}")
    print(f"  * Records with FGA=0 (eFG%, FTRate, 3PRate, ShotVal set to NaN): {zero_fga}")
    print(f"  * Records with FGM=0 (OffFlow set to NaN): {zero_fgm}")
    print(f"  * Records with TO=0 (A/TO handled specially): {zero_to}")
    ast_to0_gt0 = ((df["to"] == 0) & (df["ast"] > 0)).sum()
    print(f"    - AST>0 with TO=0 (set to 999): {ast_to0_gt0} records")
    print("  * All metrics now have explicit handling (no silent NaN from division by zero)")
    print()

# Round for readability
metric_cols = [
    "possessions", "offensive_rating", "effective_fg_pct",
    "turnover_pct", "assist_turnover_ratio",
    "free_throw_rate", "three_point_rate",
    "ball_security", "shot_value", "offensive_flow"
]

df[metric_cols] = df[metric_cols].round(3)

# Save advanced dataset
df.to_csv("../outputs/advanced_wnba_metrics.csv", index=False)

print(df[[
    "game_id", "team", "opponent", "pts",
    "possessions", "offensive_rating",
    "effective_fg_pct", "turnover_pct",
    "ball_security", "shot_value", "offensive_flow"
]].head())

print("\nAdvanced metrics saved successfully.")