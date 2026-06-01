from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

players_df = pd.read_csv(
    BASE_DIR / "outputs" / "player_influence_profiles.csv"
)

teams_df = pd.read_csv(
    BASE_DIR / "outputs" / "team_style_classifications.csv"
)





import os
import pandas as pd
from name_resolution import resolve_name

PLAYER_A = "Alyssa Thomas"
PLAYER_B = "Kelsey Mitchell"

# Lazy-loaded dataframes
_players_df = None
_teams_df = None

def load_data():
    """
    Lazy-load and cache the player and team DataFrames. Uses project-root-relative paths.
    """
    global _players_df, _teams_df
    if _players_df is None or _teams_df is None:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        players_path = os.path.join(root, "outputs", "player_influence_profiles.csv")
        teams_path = os.path.join(root, "outputs", "team_style_classifications.csv")
        _players_df = pd.read_csv(players_path)
        _teams_df = pd.read_csv(teams_path)
    return _players_df, _teams_df

def get_player_row(player_name):
    players_df, _ = load_data()
    player_list = players_df["player"].tolist()
    result = resolve_name(player_name, player_list)
    if result["match"]:
        return players_df[players_df["player"] == result["match"]].iloc[0]
    print(f"\nPlayer not found: {player_name}")
    if result["warning"]:
        print(result["warning"])
    print("\nAvailable players:")
    print(players_df["player"].unique())
    raise SystemExit

def get_team_row(team_name):
    _, teams_df = load_data()
    team_list = teams_df["team"].tolist()
    result = resolve_name(team_name, team_list)
    if result["match"]:
        return teams_df[teams_df["team"] == result["match"]].iloc[0]
    print(f"\nTeam not found: {team_name}")
    if result["warning"]:
        print(result["warning"])
    print("\nAvailable teams:")
    print(teams_df["team"].unique())
    raise SystemExit

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
    if pts >= 20 and three_pa >= 5:
        archetypes.append("Perimeter Scoring Engine")
    elif pts >= 20 and fta >= 5 and reb >= 5:
        archetypes.append("Physical Scoring Engine")
    elif pts >= 15:
        archetypes.append("Primary Scorer")
    if three_pa >= 6:
        archetypes.append("High-Gravity Shooter")
    elif three_pa >= 3:
        archetypes.append("Floor Spacer")
    if ast >= 6:
        archetypes.append("Primary Playmaker")
    elif ast >= 3:
        archetypes.append("Secondary Creator")
    if fta >= 6 and reb >= 6 and three_pa < 3:
        archetypes.append("Interior Pressure Creator")
    elif fta >= 5:
        archetypes.append("Foul Pressure Creator")
    if reb >= 8:
        archetypes.append("Rebounding Anchor")
    elif reb >= 5:
        archetypes.append("Positive Rebounder")
    if stl >= 2:
        archetypes.append("Defensive Disruptor")
    if blk >= 2:
        archetypes.append("Rim Protector")
    if ast_to >= 2 and ast >= 3:
        archetypes.append("Decision Stabilizer")
    elif ast_to < 1 and ast >= 3:
        archetypes.append("Risk-Taking Creator")
    if not archetypes:
        archetypes.append("Role Contributor")
    return archetypes

def generate_archetype_summary(player, team, archetypes):
    lines = []
    if "Physical Scoring Engine" in archetypes:
        lines.append(
            f"{player} profiles as a physical scoring engine who can pressure the paint, draw contact, and create interior advantages."
        )
    if "Primary Playmaker" in archetypes:
        lines.append(
            f"{player} helps organize {team}'s offense through creation responsibility, passing volume, and tempo control."
        )
    if "High-Gravity Shooter" in archetypes:
        lines.append(
            f"{player}'s shooting volume creates gravity that can extend the defense and open driving lanes for teammates."
        )
    if "Interior Pressure Creator" in archetypes:
        lines.append(
            f"{player}'s interior pressure can force help rotations, collapse the defense, and create foul-risk situations."
        )
    if "Rebounding Anchor" in archetypes:
        lines.append(
            f"{player} influences possession control through rebounding and second-chance prevention or creation."
        )
    if "Defensive Disruptor" in archetypes:
        lines.append(
            f"{player} can create defensive disruption through activity, steals, and passing-lane pressure."
        )
    if "Decision Stabilizer" in archetypes:
        lines.append(
            f"{player}'s decision-making helps stabilize possessions and reduce chaotic offensive stretches."
        )
    if not lines:
        lines.append(
            f"{player} contributes within role responsibilities and should be evaluated by how well that role fits {team}'s style."
        )
    return lines

def generate_matchup_keys(player, opponent_team, archetypes, opponent_style):
    keys = []
    opponent_tempo = opponent_style["tempo_style"]
    opponent_defense = opponent_style["defense_profile"]
    opponent_shot = opponent_style["shot_profile"]
    if "Perimeter Scoring Engine" in archetypes or "High-Gravity Shooter" in archetypes:
        if opponent_defense == "Aggressive Defensive Pressure":
            keys.append(
                "Use off-ball movement, quick releases, and screen actions to create separation before pressure can load up."
            )
        else:
            keys.append(
                "Force long closeouts and use perimeter gravity to open driving lanes and secondary actions."
            )
    if "Primary Playmaker" in archetypes:
        if opponent_defense == "Aggressive Defensive Pressure":
            keys.append(
                "Protect initiation points by using early outlets, simple reads, and quick reversals against pressure."
            )
        else:
            keys.append(
                "Control tempo and repeatedly force the defense into rotations through ball screens, early-clock reads, and paint touches."
            )
    if "Interior Pressure Creator" in archetypes or "Physical Scoring Engine" in archetypes:
        keys.append(
            "Establish paint touches early to force help defense, create foul pressure, and open weak-side scoring opportunities."
        )
    if "Foul Pressure Creator" in archetypes:
        keys.append(
            "Attack gaps without forcing tough attempts; the goal is to create free throws and defensive foul pressure."
        )
    if "Rebounding Anchor" in archetypes or "Positive Rebounder" in archetypes:
        keys.append(
            "Control the possession battle through rebounding, especially when the opponent tries to speed the game up."
        )
    if "Decision Stabilizer" in archetypes:
        keys.append(
            "Use decision-making discipline to keep possessions organized when the matchup becomes chaotic."
        )
    if "Risk-Taking Creator" in archetypes:
        keys.append(
            "Avoid over-dribbling into pressure and trust secondary creators when the defense loads up."
        )
    if opponent_tempo == "Fast Tempo":
        keys.append(
            f"Limit live-ball mistakes because {opponent_team} can convert rushed possessions into transition pressure."
        )
    if opponent_tempo == "Controlled Tempo":
        keys.append(
            f"Stay efficient in half-court possessions because {opponent_team} may try to reduce pace and possession volume."
        )
    if opponent_shot == "High Value Shot Creation":
        keys.append(
            f"Match {opponent_team}'s shot quality by creating efficient looks instead of settling for low-value attempts."
        )
    if not keys:
        keys.append(
            "Stay within role, protect possessions, and create advantages that align with team style."
        )
    return keys

if __name__ == "__main__":
    # Example usage/demo code here
    pass
