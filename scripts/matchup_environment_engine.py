import pandas as pd

df = pd.read_csv("../outputs/team_style_classifications.csv")

# Change teams here
TEAM_A = "Atlanta Dream"
TEAM_B = "Chicago Sky"


def get_team(team_name):
    team = df[df["team"] == team_name]

    if team.empty:
        print(f"\nTeam not found: {team_name}")
        print("\nAvailable teams:")
        print(df["team"].unique())
        raise SystemExit

    return team.iloc[0]


def determine_game_label(team_a, team_b):
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


def print_team_style(team_name, team):
    print(f"\n{team_name} Style Profile")
    print("-" * 50)
    print(f"Tempo: {team['tempo_style']}")
    print(f"Shot Profile: {team['shot_profile']}")
    print(f"Offensive Flow: {team['flow_profile']}")
    print(f"Ball Security: {team['security_profile']}")
    print(f"Defense: {team['defense_profile']}")
    print(f"Offensive Identity: {team['offense_profile']}")


def pressure_points(team_name, opponent_name, team, opponent):
    points = []

    if team["tempo_style"] == "Fast Tempo":
        points.append(
            f"{team_name}'s pace can create early-clock pressure before {opponent_name}'s half-court defense is fully organized."
        )

    if team["tempo_style"] == "Controlled Tempo":
        points.append(
            f"{team_name}'s controlled tempo can reduce transition randomness and force {opponent_name} into longer defensive possessions."
        )

    if team["shot_profile"] == "High Value Shot Creation":
        points.append(
            f"{team_name}'s shot profile can pressure {opponent_name}'s rotations by generating cleaner threes, rim pressure, or free-throw chances."
        )

    if team["flow_profile"] == "Connected Offensive Flow":
        points.append(
            f"{team_name}'s ball movement can create repeated closeouts and force {opponent_name} to defend multiple actions."
        )

    if team["defense_profile"] == "Aggressive Defensive Pressure":
        points.append(
            f"{team_name}'s defensive pressure can speed up {opponent_name}'s decisions and create live-ball turnover chances."
        )

    if team["security_profile"] == "Turnover Vulnerable":
        points.append(
            f"{team_name}'s ball security could become a stress point if {opponent_name} increases pressure."
        )

    return points


def counter_chains(team_name, opponent_name, team, opponent):
    counters = []

    if opponent["tempo_style"] == "Fast Tempo":
        counters.append(
            f"{team_name} must prioritize transition floor balance, early communication, and limiting live-ball turnovers against {opponent_name}'s pace."
        )

    if opponent["shot_profile"] == "High Value Shot Creation":
        counters.append(
            f"{team_name} must reduce {opponent_name}'s clean scoring windows by taking away rhythm threes, paint touches, and free throws."
        )

    if opponent["flow_profile"] == "Connected Offensive Flow":
        counters.append(
            f"{team_name} must disrupt passing rhythm without overhelping, because over-rotating can create open weak-side looks."
        )

    if opponent["defense_profile"] == "Aggressive Defensive Pressure":
        counters.append(
            f"{team_name} should use quick outlets, secondary ball handlers, and simple reads to punish {opponent_name}'s pressure."
        )

    if opponent["tempo_style"] == "Controlled Tempo":
        counters.append(
            f"{team_name} must avoid getting dragged into a slow-possession game where {opponent_name} can control rhythm and reduce volatility."
        )

    return counters


def swing_factors(team_a_name, team_b_name, team_a, team_b):
    factors = []

    if team_a["tempo_style"] != team_b["tempo_style"]:
        factors.append(
            "Tempo control: whichever team forces the game into its preferred pace can shape the scoring environment."
        )

    if team_a["shot_profile"] != team_b["shot_profile"]:
        factors.append(
            "Shot quality: the team that creates more efficient looks without forcing difficult attempts gains the cleaner offensive path."
        )

    if (
        team_a["defense_profile"] == "Aggressive Defensive Pressure"
        or team_b["defense_profile"] == "Aggressive Defensive Pressure"
    ):
        factors.append(
            "Turnover pressure: live-ball mistakes could immediately shift possession value and transition scoring."
        )

    if (
        team_a["flow_profile"] == "Connected Offensive Flow"
        or team_b["flow_profile"] == "Connected Offensive Flow"
    ):
        factors.append(
            "Rotational stress: sustained ball movement can force defensive communication breakdowns over time."
        )

    factors.append(
        "Foul discipline: early foul trouble can change rotations, defensive aggression, and interior/perimeter coverage."
    )

    return factors


