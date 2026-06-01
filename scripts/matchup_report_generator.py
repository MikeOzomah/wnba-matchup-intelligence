import pandas as pd

teams_df = pd.read_csv("../outputs/team_style_classifications.csv")
players_df = pd.read_csv("../outputs/player_influence_profiles.csv")

TEAM_A = "Las Vegas Aces"
TEAM_B = "Indiana Fever"


def add_team_relative_roles(players):
    players = players.copy()

    players["team_pts_rank"] = players.groupby("team")["pts"].rank(
        ascending=False,
        method="min"
    )

    players["team_fga_rank"] = players.groupby("team")["fga"].rank(
        ascending=False,
        method="min"
    )

    players["team_ast_rank"] = players.groupby("team")["ast"].rank(
        ascending=False,
        method="min"
    )

    players["team_reb_rank"] = players.groupby("team")["reb"].rank(
        ascending=False,
        method="min"
    )

    return players


players_df = add_team_relative_roles(players_df)


def get_team(team_name):
    team = teams_df[teams_df["team"] == team_name]

    if team.empty:
        print(f"Team not found: {team_name}")
        print("Available teams:", teams_df["team"].unique())
        raise SystemExit

    return team.iloc[0]


def get_team_players(team_name, top_n=3):
    team_players = players_df[players_df["team"] == team_name].copy()

    if team_players.empty:
        return pd.DataFrame()

    team_players["impact_score"] = (
        team_players["pts"].fillna(0)
        + team_players["ast"].fillna(0) * 1.5
        + team_players["reb"].fillna(0)
        + team_players["stl"].fillna(0) * 1.25
        + team_players["blk"].fillna(0) * 1.25
    )

    return team_players.sort_values(
        by="impact_score",
        ascending=False
    ).head(top_n)


def scoring_role(row):
    """
    Scoring role = how important this player is as a scorer.
    This uses both raw points and team-relative rank.
    """

    if row["pts"] >= 20:
        return "primary scoring option"

    if row["team_pts_rank"] <= 3 and row["pts"] >= 15:
        return "primary scoring option"

    if row["team_pts_rank"] <= 2 and row["team_fga_rank"] <= 2:
        return "co-primary scoring option"

    if row["pts"] >= 12:
        return "secondary scoring option"

    if row["fga"] >= 8:
        return "volume scoring contributor"

    return "role scorer"


def offensive_role(row):
    """
    Offensive role = how much this player drives the offense beyond scoring.
    This captures playmaking, initiation, and offensive responsibility.
    """

    if row["team_ast_rank"] == 1 and row["pts"] >= 15:
        return "primary offensive engine"

    if row["team_ast_rank"] == 1 and row["ast"] >= 5:
        return "primary playmaker"

    if row["ast"] >= 6:
        return "primary creator"

    if row["ast"] >= 3:
        return "secondary creator"

    return None


def describe_player(row):
    tags = []

    # Separate scoring role from offensive engine/playmaking role
    tags.append(scoring_role(row))

    role = offensive_role(row)
    if role:
        tags.append(role)

    # Spacing / perimeter pressure
    if row["3pa"] >= 6:
        tags.append("perimeter gravity")
    elif row["3pa"] >= 3:
        tags.append("floor spacer")

    # Rebounding
    if row["team_reb_rank"] == 1 and row["reb"] >= 5:
        tags.append("team rebounding leader")
    elif row["reb"] >= 8:
        tags.append("rebounding anchor")
    elif row["reb"] >= 5:
        tags.append("positive rebounder")

    # Defensive activity
    if row["stl"] >= 2:
        tags.append("defensive disruptor")

    if row["blk"] >= 2:
        tags.append("rim protection presence")

    return ", ".join(tags)


def determine_game_environment(team_a, team_b):
    if (
        team_a["tempo_style"] == "Fast Tempo"
        and team_b["tempo_style"] == "Controlled Tempo"
    ) or (
        team_b["tempo_style"] == "Fast Tempo"
        and team_a["tempo_style"] == "Controlled Tempo"
    ):
        return "Transition vs Control Matchup"

    if (
        team_a["shot_profile"] == "High Value Shot Creation"
        and team_b["shot_profile"] == "High Value Shot Creation"
    ):
        return "Shot Quality Battle"

    if (
        team_a["defense_profile"] == "Aggressive Defensive Pressure"
        or team_b["defense_profile"] == "Aggressive Defensive Pressure"
    ):
        return "Possession Pressure Game"

    if (
        team_a["flow_profile"] == "Connected Offensive Flow"
        and team_b["flow_profile"] == "Connected Offensive Flow"
    ):
        return "Flow and Rotation Game"

    return "Balanced Style Matchup"


