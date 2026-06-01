import pandas as pd

# Load team style classifications
df = pd.read_csv("../outputs/team_style_classifications.csv")

# Select teams
TEAM_A = "Seattle Storm"
TEAM_B = "Portland Fire"

team_a = df[df["team"] == TEAM_A].iloc[0]
team_b = df[df["team"] == TEAM_B].iloc[0]

print("\nSTYLE MATCHUP ENGINE")
print("=" * 60)

print(f"\n{TEAM_A} vs {TEAM_B}")
print("=" * 60)

# Display team identities
print(f"\n{TEAM_A} IDENTITY")
print("-" * 40)

print(f"Tempo Style: {team_a['tempo_style']}")
print(f"Shot Profile: {team_a['shot_profile']}")
print(f"Offensive Style: {team_a['flow_profile']}")
print(f"Defense Style: {team_a['defense_profile']}")
print(f"Offensive Identity: {team_a['offense_profile']}")

print(f"\n{TEAM_B} IDENTITY")
print("-" * 40)

print(f"Tempo Style: {team_b['tempo_style']}")
print(f"Shot Profile: {team_b['shot_profile']}")
print(f"Offensive Style: {team_b['flow_profile']}")
print(f"Defense Style: {team_b['defense_profile']}")
print(f"Offensive Identity: {team_b['offense_profile']}")

print("\nTACTICAL CONSEQUENCES")
print("-" * 40)

# TEMPO INTERACTION
if (
    team_a["tempo_style"] == "Fast Tempo"
    and team_b["tempo_style"] != "Fast Tempo"
):
    print(
        f"{TEAM_A}'s pace may pressure "
        f"{TEAM_B} into earlier defensive rotations "
        f"before their half-court defense becomes organized."
    )

elif (
    team_b["tempo_style"] == "Fast Tempo"
    and team_a["tempo_style"] != "Fast Tempo"
):
    print(
        f"{TEAM_B}'s transition pace may increase "
        f"possession volume and stress "
        f"{TEAM_A}'s defensive organization."
    )

else:
    print(
        "Both teams operate in relatively similar "
        "tempo environments."
    )

# SHOT PROFILE INTERACTION
if (
    team_a["shot_profile"] == "High Value Shot Creation"
    and team_b["defense_profile"] != "Aggressive Defensive Pressure"
):
    print(
        f"{TEAM_A}'s shot creation profile may generate "
        f"efficient scoring opportunities if "
        f"{TEAM_B} cannot disrupt early actions."
    )

if (
    team_b["shot_profile"] == "High Value Shot Creation"
    and team_a["defense_profile"] != "Aggressive Defensive Pressure"
):
    print(
        f"{TEAM_B}'s spacing and scoring environment "
        f"may challenge {TEAM_A}'s defensive containment."
    )

# OFFENSIVE FLOW INTERACTION
if (
    team_a["flow_profile"] == "Connected Offensive Flow"
    and team_b["defense_profile"] == "Aggressive Defensive Pressure"
):
    print(
        f"{TEAM_B}'s defensive activity may attempt to "
        f"disrupt {TEAM_A}'s ball movement rhythm."
    )

if (
    team_b["flow_profile"] == "Connected Offensive Flow"
    and team_a["defense_profile"] == "Aggressive Defensive Pressure"
):
    print(
        f"{TEAM_A}'s pressure defense could challenge "
        f"{TEAM_B}'s offensive timing and initiation."
    )

# BALL SECURITY INTERACTION
if (
    team_a["security_profile"] == "Turnover Vulnerable"
    and team_b["defense_profile"] == "Aggressive Defensive Pressure"
):
    print(
        f"{TEAM_A} may struggle with live-ball turnovers "
        f"against defensive pressure."
    )

if (
    team_b["security_profile"] == "Turnover Vulnerable"
    and team_a["defense_profile"] == "Aggressive Defensive Pressure"
):
    print(
        f"{TEAM_B} may face decision-making pressure "
        f"against aggressive perimeter activity."
    )

print("\nKEY MATCHUP SWING")
print("-" * 40)

print(
    "The outcome of this matchup may depend on "
    "which team better imposes its preferred "
    "tempo, offensive rhythm, and defensive pressure."
)

print("\nStyle matchup analysis completed successfully.")