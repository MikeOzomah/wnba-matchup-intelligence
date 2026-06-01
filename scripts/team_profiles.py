import pandas as pd

# Load advanced metrics dataset
df = pd.read_csv("../outputs/advanced_wnba_metrics.csv")

# Group by team and calculate average profile metrics
team_profiles = df.groupby("team")[[
    "pts",
    "possessions",
    "offensive_rating",
    "effective_fg_pct",
    "turnover_pct",
    "assist_turnover_ratio",
    "free_throw_rate",
    "three_point_rate",
    "ball_security",
    "shot_value",
    "offensive_flow"
]].mean().round(3)

# Sort by offensive rating
team_profiles = team_profiles.sort_values(
    by="offensive_rating",
    ascending=False
)

print("\nWNBA TEAM PROFILES\n")

for team, row in team_profiles.iterrows():

    # Skip teams with no real data yet
    if pd.isna(row["offensive_rating"]):
        continue

    print(f"{team}")
    print("-" * 40)
    print(f"Points: {row['pts']}")
    print(f"Possessions: {row['possessions']}")
    print(f"Offensive Rating: {row['offensive_rating']}")
    print(f"Shot Value: {row['shot_value']}")
    print(f"Offensive Flow: {row['offensive_flow']}")
    print(f"Ball Security: {row['ball_security']}")
    print()

    # Offensive rating description
    if row["offensive_rating"] >= 115:
        print("Elite offensive efficiency")
    elif row["offensive_rating"] >= 105:
        print("Strong offensive production")
    elif row["offensive_rating"] >= 95:
        print("Average offensive production")
    else:
        print("Offense still developing")

    # Pace description
    if row["possessions"] >= 90:
        print("Fast-paced tempo profile")
    elif row["possessions"] >= 82:
        print("Balanced tempo profile")
    else:
        print("Slower half-court profile")

    # Shot value description
    if row["shot_value"] >= 0.75:
        print("Strong shot value")
    elif row["shot_value"] >= 0.55:
        print("Average shot value")
    else:
        print("Low shot value")

    # Offensive flow description
    if row["offensive_flow"] >= 0.65:
        print("High offensive flow")
    elif row["offensive_flow"] >= 0.55:
        print("Moderate offensive flow")
    else:
        print("Low offensive flow")

    # Ball security description
    if row["ball_security"] >= 0.86:
        print("Strong ball security")
    elif row["ball_security"] >= 0.80:
        print("Average ball security")
    else:
        print("Below-average ball security")

    print("\n")

# Save numeric team profiles
team_profiles.to_csv("../outputs/team_profiles.csv")

print("Team profiles saved successfully.")