def style_edge(team_a_name, team_b_name, team_a, team_b):
    lines = []

    if team_a["tempo_style"] != team_b["tempo_style"]:
        faster = (
            team_a_name if team_a["tempo_style"] == "Fast Tempo"
            else team_b_name if team_b["tempo_style"] == "Fast Tempo"
            else None
        )

        slower = (
            team_a_name if team_a["tempo_style"] == "Controlled Tempo"
            else team_b_name if team_b["tempo_style"] == "Controlled Tempo"
            else None
        )

        if faster and slower:
            lines.append(
                f"{faster} benefits if the game opens up in transition, while {slower} benefits if possessions become more organized and half-court oriented."
            )
        elif faster:
            lines.append(
                f"{faster} has the stronger pace profile and may try to increase possession volume."
            )
        elif slower:
            lines.append(
                f"{slower} has the more controlled tempo profile and may try to reduce volatility."
            )

    if team_a["shot_profile"] != team_b["shot_profile"]:
        high_value = (
            team_a_name if team_a["shot_profile"] == "High Value Shot Creation"
            else team_b_name if team_b["shot_profile"] == "High Value Shot Creation"
            else None
        )

        if high_value:
            lines.append(
                f"{high_value} enters with the clearer shot-value profile, which means the opponent must reduce clean threes, rim pressure, and free-throw creation."
            )

    if team_a["flow_profile"] != team_b["flow_profile"]:
        connected = (
            team_a_name if team_a["flow_profile"] == "Connected Offensive Flow"
            else team_b_name if team_b["flow_profile"] == "Connected Offensive Flow"
            else None
        )

        if connected:
            lines.append(
                f"{connected} has the stronger ball-movement profile, so defensive communication and closeout discipline become important."
            )

    if team_a["defense_profile"] != team_b["defense_profile"]:
        pressure = (
            team_a_name if team_a["defense_profile"] == "Aggressive Defensive Pressure"
            else team_b_name if team_b["defense_profile"] == "Aggressive Defensive Pressure"
            else None
        )

        if pressure:
            lines.append(
                f"{pressure} can create value by turning defensive activity into rushed decisions and transition chances."
            )

    if not lines:
        lines.append(
            "Neither team has a major style separation yet, so execution, shot quality, and player production may decide the matchup."
        )

    return lines


def pressure_points(team_name, opponent_name, team, opponent):
    points = []

    if team["tempo_style"] == "Fast Tempo":
        points.append(
            f"{team_name}'s pace can pressure {opponent_name} before its half-court defense is fully set."
        )

    if team["tempo_style"] == "Controlled Tempo":
        points.append(
            f"{team_name}'s controlled tempo can reduce transition randomness and force {opponent_name} into longer possessions."
        )

    if team["shot_profile"] == "High Value Shot Creation":
        points.append(
            f"{team_name}'s shot profile can stress rotations through threes, rim pressure, and free-throw chances."
        )

    if team["flow_profile"] == "Connected Offensive Flow":
        points.append(
            f"{team_name}'s ball movement can force repeated closeouts and communication stress."
        )

    if team["defense_profile"] == "Aggressive Defensive Pressure":
        points.append(
            f"{team_name}'s defensive pressure can speed up decisions and create live-ball turnover chances."
        )

    if team["security_profile"] == "Turnover Vulnerable":
        points.append(
            f"{team_name}'s ball security could become a stress point if {opponent_name} increases pressure."
        )

    if not points:
        points.append(
            f"{team_name}'s main pressure point is establishing a clear identity advantage early."
        )

    return points


