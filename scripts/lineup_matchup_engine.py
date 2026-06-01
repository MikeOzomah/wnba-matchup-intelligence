import pandas as pd

players_df = pd.read_csv("../outputs/cleaned_player_data.csv")

TEAM_A = "Atlanta Dream"
TEAM_B = "Dallas Wings"


def minutes_to_float(min_value):
    if pd.isna(min_value):
        return 0

    min_value = str(min_value)

    if ":" in min_value:
        minutes, seconds = min_value.split(":")
        return int(minutes) + int(seconds) / 60

    try:
        return float(min_value)
    except ValueError:
        return 0


def get_lineup(team_name, top_n=5):
    team_players = players_df[players_df["team"] == team_name].copy()

    if team_players.empty:
        print(f"No player data found for {team_name}")
        raise SystemExit

    team_players["minutes_float"] = team_players["min"].apply(minutes_to_float)

    summary = team_players.groupby(
        ["player", "team", "position"],
        as_index=False
    ).agg({
        "minutes_float": "mean",
        "pts": "mean",
        "reb": "mean",
        "ast": "mean",
        "stl": "mean",
        "blk": "mean",
        "3pa": "mean",
        "fga": "mean"
    })

    summary = summary.round({
        "minutes_float": 1,
        "pts": 1,
        "reb": 1,
        "ast": 1,
        "stl": 1,
        "blk": 1,
        "3pa": 1,
        "fga": 1
    })

    summary["team_pts_rank"] = summary["pts"].rank(
        ascending=False,
        method="min"
    )

    summary["team_ast_rank"] = summary["ast"].rank(
        ascending=False,
        method="min"
    )

    summary["team_fga_rank"] = summary["fga"].rank(
        ascending=False,
        method="min"
    )

    return summary.sort_values(
        by="minutes_float",
        ascending=False
    ).head(top_n)


def classify_player(row):
    tags = []

    if row["pts"] >= 20:
        tags.append("Primary Scorer")
    elif row["team_pts_rank"] <= 3 and row["pts"] >= 15:
        tags.append("Primary Scorer")
    elif row["team_pts_rank"] <= 2 and row["team_fga_rank"] <= 2:
        tags.append("Co-Primary Scorer")
    elif row["pts"] >= 12:
        tags.append("Secondary Scorer")

    if row["team_ast_rank"] == 1 and row["pts"] >= 15:
        tags.append("Primary Offensive Engine")
    elif row["team_ast_rank"] == 1 and row["ast"] >= 5:
        tags.append("Primary Playmaker")
    elif row["ast"] >= 6:
        tags.append("Primary Creator")
    elif row["ast"] >= 3:
        tags.append("Secondary Creator")

    if row["3pa"] >= 6:
        tags.append("High Gravity Shooter")
    elif row["3pa"] >= 3:
        tags.append("Floor Spacer")

    if row["reb"] >= 8:
        tags.append("Rebounding Anchor")
    elif row["reb"] >= 5:
        tags.append("Positive Rebounder")

    if row["stl"] >= 2:
        tags.append("Defensive Disruptor")

    if row["blk"] >= 2:
        tags.append("Rim Protector")

    if row["position"] == "C":
        tags.append("Interior Big")
    elif row["position"] == "F":
        tags.append("Forward")
    elif row["position"] == "G":
        tags.append("Guard")

    return tags


def lineup_scores(lineup):
    scores = {
        "pace": 0,
        "spacing": 0,
        "creation": 0,
        "rebounding": 0,
        "defense": 0,
        "size": 0
    }

    for _, row in lineup.iterrows():
        tags = classify_player(row)

        if "Primary Offensive Engine" in tags:
            scores["pace"] += 2
            scores["creation"] += 3

        if "Primary Creator" in tags:
            scores["creation"] += 2

        if "Primary Playmaker" in tags:
            scores["creation"] += 2

        if "Secondary Creator" in tags:
            scores["creation"] += 1

        if "High Gravity Shooter" in tags:
            scores["spacing"] += 3

        if "Floor Spacer" in tags:
            scores["spacing"] += 2

        if "Rebounding Anchor" in tags:
            scores["rebounding"] += 3

        if "Positive Rebounder" in tags:
            scores["rebounding"] += 1

        if "Defensive Disruptor" in tags:
            scores["defense"] += 2

        if "Rim Protector" in tags:
            scores["defense"] += 2

        if "Interior Big" in tags:
            scores["size"] += 3

        if "Forward" in tags:
            scores["size"] += 1

        if "Guard" in tags:
            scores["pace"] += 1

    return scores


