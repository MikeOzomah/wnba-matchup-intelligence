import pandas as pd

# Load cleaned player data
df = pd.read_csv("../outputs/cleaned_player_data.csv")

# Group player averages
player_profiles = df.groupby(["player", "team", "position"])[[
    "pts",
    "reb",
    "ast",
    "stl",
    "blk",
    "to",
    "fgm",
    "fga",
    "3pm",
    "3pa",
    "ftm",
    "fta",
    "player_shot_value",
    "player_offensive_flow",
    "assist_turnover_ratio"
]].mean().round(3)

player_profiles = player_profiles.reset_index()

print("\nPLAYER INFLUENCE ENGINE")
print("=" * 60)

for _, row in player_profiles.iterrows():

    player = row["player"]
    team = row["team"]

    pts = row["pts"]
    reb = row["reb"]
    ast = row["ast"]
    stl = row["stl"]
    blk = row["blk"]
    to = row["to"]
    fga = row["fga"]
    three_pa = row["3pa"]
    fta = row["fta"]
    shot_value = row["player_shot_value"]
    offensive_flow = row["player_offensive_flow"]
    ast_to = row["assist_turnover_ratio"]

    influence_tags = []

    # Scoring load
    if pts >= 20:
        influence_tags.append("Primary Scoring Engine")
    elif pts >= 12:
        influence_tags.append("Secondary Scoring Option")

    # Shot creation / usage
    if fga >= 15:
        influence_tags.append("High-Usage Shot Creator")
    elif fga >= 10:
        influence_tags.append("Moderate Shot Creator")

    # Perimeter gravity
    if three_pa >= 6:
        influence_tags.append("Perimeter Gravity")
    elif three_pa >= 3:
        influence_tags.append("Floor Spacer")

    # Rim / foul pressure
    if fta >= 6:
        influence_tags.append("Paint / Foul Pressure Creator")
    elif fta >= 3:
        influence_tags.append("Contact Pressure Threat")

    # Playmaking
    if ast >= 6:
        influence_tags.append("Primary Playmaker")
    elif ast >= 3:
        influence_tags.append("Secondary Creator")

    # Offensive connection
    if offensive_flow >= 1.5:
        influence_tags.append("Offensive Connector")

    # Ball security / decision making
    if ast_to >= 2:
        influence_tags.append("Strong Decision-Maker")
    elif ast_to < 1 and ast >= 3:
        influence_tags.append("Turnover-Risk Creator")

    # Rebounding
    if reb >= 8:
        influence_tags.append("Rebounding Anchor")
    elif reb >= 5:
        influence_tags.append("Positive Rebounding Presence")

    # Defensive activity
    if stl >= 2:
        influence_tags.append("Passing Lane Disruptor")

    if blk >= 2:
        influence_tags.append("Rim Protection Presence")

    # Skip low-impact players for now
    if not influence_tags:
        continue

    print(f"\n{player} -- {team}")
    print("-" * 50)

    print(f"Points: {pts}")
    print(f"Assists: {ast}")
    print(f"Rebounds: {reb}")
    print(f"Shot Value: {shot_value}")
    print(f"Offensive Flow: {offensive_flow}")
    print(f"Assist/Turnover Ratio: {ast_to}")

    print("\nInfluence Tags:")
    for tag in influence_tags:
        print(f"- {tag}")

    print("\nBasketball Interpretation:")

    if "Primary Scoring Engine" in influence_tags:
        print(f"{player} carries a major scoring responsibility for {team}.")

    if "Perimeter Gravity" in influence_tags:
        print(f"{player}'s perimeter volume can stretch defenses and create longer closeout situations.")

    if "Primary Playmaker" in influence_tags:
        print(f"{player} helps organize offense through passing volume and creation responsibility.")

    if "Paint / Foul Pressure Creator" in influence_tags:
        print(f"{player} can create interior pressure that forces defensive help and foul risk.")

    if "Rebounding Anchor" in influence_tags:
        print(f"{player} helps control possessions through rebounding impact.")

    if "Turnover-Risk Creator" in influence_tags:
        print(f"{player}'s creation role comes with decision-making risk under pressure.")

# Save output table
player_profiles.to_csv("../outputs/player_influence_profiles.csv", index=False)

print("\nPlayer influence profiles saved successfully.")