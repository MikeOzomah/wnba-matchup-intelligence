import pandas as pd
from scripts.name_resolution import resolve_name
from scripts.matchup_engine import (
    build_team_profiles,
    build_player_profiles,
    load_player_stats,
    load_starters,
)
from scripts.player_matchup_engine import classify_archetypes
from scripts.lineup_ecosystem_engine import generate_lineup_insights

# Load data once for efficiency
PLAYER_STATS = load_player_stats()
STARTER_REFERENCE = load_starters()
PLAYER_PROFILES = build_player_profiles(PLAYER_STATS)
TEAM_PROFILES = build_team_profiles(PLAYER_STATS)

TEAM_LIST = TEAM_PROFILES['team'].dropna().unique().tolist()
PLAYER_LIST = PLAYER_PROFILES['player_name'].dropna().unique().tolist()


def get_team_profile(team_name):
    result = resolve_name(team_name, TEAM_LIST)
    response = {"data": None, "summary": None, "confidence": 0, "warning": None}
    if result["match"]:
        row = TEAM_PROFILES[TEAM_PROFILES["team"] == result["match"]]
        if not row.empty:
            row = row.iloc[0]
            games_played = row.get("games_played", 0)
            confidence = min(1.0, games_played / 10) if games_played else 0
            summary = f"{result['match']} averages {row['points_per_game']:.1f} PPG, {row['rebounds_per_game']:.1f} RPG, {row['assists_per_game']:.1f} APG."
            response.update({
                "data": row.to_dict(),
                "summary": summary,
                "confidence": confidence,
                "warning": result["warning"]
            })
        else:
            response["warning"] = f"No data found for team: {result['match']}"
    else:
        response["warning"] = result["warning"] or "Team not found."
    return response


def get_player_profile(player_name):
    result = resolve_name(player_name, PLAYER_LIST)
    response = {"data": None, "summary": None, "confidence": 0, "warning": None}
    if result["match"]:
        row = PLAYER_PROFILES[PLAYER_PROFILES["player_name"] == result["match"]]
        if not row.empty:
            row = row.iloc[0]
            games_played = row.get("games_played", 0)
            confidence = min(1.0, games_played / 10) if games_played else 0
            archetypes = classify_archetypes(row)
            summary = f"{result['match']} profile: {', '.join(archetypes)}."
            response.update({
                "data": row.to_dict(),
                "summary": summary,
                "confidence": confidence,
                "warning": result["warning"]
            })
        else:
            response["warning"] = f"No data found for player: {result['match']}"
    else:
        response["warning"] = result["warning"] or "Player not found."
    return response


def get_matchup_report(team_a, team_b):
    team_a_result = resolve_name(team_a, TEAM_LIST)
    team_b_result = resolve_name(team_b, TEAM_LIST)
    response = {"data": None, "summary": None, "confidence": 0, "warning": None}
    warnings = []
    if not team_a_result["match"]:
        warnings.append(team_a_result["warning"] or f"Team not found: {team_a}")
    if not team_b_result["match"]:
        warnings.append(team_b_result["warning"] or f"Team not found: {team_b}")
    if warnings:
        response["warning"] = "; ".join(warnings)
        return response
    row_a = TEAM_PROFILES[TEAM_PROFILES["team"] == team_a_result["match"]]
    row_b = TEAM_PROFILES[TEAM_PROFILES["team"] == team_b_result["match"]]
    if row_a.empty or row_b.empty:
        response["warning"] = "Missing data for one or both teams."
        return response
    row_a = row_a.iloc[0]
    row_b = row_b.iloc[0]
    games_played = min(row_a.get("games_played", 0), row_b.get("games_played", 0))
    confidence = min(1.0, games_played / 10) if games_played else 0
    summary = f"Matchup: {team_a_result['match']} vs {team_b_result['match']}. "
    summary += f"{team_a_result['match']} averages {row_a['points_per_game']:.1f} PPG, {team_b_result['match']} averages {row_b['points_per_game']:.1f} PPG."
    data = {
        "team_a": row_a.to_dict(),
        "team_b": row_b.to_dict(),
        "insights": []
    }
    # Use matchup_engine's insight generator
    from scripts.matchup_engine import generate_matchup_insights
    data["insights"] = generate_matchup_insights(team_a_result["match"], team_b_result["match"], row_a, row_b)
    response.update({
        "data": data,
        "summary": summary,
        "confidence": confidence,
        "warning": None
    })
    return response


def get_lineup_analysis(team_name):
    result = resolve_name(team_name, TEAM_LIST)
    response = {"data": None, "summary": None, "confidence": 0, "warning": None}
    if not result["match"]:
        response["warning"] = result["warning"] or "Team not found."
        return response
    team_players = PLAYER_PROFILES[PLAYER_PROFILES["team"] == result["match"]]
    if team_players.empty:
        response["warning"] = f"No player data for team: {result['match']}"
        return response
    lineup, missing, warnings = get_lineup(team_players, result["match"], STARTER_REFERENCE)
    profile = calculate_lineup_profile(lineup)
    context = generate_lineup_context(result["match"], profile)
    confidence = min(1.0, len(lineup) / 5) if len(lineup) else 0
    summary = f"Projected lineup for {result['match']}: {', '.join(lineup['player_name']) if not lineup.empty else 'N/A'}. "
    summary += " ".join(context)
    warn = warnings if warnings else None
    response.update({
        "data": {
            "lineup": lineup.to_dict(orient="records"),
            "profile": profile,
            "context": context,
            "missing": missing
        },
        "summary": summary,
        "confidence": confidence,
        "warning": warn
    })
    return response


def get_team_style(team_name):
    result = resolve_name(team_name, TEAM_LIST)
    response = {"data": None, "summary": None, "confidence": 0, "warning": None}
    if not result["match"]:
        response["warning"] = result["warning"] or "Team not found."
        return response
    # Try to load team style from outputs/team_style_classifications.csv
    try:
        style_df = pd.read_csv("outputs/team_style_classifications.csv")
        row = style_df[style_df["team"] == result["match"]]
        if not row.empty:
            row = row.iloc[0]
            confidence = 1.0
            summary = f"{result['match']} style: {row['style']}"
            response.update({
                "data": row.to_dict(),
                "summary": summary,
                "confidence": confidence,
                "warning": result["warning"]
            })
        else:
            response["warning"] = f"No style data for team: {result['match']}"
    except Exception as e:
        response["warning"] = f"Error loading style data: {e}"
    return response
