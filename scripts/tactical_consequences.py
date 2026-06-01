import pandas as pd

# Load team style classifications
df = pd.read_csv("../outputs/team_style_classifications.csv")

# Select teams
TEAM_A = "Dallas Wings"
TEAM_B = "Indiana Fever"

team_a = df[df["team"] == TEAM_A].iloc[0]
team_b = df[df["team"] == TEAM_B].iloc[0]


def tempo_consequence(team, opponent, tempo_style):
    if tempo_style == "Fast Tempo":
        return (
            f"{team}'s fast tempo can create early-clock pressure, "
            f"forcing {opponent} to get matched up quickly in transition."
        )
    elif tempo_style == "Controlled Tempo":
        return (
            f"{team}'s controlled tempo can reduce chaos, limit transition chances, "
            f"and force {opponent} to defend longer half-court possessions."
        )
    else:
        return (
            f"{team}'s balanced tempo allows them to adjust between transition "
            f"opportunities and half-court execution."
        )


def shot_profile_consequence(team, opponent, shot_profile):
    if shot_profile == "High Value Shot Creation":
        return (
            f"{team}'s high-value shot creation can stress {opponent}'s defensive rotations "
            f"by generating threes, rim pressure, and free-throw opportunities."
        )
    elif shot_profile == "Difficult Shot Environment":
        return (
            f"{team} may struggle to create clean scoring chances, which allows {opponent} "
            f"to stay home defensively and avoid unnecessary rotations."
        )
    else:
        return (
            f"{team}'s balanced shot profile gives them multiple ways to score, "
            f"but they still need to consistently create efficient looks."
        )


def flow_consequence(team, opponent, flow_profile):
    if flow_profile == "Connected Offensive Flow":
        return (
            f"{team}'s connected offensive flow can force {opponent} into repeated closeouts, "
            f"help rotations, and communication stress."
        )
    elif flow_profile == "Stagnant Offensive Flow":
        return (
            f"{team}'s stagnant offensive flow may make them easier to scout, allowing "
            f"{opponent} to load up on primary actions."
        )
    else:
        return (
            f"{team}'s moderate ball movement suggests they can create rhythm, "
            f"but may still rely on individual shot creation in key moments."
        )


def pressure_consequence(team, opponent, defense_profile):
    if defense_profile == "Aggressive Defensive Pressure":
        return (
            f"{team}'s aggressive defensive pressure can speed up {opponent}'s decisions, "
            f"create live-ball turnovers, and trigger transition offense."
        )
    elif defense_profile == "Low Disruption Defense":
        return (
            f"{team}'s low disruption defense may allow {opponent} to enter actions cleanly "
            f"and maintain offensive rhythm."
        )
    else:
        return (
            f"{team}'s active defensive presence can bother possessions without fully "
            f"overextending defensively."
        )


def counter_note(team, opponent, defense_profile, security_profile):
    if defense_profile == "Aggressive Defensive Pressure" and security_profile == "Turnover Vulnerable":
        return (
            f"Key counter for {opponent}: use secondary ball handlers, quick outlets, "
            f"and simple reads to avoid live-ball turnovers."
        )
    elif defense_profile == "Aggressive Defensive Pressure":
        return (
            f"Key counter for {opponent}: stay spaced, avoid rushed passes, "
            f"and punish pressure with quick advantage reads."
        )
    else:
        return (
            f"Key counter for {opponent}: force {team} into longer defensive possessions "
            f"and test their discipline over multiple actions."
        )


print("\nTACTICAL CONSEQUENCES REPORT")
print("=" * 60)

print(f"\n{TEAM_A} vs {TEAM_B}")
print("=" * 60)

print(f"\n{TEAM_A} Tactical Profile")
print("-" * 40)
print(tempo_consequence(TEAM_A, TEAM_B, team_a["tempo_style"]))
print(shot_profile_consequence(TEAM_A, TEAM_B, team_a["shot_profile"]))
print(flow_consequence(TEAM_A, TEAM_B, team_a["flow_profile"]))
print(pressure_consequence(TEAM_A, TEAM_B, team_a["defense_profile"]))

print(f"\n{TEAM_B} Tactical Profile")
print("-" * 40)
print(tempo_consequence(TEAM_B, TEAM_A, team_b["tempo_style"]))
print(shot_profile_consequence(TEAM_B, TEAM_A, team_b["shot_profile"]))
print(flow_consequence(TEAM_B, TEAM_A, team_b["flow_profile"]))
print(pressure_consequence(TEAM_B, TEAM_A, team_b["defense_profile"]))

print("\nCounters / Adjustment Notes")
print("-" * 40)
print(counter_note(TEAM_A, TEAM_B, team_a["defense_profile"], team_b["security_profile"]))
print(counter_note(TEAM_B, TEAM_A, team_b["defense_profile"], team_a["security_profile"]))

print("\nKey Matchup Swing")
print("-" * 40)
print(
    f"This matchup should be evaluated by which team better imposes its tempo, "
    f"protects possessions, and forces the opponent into lower-quality decision-making."
)

print("\nTactical consequence report generated successfully.")