import pandas as pd
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent

PLAYER_STATS_FILE = BASE_DIR / "data" / "player_box_scores.csv"
STARTER_FILE = BASE_DIR / "data" / "starter_reference.csv"


def clean_name(name):
    return str(name).strip()


def name_matches(input_name, full_name):
    input_name = clean_name(input_name)
    full_name = clean_name(full_name)

    if input_name.lower() == full_name.lower():
        return True

    if "." in input_name:
        input_parts = input_name.split()
        full_parts = full_name.split()

        if len(input_parts) >= 2 and len(full_parts) >= 2:
            input_initial = input_parts[0].replace(".", "").lower()
            input_last = input_parts[-1].lower()

            return (
                full_parts[0].lower().startswith(input_initial)
                and full_parts[-1].lower() == input_last
            )

    return False


def load_player_stats():
    df = pd.read_csv(PLAYER_STATS_FILE)

    column_map = {
        "player": "player_name",
        "pts": "PTS",
        "reb": "REB",
        "ast": "AST",
        "stl": "STL",
        "blk": "BLK",
        "min": "MIN",
    }

    df = df.rename(columns={col: column_map[col] for col in df.columns if col in column_map})

    for col in ["MIN", "PTS", "REB", "AST", "STL", "BLK"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df[df["season_phase"].astype(str).str.lower().str.contains("regular")].copy()

    return df


def load_starters():
    if not STARTER_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(STARTER_FILE)


def build_player_profiles(raw_df):
    return raw_df.groupby(
        ["team", "player_name", "position"],
        as_index=False
    ).agg({
        "MIN": "mean",
        "PTS": "mean",
        "REB": "mean",
        "AST": "mean",
        "STL": "mean",
        "BLK": "mean",
    })


def build_team_profiles(raw_df):
    team_totals = raw_df.groupby(["team", "game_id"], as_index=False).agg({
        "PTS": "sum",
        "REB": "sum",
        "AST": "sum",
        "STL": "sum",
        "BLK": "sum",
    })

    team_profiles = team_totals.groupby("team", as_index=False).agg({
        "PTS": "mean",
        "REB": "mean",
        "AST": "mean",
        "STL": "mean",
        "BLK": "mean",
        "game_id": "nunique",
    })

    team_profiles = team_profiles.rename(columns={
        "PTS": "points_per_game",
        "REB": "rebounds_per_game",
        "AST": "assists_per_game",
        "STL": "steals_per_game",
        "BLK": "blocks_per_game",
        "game_id": "games_played",
    })

    team_profiles["defensive_activity"] = (
        team_profiles["steals_per_game"] + team_profiles["blocks_per_game"]
    )

    return team_profiles


def get_lineup(team_players, team_name, starter_reference):
    row = starter_reference[starter_reference["team"] == team_name]

    if row.empty:
        return team_players.sort_values("MIN", ascending=False).head(5).copy(), []

    starter_names = row.iloc[0][
        ["starter_1", "starter_2", "starter_3", "starter_4", "starter_5"]
    ].tolist()

    matched_rows = []
    missing = []

    for name in starter_names:
        match = team_players[
            team_players["player_name"].apply(lambda x: name_matches(name, x))
        ]

        if not match.empty:
            matched_rows.append(match.iloc[0])
        else:
            missing.append(name)

    if matched_rows:
        return pd.DataFrame(matched_rows), missing

    return team_players.sort_values("MIN", ascending=False).head(5).copy(), missing


def calculate_lineup_profile(lineup_df):
    return {
        "scoring": float(lineup_df["PTS"].mean()),
        "playmaking": float(lineup_df["AST"].mean()),
        "rebounding": float(lineup_df["REB"].mean()),
        "defensive_activity": float(lineup_df["STL"].mean() + lineup_df["BLK"].mean()),
    }


def compare_team_metric(label, team_a, team_b, value_a, value_b, threshold):
    if abs(value_a - value_b) < threshold:
        return {"metric": label, "advantage": "Even"}

    if value_a > value_b:
        return {"metric": label, "advantage": team_a}
    else:
        return {"metric": label, "advantage": team_b}


def generate_matchup_insights(team_a, team_b, row_a, row_b):
    insights = []

    if row_a["points_per_game"] > row_b["points_per_game"] + 5:
        insights.append(f"{team_a} has the stronger team scoring profile.")
    elif row_b["points_per_game"] > row_a["points_per_game"] + 5:
        insights.append(f"{team_b} has the stronger team scoring profile.")

    if row_a["rebounds_per_game"] > row_b["rebounds_per_game"] + 4:
        insights.append(f"{team_a} has the rebounding edge, which can create extra possessions.")
    elif row_b["rebounds_per_game"] > row_a["rebounds_per_game"] + 4:
        insights.append(f"{team_b} has the rebounding edge, which can create extra possessions.")

    if row_a["assists_per_game"] > row_b["assists_per_game"] + 3:
        insights.append(f"{team_a} shows stronger team playmaking and ball movement.")
    elif row_b["assists_per_game"] > row_a["assists_per_game"] + 3:
        insights.append(f"{team_b} shows stronger team playmaking and ball movement.")

    if row_a["defensive_activity"] > row_b["defensive_activity"] + 2:
        insights.append(f"{team_a} creates more defensive events through steals and blocks.")
    elif row_b["defensive_activity"] > row_a["defensive_activity"] + 2:
        insights.append(f"{team_b} creates more defensive events through steals and blocks.")

    if not insights:
        insights.append("This matchup looks close by team averages, so execution, turnovers, and shot quality may decide it.")

    return insights


def generate_lineup_context(team_name, lineup_profile):
    context = []

    if lineup_profile["scoring"] >= 12:
        context.append(f"{team_name}'s projected lineup has strong individual scoring punch.")
    if lineup_profile["rebounding"] >= 6:
        context.append(f"{team_name}'s projected lineup has strong rebounding presence.")
    if lineup_profile["playmaking"] < 3:
        context.append(f"{team_name}'s projected lineup may rely more on individual creation than flow.")
    if lineup_profile["defensive_activity"] >= 2:
        context.append(f"{team_name}'s projected lineup has disruptive defensive activity.")

    return context


def get_report(matchup_input: str) -> Dict[str, Any]:
    """
    Generate a matchup report from a string input in format: 'Team A vs Team B'
    
    Args:
        matchup_input: String in format 'Team A vs Team B'
        
    Returns:
        Dictionary containing matchup analysis
    """
    # Parse input
    parts = [p.strip() for p in matchup_input.split(" vs ")]
    if len(parts) != 2:
        return {"error": "Invalid format. Use 'Team A vs Team B'"}
    
    team_a, team_b = parts
    
    # Load data
    try:
        raw_df = load_player_stats()
        starter_reference = load_starters()
        
        player_profiles = build_player_profiles(raw_df)
        team_profiles = build_team_profiles(raw_df)
        
        # Get team data
        row_a = team_profiles[team_profiles["team"] == team_a]
        row_b = team_profiles[team_profiles["team"] == team_b]
        
        if row_a.empty or row_b.empty:
            available_teams = sorted(team_profiles["team"].dropna().unique().tolist())
            return {
                "error": f"Team not found. Available teams: {available_teams}",
                "available_teams": available_teams
            }
        
        row_a = row_a.iloc[0]
        row_b = row_b.iloc[0]
        
        # Get player profiles for each team
        team_a_players = player_profiles[player_profiles["team"] == team_a].copy()
        team_b_players = player_profiles[player_profiles["team"] == team_b].copy()
        
        # Get lineups
        lineup_a, missing_a = get_lineup(team_a_players, team_a, starter_reference)
        lineup_b, missing_b = get_lineup(team_b_players, team_b, starter_reference)
        
        # Calculate lineup profiles
        lineup_profile_a = calculate_lineup_profile(lineup_a)
        lineup_profile_b = calculate_lineup_profile(lineup_b)
        
        # Build report
        report = {
            "matchup": f"{team_a} vs {team_b}",
            "team_stats": {
                team_a: {
                    "points_per_game": float(row_a["points_per_game"]),
                    "rebounds_per_game": float(row_a["rebounds_per_game"]),
                    "assists_per_game": float(row_a["assists_per_game"]),
                    "steals_per_game": float(row_a["steals_per_game"]),
                    "blocks_per_game": float(row_a["blocks_per_game"]),
                    "games_played": int(row_a["games_played"])
                },
                team_b: {
                    "points_per_game": float(row_b["points_per_game"]),
                    "rebounds_per_game": float(row_b["rebounds_per_game"]),
                    "assists_per_game": float(row_b["assists_per_game"]),
                    "steals_per_game": float(row_b["steals_per_game"]),
                    "blocks_per_game": float(row_b["blocks_per_game"]),
                    "games_played": int(row_b["games_played"])
                }
            },
            "team_advantages": [
                compare_team_metric("Scoring", team_a, team_b, row_a["points_per_game"], row_b["points_per_game"], 3),
                compare_team_metric("Rebounding", team_a, team_b, row_a["rebounds_per_game"], row_b["rebounds_per_game"], 2),
                compare_team_metric("Playmaking", team_a, team_b, row_a["assists_per_game"], row_b["assists_per_game"], 2),
                compare_team_metric("Defensive Activity", team_a, team_b, row_a["defensive_activity"], row_b["defensive_activity"], 1),
            ],
            "matchup_insights": generate_matchup_insights(team_a, team_b, row_a, row_b),
            "lineups": {
                team_a: [
                    {
                        "player": str(player["player_name"]),
                        "position": str(player["position"]),
                        "pts": float(player["PTS"]),
                        "ast": float(player["AST"]),
                        "reb": float(player["REB"]),
                        "stl": float(player["STL"]),
                        "blk": float(player["BLK"])
                    }
                    for _, player in lineup_a.iterrows()
                ],
                team_b: [
                    {
                        "player": str(player["player_name"]),
                        "position": str(player["position"]),
                        "pts": float(player["PTS"]),
                        "ast": float(player["AST"]),
                        "reb": float(player["REB"]),
                        "stl": float(player["STL"]),
                        "blk": float(player["BLK"])
                    }
                    for _, player in lineup_b.iterrows()
                ]
            },
            "lineup_profiles": {
                team_a: lineup_profile_a,
                team_b: lineup_profile_b
            },
            "lineup_context": {
                team_a: generate_lineup_context(team_a, lineup_profile_a),
                team_b: generate_lineup_context(team_b, lineup_profile_b)
            },
            "warnings": {
                team_a: missing_a,
                team_b: missing_b
            }
        }
        
        return report
        
    except Exception as e:
        return {"error": str(e)}