def score_label(value, category):
    if category == "spacing":
        if value >= 8:
            return "elite spacing"
        elif value >= 5:
            return "functional spacing"
        return "limited spacing"

    if category == "creation":
        if value >= 8:
            return "multi-creator"
        elif value >= 4:
            return "structured creation"
        return "limited creation"

    if category == "rebounding":
        if value >= 6:
            return "strong rebounding"
        elif value >= 3:
            return "moderate rebounding"
        return "limited rebounding"

    if category == "defense":
        if value >= 6:
            return "high defensive disruption"
        elif value >= 3:
            return "balanced defensive activity"
        return "low defensive disruption"

    if category == "size":
        if value >= 7:
            return "big/interior-oriented"
        elif value >= 4:
            return "balanced size"
        return "smaller/guard-heavy"

    if category == "pace":
        if value >= 7:
            return "high-speed"
        elif value >= 4:
            return "balanced tempo"
        return "controlled tempo"

    return "neutral"


def print_lineup(team_name, lineup, scores):
    print(f"\n{team_name} Lineup")
    print("-" * 50)

    for _, row in lineup.iterrows():
        print(
            f"- {row['player']} | {row['position']} | "
            f"{row['minutes_float']} MIN | {row['pts']} PTS | "
            f"{row['reb']} REB | {row['ast']} AST"
        )

    print("\nLineup Profile:")
    print(f"- Pace: {score_label(scores['pace'], 'pace')}")
    print(f"- Spacing: {score_label(scores['spacing'], 'spacing')}")
    print(f"- Creation: {score_label(scores['creation'], 'creation')}")
    print(f"- Rebounding: {score_label(scores['rebounding'], 'rebounding')}")
    print(f"- Defense: {score_label(scores['defense'], 'defense')}")
    print(f"- Size: {score_label(scores['size'], 'size')}")


def compare_category(team_a, team_b, scores_a, scores_b, category, label):
    a_score = scores_a[category]
    b_score = scores_b[category]

    if a_score > b_score:
        return f"{label}: {team_a} edge"
    elif b_score > a_score:
        return f"{label}: {team_b} edge"
    return f"{label}: Even"


def tactical_collision(team_a, team_b, scores_a, scores_b):
    notes = []

    if scores_a["pace"] > scores_b["pace"]:
        notes.append(
            f"{team_a} may try to increase tempo and force {team_b} into earlier defensive matchups."
        )
    elif scores_b["pace"] > scores_a["pace"]:
        notes.append(
            f"{team_b} may try to increase tempo and force {team_a} into earlier defensive matchups."
        )

    if scores_a["spacing"] > scores_b["defense"]:
        notes.append(
            f"{team_a}'s spacing may stretch {team_b}'s defensive shell and create longer closeouts."
        )

    if scores_b["spacing"] > scores_a["defense"]:
        notes.append(
            f"{team_b}'s spacing may stretch {team_a}'s defensive shell and create longer closeouts."
        )

    if scores_a["creation"] > scores_b["defense"]:
        notes.append(
            f"{team_a}'s creation profile may pressure {team_b}'s defensive rotations."
        )

    if scores_b["creation"] > scores_a["defense"]:
        notes.append(
            f"{team_b}'s creation profile may pressure {team_a}'s defensive rotations."
        )

    if scores_a["rebounding"] > scores_b["size"]:
        notes.append(
            f"{team_a} may create possession pressure through rebounding if {team_b} cannot match size and physicality."
        )

    if scores_b["rebounding"] > scores_a["size"]:
        notes.append(
            f"{team_b} may create possession pressure through rebounding if {team_a} cannot match size and physicality."
        )

    if scores_a["defense"] > scores_b["creation"]:
        notes.append(
            f"{team_a}'s defensive activity may disrupt {team_b}'s initiation and force rushed decisions."
        )

    if scores_b["defense"] > scores_a["creation"]:
        notes.append(
            f"{team_b}'s defensive activity may disrupt {team_a}'s initiation and force rushed decisions."
        )

    if not notes:
        notes.append(
            "This lineup matchup profiles as balanced, with execution and shot quality likely deciding the advantage."
        )

    return notes


