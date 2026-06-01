import pandas as pd

# Load cleaned player data
df = pd.read_csv("../outputs/cleaned_player_data.csv")

# Group by player and calculate averages
player_profiles = df.groupby("player")[[
    "pts",
    "reb",
    "ast",
    "stl",
    "blk",
    "to",
    "player_shot_value",
    "player_offensive_flow",
    "assist_turnover_ratio"
]].mean().round(3)

# Sort by points
player_profiles = player_profiles.sort_values(
    by="pts",
    ascending=False
)

print("\nWNBA PLAYER PROFILES\n")

for player, row in player_profiles.iterrows():

    # Skip players without enough data
    if pd.isna(row["pts"]):
        continue

    print(f"{player}")
    print("-" * 40)

    print(f"Points: {row['pts']}")
    print(f"Rebounds: {row['reb']}")
    print(f"Assists: {row['ast']}")
    print(f"Shot Value: {row['player_shot_value']}")
    print(f"Offensive Flow: {row['player_offensive_flow']}")
    print(f"Assist/Turnover Ratio: {row['assist_turnover_ratio']}")
    print()

    # Scoring profile
    if row["pts"] >= 20:
        print("High-volume scorer")
    elif row["pts"] >= 12:
        print("Reliable scoring option")
    else:
        print("Lower scoring role")

    # Playmaking profile
    if row["ast"] >= 6:
        print("Primary playmaker")
    elif row["ast"] >= 3:
        print("Secondary creator")
    else:
        print("Limited playmaking role")

    # Shot value profile
    if row["player_shot_value"] >= 0.80:
        print("Strong scoring efficiency")
    elif row["player_shot_value"] >= 0.60:
        print("Average scoring efficiency")
    else:
        print("Low scoring efficiency")

    # Offensive flow profile
    if row["player_offensive_flow"] >= 1.5:
        print("High offensive connector")
    elif row["player_offensive_flow"] >= 0.8:
        print("Moderate offensive connector")
    else:
        print("Lower offensive flow impact")

    # Ball security/playmaking balance
    if row["assist_turnover_ratio"] >= 2:
        print("Strong decision-maker")
    elif row["assist_turnover_ratio"] >= 1:
        print("Average decision-making")
    else:
        print("Turnover-prone creator")

    print("\n")

# Save player profiles
player_profiles.to_csv(
    "../outputs/player_profiles.csv"
)

print("Player profiles saved successfully.")