def matchup_counters(team_name, opponent_name, team, opponent):
    counters = []

    if opponent["tempo_style"] == "Fast Tempo":
        counters.append(
            f"{team_name} must protect the ball, communicate early, and get matched in transition to reduce {opponent_name}'s pace advantage."
        )

    if opponent["tempo_style"] == "Controlled Tempo":
        counters.append(
            f"{team_name} must avoid being dragged into long possessions where {opponent_name} can control rhythm."
        )

    if opponent["shot_profile"] == "High Value Shot Creation":
        counters.append(
            f"{team_name} must limit rhythm threes, rim touches, and foul-driven scoring chances."
        )

    if opponent["flow_profile"] == "Connected Offensive Flow":
        counters.append(
            f"{team_name} must disrupt passing rhythm without overhelping into weak-side breakdowns."
        )

    if opponent["defense_profile"] == "Aggressive Defensive Pressure":
        counters.append(
            f"{team_name} should use quick outlets, spacing, and secondary ball handlers to punish pressure."
        )

    if not counters:
        counters.append(
            f"{team_name} must stay disciplined, protect possessions, and avoid letting {opponent_name} dictate rhythm."
        )

    return counters


def detailed_swing_factors(team_a_name, team_b_name, team_a, team_b, a_players, b_players):
    factors = []

    if team_a["tempo_style"] != team_b["tempo_style"]:
        fast_team = (
            team_a_name if team_a["tempo_style"] == "Fast Tempo"
            else team_b_name if team_b["tempo_style"] == "Fast Tempo"
            else None
        )

        control_team = (
            team_a_name if team_a["tempo_style"] == "Controlled Tempo"
            else team_b_name if team_b["tempo_style"] == "Controlled Tempo"
            else None
        )

        if fast_team and control_team:
            factors.append(
                f"Tempo control: {fast_team} benefits if the game becomes open-floor and transition-heavy, while {control_team} benefits if the matchup turns into a slower half-court possession battle."
            )
        elif fast_team:
            factors.append(
                f"Tempo control: {fast_team}'s pace can increase possession volume and create defensive cross-match pressure."
            )
        elif control_team:
            factors.append(
                f"Tempo control: {control_team}'s pace discipline can reduce randomness and make the game more execution-based."
            )

    if (
        team_a["defense_profile"] == "Aggressive Defensive Pressure"
        or team_b["defense_profile"] == "Aggressive Defensive Pressure"
        or team_a["security_profile"] == "Turnover Vulnerable"
        or team_b["security_profile"] == "Turnover Vulnerable"
    ):
        factors.append(
            "Ball security: live-ball turnovers can immediately shift the game by creating transition chances, foul pressure, and momentum swings before the defense gets organized."
        )
    else:
        factors.append(
            "Ball security: even without an extreme pressure profile, empty possessions can decide the matchup if shot quality is similar."
        )

    if team_a["shot_profile"] != team_b["shot_profile"]:
        high_value_team = (
            team_a_name if team_a["shot_profile"] == "High Value Shot Creation"
            else team_b_name if team_b["shot_profile"] == "High Value Shot Creation"
            else None
        )

        if high_value_team:
            factors.append(
                f"Shot quality: {high_value_team} has a stronger shot-value identity, so the opponent must reduce clean perimeter looks, paint touches, and free-throw opportunities."
            )
    else:
        factors.append(
            "Shot quality: because both teams have similar shot-profile labels, the difference may come from who creates cleaner looks late in possessions."
        )

    connected_team = []

    if team_a["flow_profile"] == "Connected Offensive Flow":
        connected_team.append(team_a_name)

    if team_b["flow_profile"] == "Connected Offensive Flow":
        connected_team.append(team_b_name)

    if connected_team:
        factors.append(
            f"Offensive flow: {', '.join(connected_team)} can create rotational stress through ball movement, but overpassing or pressure can turn flow into turnovers."
        )

    a_key = a_players.iloc[0]["player"] if not a_players.empty else None
    b_key = b_players.iloc[0]["player"] if not b_players.empty else None

    if a_key or b_key:
        factors.append(
            f"Key player production: {a_key or team_a_name}'s impact and {b_key or team_b_name}'s impact can swing the game if one side creates a clear advantage through scoring, creation, rebounding, or defensive activity."
        )

    factors.append(
        "Foul discipline: early foul trouble can change rotations, reduce defensive aggression, and alter which players are available in the game's most important stretches."
    )

    return factors


