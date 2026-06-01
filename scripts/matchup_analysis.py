import pandas as pd

# Load defensive metrics dataset
df = pd.read_csv("../outputs/defensive_metrics.csv")

# Group team averages
team_profiles = df.groupby("team")[[
    "offensive_rating",
    "shot_value",
    "offensive_flow",
    "ball_security",
    "possessions",
    "defensive_pressure",
    "opponent_offensive_rating_allowed",
    "opponent_shot_value_allowed",
    "opponent_offensive_flow_allowed"
]].mean().round(3)

# Reset index
team_profiles = team_profiles.reset_index()

# Select matchup teams
TEAM_A = "Dallas Wings"
TEAM_B = "Indiana Fever"

team_a = team_profiles[
    team_profiles["team"] == TEAM_A
].iloc[0]

team_b = team_profiles[
    team_profiles["team"] == TEAM_B
].iloc[0]

print(f"\nMATCHUP ANALYSIS")
print("=" * 60)

print(f"\n{TEAM_A} vs {TEAM_B}")
print("=" * 60)

# Team A profile
print(f"\n{TEAM_A} PROFILE")
print("-" * 40)

print(f"Offensive Rating: {team_a['offensive_rating']}")
print(f"Shot Value: {team_a['shot_value']}")
print(f"Offensive Flow: {team_a['offensive_flow']}")
print(f"Ball Security: {team_a['ball_security']}")
print(f"Defensive Pressure: {team_a['defensive_pressure']}")

# Team B profile
print(f"\n{TEAM_B} PROFILE")
print("-" * 40)

print(f"Offensive Rating: {team_b['offensive_rating']}")
print(f"Shot Value: {team_b['shot_value']}")
print(f"Offensive Flow: {team_b['offensive_flow']}")
print(f"Ball Security: {team_b['ball_security']}")
print(f"Defensive Pressure: {team_b['defensive_pressure']}")

# Matchup interpretation
print("\nMATCHUP INTERACTION")
print("-" * 40)

# Tempo
if team_a["possessions"] > team_b["possessions"]:
    print(f"{TEAM_A} currently plays at a faster pace.")
else:
    print(f"{TEAM_B} currently plays at a faster pace.")

# Shot value interaction
if (
    team_a["shot_value"]
    > team_b["opponent_shot_value_allowed"]
):
    print(
        f"{TEAM_A}'s shot creation may challenge "
        f"{TEAM_B}'s defensive shot containment."
    )
else:
    print(
        f"{TEAM_B} may be able to limit "
        f"{TEAM_A}'s shot efficiency."
    )

if (
    team_b["shot_value"]
    > team_a["opponent_shot_value_allowed"]
):
    print(
        f"{TEAM_B}'s offensive shot profile may stress "
        f"{TEAM_A}'s defense."
    )
else:
    print(
        f"{TEAM_A} may effectively suppress "
        f"{TEAM_B}'s shot quality."
    )

# Offensive flow interaction
if (
    team_a["offensive_flow"]
    > team_b["opponent_offensive_flow_allowed"]
):
    print(
        f"{TEAM_A} may maintain strong offensive movement "
        f"against this defense."
    )
else:
    print(
        f"{TEAM_B} may disrupt "
        f"{TEAM_A}'s offensive rhythm."
    )

if (
    team_b["offensive_flow"]
    > team_a["opponent_offensive_flow_allowed"]
):
    print(
        f"{TEAM_B}'s offensive flow could pressure "
        f"{TEAM_A}'s rotations."
    )
else:
    print(
        f"{TEAM_A} may successfully slow "
        f"{TEAM_B}'s offensive flow."
    )

# Ball security vs pressure
if (
    team_a["ball_security"]
    < team_b["defensive_pressure"]
):
    print(
        f"{TEAM_A} could face turnover pressure "
        f"in this matchup."
    )

if (
    team_b["ball_security"]
    < team_a["defensive_pressure"]
):
    print(
        f"{TEAM_B} could face turnover pressure "
        f"in this matchup."
    )

# Strategic takeaway
print("\nSTRATEGIC TAKEAWAY")
print("-" * 40)

print(
    "This matchup projects as a stylistic battle "
    "between offensive efficiency, tempo control, "
    "and defensive disruption."
)

print(
    "The team that best controls possessions while "
    "maintaining offensive flow is more likely to "
    "generate sustainable scoring opportunities."
)