def failure_conditions(team_name, opponent_name, team, opponent):
    failures = []

    if team["tempo_style"] == "Fast Tempo":
        failures.append(
            f"{team_name} can lose its pace advantage if turnovers rise or {opponent_name} controls the defensive glass."
        )

    if team["tempo_style"] == "Controlled Tempo":
        failures.append(
            f"{team_name} can lose control if {opponent_name} creates live-ball turnovers and turns the game into transition possessions."
        )

    if team["shot_profile"] == "High Value Shot Creation":
        failures.append(
            f"{team_name}'s shot-value edge can disappear if spacing breaks down or possessions end in forced late-clock attempts."
        )

    if team["flow_profile"] == "Connected Offensive Flow":
        failures.append(
            f"{team_name}'s offensive flow can break if pressure disrupts initiation or passing windows become predictable."
        )

    if team["defense_profile"] == "Aggressive Defensive Pressure":
        failures.append(
            f"{team_name}'s pressure can backfire if over-aggression leads to fouls, missed rotations, or easy backside scoring."
        )

    if not failures:
        failures.append(
            f"{team_name}'s biggest risk is failing to establish a clear identity advantage early in the matchup."
        )

    return failures


def game_phase_projection(team_a_name, team_b_name, team_a, team_b):
    print("\nGAME PHASE PROJECTION")
    print("-" * 50)

    print("\nEarly Game:")
    if team_a["tempo_style"] == "Fast Tempo" or team_b["tempo_style"] == "Fast Tempo":
        fast_team = team_a_name if team_a["tempo_style"] == "Fast Tempo" else team_b_name
        print(
            f"- Expect {fast_team} to test transition chances early and see whether the opponent can get matched defensively."
        )
    else:
        print(
            "- Early possessions may be used to establish offensive rhythm, spacing, and defensive matchups."
        )

    print("\nMiddle Game:")
    print(
        "- The matchup may shift toward adjustments: defensive pressure, rebounding control, shot selection, and how each team responds after initial actions are taken away."
    )

    print("\nLate Game:")
    if (
        team_a["security_profile"] == "Strong Ball Security"
        or team_b["security_profile"] == "Strong Ball Security"
    ):
        print(
            "- Late-game possessions may favor the team that protects the ball and creates organized looks under pressure."
        )
    else:
        print(
            "- Late-game execution could become volatile if pressure, rushed decisions, or difficult shot creation increase."
        )


team_a = get_team(TEAM_A)
team_b = get_team(TEAM_B)

label = determine_game_label(team_a, team_b)

print("\nGAME FLOW / MATCHUP ENVIRONMENT ENGINE")
print("=" * 70)

print(f"\n{TEAM_A} vs {TEAM_B}")
print("=" * 70)

print_team_style(TEAM_A, team_a)
print_team_style(TEAM_B, team_b)

print("\nFINAL GAME LABEL")
print("-" * 50)
print(label)

print("\nPRESSURE POINTS")
print("-" * 50)

print(f"\n{TEAM_A} pressure points:")
for point in pressure_points(TEAM_A, TEAM_B, team_a, team_b):
    print(f"- {point}")

print(f"\n{TEAM_B} pressure points:")
for point in pressure_points(TEAM_B, TEAM_A, team_b, team_a):
    print(f"- {point}")

print("\nCOUNTER CHAINS")
print("-" * 50)

print(f"\n{TEAM_A} counters:")
for counter in counter_chains(TEAM_A, TEAM_B, team_a, team_b):
    print(f"- {counter}")

print(f"\n{TEAM_B} counters:")
for counter in counter_chains(TEAM_B, TEAM_A, team_b, team_a):
    print(f"- {counter}")

print("\nSWING FACTORS")
print("-" * 50)
for factor in swing_factors(TEAM_A, TEAM_B, team_a, team_b):
    print(f"- {factor}")

print("\nFAILURE CONDITIONS")
print("-" * 50)

print(f"\n{TEAM_A} failure conditions:")
for failure in failure_conditions(TEAM_A, TEAM_B, team_a, team_b):
    print(f"- {failure}")

print(f"\n{TEAM_B} failure conditions:")
for failure in failure_conditions(TEAM_B, TEAM_A, team_b, team_a):
    print(f"- {failure}")

game_phase_projection(TEAM_A, TEAM_B, team_a, team_b)

print("\nGame flow report generated successfully.")