def final_read(team_a_name, team_b_name, team_a, team_b, env, a_players, b_players):
    a_key_player = (
        a_players.iloc[0]["player"] if not a_players.empty
        else "their primary contributors"
    )

    b_key_player = (
        b_players.iloc[0]["player"] if not b_players.empty
        else "their primary contributors"
    )

    return (
        f"This matchup profiles as a {env.lower()}. "
        f"{team_a_name} brings a {team_a['tempo_style'].lower()} identity with {team_a['shot_profile'].lower()} and {team_a['flow_profile'].lower()}, "
        f"while {team_b_name} brings a {team_b['tempo_style'].lower()} identity with {team_b['shot_profile'].lower()} and {team_b['defense_profile'].lower()}.\n\n"
        f"The key player layer matters here: {a_key_player} is one of the main players shaping {team_a_name}'s current profile, "
        f"while {b_key_player} is one of the main players shaping {team_b_name}'s profile. "
        f"The game is likely to tilt toward the team that better controls tempo, protects possessions, and creates cleaner scoring opportunities.\n\n"
        f"If {team_a_name} can impose its preferred style while limiting empty possessions, it can sustain pressure across multiple phases of the game. "
        f"If {team_b_name} can disrupt that rhythm, control shot quality, and generate value from its key players, it can shift the matchup environment in its favor."
    )


team_a = get_team(TEAM_A)
team_b = get_team(TEAM_B)

team_a_players = get_team_players(TEAM_A)
team_b_players = get_team_players(TEAM_B)

environment = determine_game_environment(team_a, team_b)

report_lines = []

report_lines.append("WNBA MATCHUP REPORT")
report_lines.append("=" * 70)
report_lines.append(f"{TEAM_A} vs {TEAM_B}")
report_lines.append("=" * 70)

report_lines.append("\n1. GAME ENVIRONMENT")
report_lines.append("-" * 45)
report_lines.append(environment)

report_lines.append("\n2. TEAM STYLE CLASH")
report_lines.append("-" * 45)
for line in style_edge(TEAM_A, TEAM_B, team_a, team_b):
    report_lines.append(f"- {line}")

report_lines.append("\n3. KEY PLAYER DRIVERS")
report_lines.append("-" * 45)

report_lines.append(f"\n{TEAM_A}:")
if team_a_players.empty:
    report_lines.append("- No player data available yet.")
else:
    for _, row in team_a_players.iterrows():
        report_lines.append(
            f"- {row['player']}: {describe_player(row)} "
            f"({row['pts']} PTS, {row['reb']} REB, {row['ast']} AST)"
        )

report_lines.append(f"\n{TEAM_B}:")
if team_b_players.empty:
    report_lines.append("- No player data available yet.")
else:
    for _, row in team_b_players.iterrows():
        report_lines.append(
            f"- {row['player']}: {describe_player(row)} "
            f"({row['pts']} PTS, {row['reb']} REB, {row['ast']} AST)"
        )

report_lines.append("\n4. TACTICAL PRESSURE POINTS")
report_lines.append("-" * 45)

report_lines.append(f"\n{TEAM_A}:")
for point in pressure_points(TEAM_A, TEAM_B, team_a, team_b):
    report_lines.append(f"- {point}")

report_lines.append(f"\n{TEAM_B}:")
for point in pressure_points(TEAM_B, TEAM_A, team_b, team_a):
    report_lines.append(f"- {point}")

report_lines.append("\n5. COUNTERS / ADJUSTMENTS")
report_lines.append("-" * 45)

report_lines.append(f"\n{TEAM_A}:")
for counter in matchup_counters(TEAM_A, TEAM_B, team_a, team_b):
    report_lines.append(f"- {counter}")

report_lines.append(f"\n{TEAM_B}:")
for counter in matchup_counters(TEAM_B, TEAM_A, team_b, team_a):
    report_lines.append(f"- {counter}")

report_lines.append("\n6. SWING FACTORS")
report_lines.append("-" * 45)
for factor in detailed_swing_factors(
    TEAM_A,
    TEAM_B,
    team_a,
    team_b,
    team_a_players,
    team_b_players
):
    report_lines.append(f"- {factor}")

report_lines.append("\n7. FINAL READ")
report_lines.append("-" * 45)
report_lines.append(
    final_read(
        TEAM_A,
        TEAM_B,
        team_a,
        team_b,
        environment,
        team_a_players,
        team_b_players
    )
)

final_report = "\n".join(report_lines)

print(final_report)

with open("../outputs/matchup_report.txt", "w", encoding="utf-8") as file:
    file.write(final_report)

print("\nMatchup report saved to outputs/matchup_report.txt")