def swing_factors(team_a, team_b, scores_a, scores_b):
    factors = []

    if scores_a["spacing"] != scores_b["spacing"]:
        stronger = team_a if scores_a["spacing"] > scores_b["spacing"] else team_b
        factors.append(
            f"Spacing: {stronger} has the cleaner spacing profile, which can affect driving lanes, closeouts, and shot quality."
        )

    if scores_a["creation"] != scores_b["creation"]:
        stronger = team_a if scores_a["creation"] > scores_b["creation"] else team_b
        factors.append(
            f"Creation: {stronger} has more creation support, which matters when first actions break down."
        )

    if scores_a["rebounding"] != scores_b["rebounding"]:
        stronger = team_a if scores_a["rebounding"] > scores_b["rebounding"] else team_b
        factors.append(
            f"Rebounding: {stronger} may control more possession value through second chances and defensive glass control."
        )

    if scores_a["defense"] != scores_b["defense"]:
        stronger = team_a if scores_a["defense"] > scores_b["defense"] else team_b
        factors.append(
            f"Defensive disruption: {stronger} may create more rushed decisions and transition opportunities."
        )

    factors.append(
        "Foul discipline: lineup advantages can disappear quickly if key creators or interior players get into foul trouble."
    )

    return factors


lineup_a = get_lineup(TEAM_A)
lineup_b = get_lineup(TEAM_B)

scores_a = lineup_scores(lineup_a)
scores_b = lineup_scores(lineup_b)

print("\nLINEUP MATCHUP ENGINE")
print("=" * 70)

print(f"\n{TEAM_A} vs {TEAM_B}")
print("=" * 70)

print_lineup(TEAM_A, lineup_a, scores_a)
print_lineup(TEAM_B, lineup_b, scores_b)

print("\nMATCHUP EDGES")
print("-" * 50)
print(compare_category(TEAM_A, TEAM_B, scores_a, scores_b, "pace", "Pace"))
print(compare_category(TEAM_A, TEAM_B, scores_a, scores_b, "spacing", "Spacing"))
print(compare_category(TEAM_A, TEAM_B, scores_a, scores_b, "creation", "Creation"))
print(compare_category(TEAM_A, TEAM_B, scores_a, scores_b, "rebounding", "Rebounding"))
print(compare_category(TEAM_A, TEAM_B, scores_a, scores_b, "defense", "Defensive Activity"))
print(compare_category(TEAM_A, TEAM_B, scores_a, scores_b, "size", "Size"))

print("\nTACTICAL COLLISION")
print("-" * 50)
for note in tactical_collision(TEAM_A, TEAM_B, scores_a, scores_b):
    print(f"- {note}")

print("\nLINEUP SWING FACTORS")
print("-" * 50)
for factor in swing_factors(TEAM_A, TEAM_B, scores_a, scores_b):
    print(f"- {factor}")

print("\nFINAL LINEUP READ")
print("-" * 50)
print(
    f"This lineup matchup should be evaluated through spacing, creation support, rebounding control, "
    f"defensive disruption, and size. The advantage belongs to the team that can force the matchup into "
    f"its preferred environment while protecting possessions and limiting high-value looks."
)

print("\nLineup matchup analysis completed successfully.")