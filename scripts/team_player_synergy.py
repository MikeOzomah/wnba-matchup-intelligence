import pandas as pd

# Load datasets
players_df = pd.read_csv("../outputs/player_influence_profiles.csv")
teams_df = pd.read_csv("../outputs/team_style_classifications.csv")


def classify_archetypes(row):
    archetypes = []

    pts = row["pts"]
    ast = row["ast"]
    reb = row["reb"]
    stl = row["stl"]
    blk = row["blk"]
    fga = row["fga"]
    three_pa = row["3pa"]
    fta = row["fta"]
    ast_to = row["assist_turnover_ratio"]

    # SCORING ARCHETYPES
    if pts >= 20 and three_pa >= 5:
        archetypes.append("Perimeter Scoring Engine")
    elif pts >= 20 and fta >= 5 and reb >= 5:
        archetypes.append("Physical Scoring Engine")
    elif pts >= 15:
        archetypes.append("Primary Scorer")

    # SHOOTING / SPACING
    if three_pa >= 6:
        archetypes.append("High-Gravity Shooter")
    elif three_pa >= 3:
        archetypes.append("Floor Spacer")

    # PLAYMAKING
    if ast >= 6:
        archetypes.append("Primary Playmaker")
    elif ast >= 3:
        archetypes.append("Secondary Creator")

    # INTERIOR PRESSURE
    if fta >= 6 and reb >= 6 and three_pa < 3:
        archetypes.append("Interior Pressure Creator")
    elif fta >= 5:
        archetypes.append("Foul Pressure Creator")

    # REBOUNDING
    if reb >= 8:
        archetypes.append("Rebounding Anchor")
    elif reb >= 5:
        archetypes.append("Positive Rebounder")

    # DEFENSE
    if stl >= 2:
        archetypes.append("Defensive Disruptor")

    if blk >= 2:
        archetypes.append("Rim Protector")

    # DECISION MAKING
    if ast_to >= 2 and ast >= 3:
        archetypes.append("Decision Stabilizer")

    # FALLBACK
    if not archetypes:
        archetypes.append("Role Contributor")

    return archetypes


print("\nTEAM <-> PLAYER SYNERGY ENGINE")
print("=" * 75)

# LOOP THROUGH TEAMS
for _, team_row in teams_df.iterrows():

    team_name = team_row["team"]

    tempo_style = team_row["tempo_style"]
    shot_profile = team_row["shot_profile"]
    flow_profile = team_row["flow_profile"]
    defense_profile = team_row["defense_profile"]

    print(f"\n{team_name}")
    print("=" * 75)

    print("TEAM IDENTITY")
    print("-" * 45)
    print(f"Tempo: {tempo_style}")
    print(f"Shot Profile: {shot_profile}")
    print(f"Offensive Flow: {flow_profile}")
    print(f"Defense: {defense_profile}")

    # Pull team players
    team_players = players_df[
        players_df["team"] == team_name
    ]

    if team_players.empty:
        print("\nNo player data available.")
        continue

    print("\nPLAYER SYNERGY")
    print("-" * 45)

    for _, player_row in team_players.iterrows():

        player_name = player_row["player"]

        archetypes = classify_archetypes(player_row)

        synergy_notes = []

        # TEMPO SYNERGY
        if (
            tempo_style == "Fast Tempo"
            and "Primary Playmaker" in archetypes
        ):
            synergy_notes.append(
                "helps accelerate transition pace and early-clock offense"
            )

        if (
            tempo_style == "Controlled Tempo"
            and "Decision Stabilizer" in archetypes
        ):
            synergy_notes.append(
                "helps stabilize possessions and maintain half-court organization"
            )

        # SHOT PROFILE SYNERGY
        if (
            shot_profile == "High Value Shot Creation"
            and "High-Gravity Shooter" in archetypes
        ):
            synergy_notes.append(
                "creates perimeter gravity that improves overall shot quality"
            )

        if (
            shot_profile == "Balanced Shot Profile"
            and "Physical Scoring Engine" in archetypes
        ):
            synergy_notes.append(
                "balances perimeter offense with physical interior scoring"
            )

        # FLOW SYNERGY
        if (
            flow_profile == "Connected Offensive Flow"
            and "Primary Playmaker" in archetypes
        ):
            synergy_notes.append(
                "helps sustain offensive rhythm through passing and initiation"
            )

        if (
            flow_profile == "Connected Offensive Flow"
            and "Floor Spacer" in archetypes
        ):
            synergy_notes.append(
                "supports offensive flow by maintaining spacing during rotations"
            )

        # DEFENSIVE SYNERGY
        if (
            defense_profile == "Aggressive Defensive Pressure"
            and "Defensive Disruptor" in archetypes
        ):
            synergy_notes.append(
                "creates transition opportunities through defensive activity"
            )

        if (
            defense_profile == "Aggressive Defensive Pressure"
            and "Rim Protector" in archetypes
        ):
            synergy_notes.append(
                "supports aggressive perimeter pressure with interior rim protection"
            )

        # REBOUNDING / POSSESSION CONTROL
        if "Rebounding Anchor" in archetypes:
            synergy_notes.append(
                "drives possession control through rebounding and second-chance opportunities"
            )

        if "Positive Rebounder" in archetypes:
            synergy_notes.append(
                "adds possession value through rebounding activity"
            )

        # INTERIOR PRESSURE
        if "Interior Pressure Creator" in archetypes:
            synergy_notes.append(
                "creates paint pressure that can collapse defenses and force help rotations"
            )

        # PLAYMAKING
        if "Primary Playmaker" in archetypes:
            synergy_notes.append(
                "helps organize offensive possessions and control initiation responsibility"
            )

        # PERIMETER PRESSURE
        if "High-Gravity Shooter" in archetypes:
            synergy_notes.append(
                "forces defensive attention beyond the arc and stretches defensive coverage"
            )

        # FALLBACK
        if not synergy_notes:
            synergy_notes.append(
                "No major team-style amplification detected yet based on current sample size."
            )

        print(f"\n{player_name}")

        print("Archetypes:")
        for archetype in archetypes:
            print(f"- {archetype}")

        print("Synergy Impact:")
        for note in synergy_notes:
            print(f"- {note}")

print("\nTeam-player synergy analysis completed successfully.")