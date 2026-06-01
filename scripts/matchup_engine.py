
import pandas as pd
from pathlib import Path
from scripts.name_resolution import resolve_name

BASE_DIR = Path(__file__).resolve().parent.parent

PLAYER_STATS_FILE = BASE_DIR / "data" / "player_box_scores.csv"
STARTER_FILE = BASE_DIR / "data" / "starter_reference.csv"


def name_matches(input_name, full_name):
    # Deprecated: replaced by resolve_name
    raise NotImplementedError("Use resolve_name from name_resolution.py instead.")


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


    row = starter_reference[starter_reference["team"] == team_name]
    if row.empty:
        return team_players.sort_values("MIN", ascending=False).head(5).copy(), []

    starter_names = row.iloc[0][["starter_1", "starter_2", "starter_3", "starter_4", "starter_5"]].tolist()
    matched_rows = []
    missing = []
    warnings = []
    player_list = team_players["player_name"].tolist()
    for name in starter_names:
        result = resolve_name(name, player_list)
        if result["match"]:
            matched_rows.append(team_players[team_players["player_name"] == result["match"]].iloc[0])
            if result["warning"]:
                warnings.append(result["warning"])
        elif result["matches"]:
            warnings.append(result["warning"])
            missing.append(name)
        else:
            warnings.append(result["warning"])
            missing.append(name)
    if matched_rows:
        return pd.DataFrame(matched_rows), missing, warnings
    return team_players.sort_values("MIN", ascending=False).head(5).copy(), missing, warnings


def calculate_lineup_profile(lineup_df):
    return {
        "scoring": lineup_df["PTS"].mean(),
        "playmaking": lineup_df["AST"].mean(),
        "rebounding": lineup_df["REB"].mean(),
        "defensive_activity": lineup_df["STL"].mean() + lineup_df["BLK"].mean(),
    }


def print_lineup(team_name, lineup_df):
    print(f"\n{team_name} PROJECTED LINEUP CONTEXT")
    print("---------------------------------------------")

    for _, player in lineup_df.iterrows():
        print(
            f"- {player['player_name']} | {player['position']} | "
            f"{player['PTS']:.1f} PTS | {player['AST']:.1f} AST | "
            f"{player['REB']:.1f} REB | {player['STL']:.1f} STL | {player['BLK']:.1f} BLK"
        )


def compare_team_metric(label, team_a, team_b, value_a, value_b, threshold):
    if abs(value_a - value_b) < threshold:
        return f"- {label}: Even"

    if value_a > value_b:
        return f"- {label}: Advantage {team_a}"
    else:
        return f"- {label}: Advantage {team_b}"


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


def choose_team(teams, label):
    print(f"\nAvailable teams for {label}:")
    for team in teams:
        print(f"- {team}")

    return input(f"\nEnter {label} team exactly as shown: ").strip()


def main():
    raw_df = load_player_stats()
    starter_reference = load_starters()

    player_profiles = build_player_profiles(raw_df)
    team_profiles = build_team_profiles(raw_df)

    teams = sorted(team_profiles["team"].dropna().unique())

    team_a = choose_team(teams, "Team A")
    team_b = choose_team(teams, "Team B")

    row_a = team_profiles[team_profiles["team"] == team_a].iloc[0]
    row_b = team_profiles[team_profiles["team"] == team_b].iloc[0]

    team_a_players = player_profiles[player_profiles["team"] == team_a].copy()
    team_b_players = player_profiles[player_profiles["team"] == team_b].copy()

    lineup_a, missing_a, warnings_a = get_lineup(team_a_players, team_a, starter_reference)
    lineup_b, missing_b, warnings_b = get_lineup(team_b_players, team_b, starter_reference)

    lineup_profile_a = calculate_lineup_profile(lineup_a)
    lineup_profile_b = calculate_lineup_profile(lineup_b)

    print("\n" + "=" * 70)
    print("WNBA MATCHUP ENGINE")
    print("=" * 70)

    print(f"\nMatchup: {team_a} vs {team_b}")

    print("\nTEAM AVERAGE COMPARISON")
    print("---------------------------------------------")
    print(
        f"{team_a}: "
        f"{row_a['points_per_game']:.1f} PPG | "
        f"{row_a['rebounds_per_game']:.1f} RPG | "
        f"{row_a['assists_per_game']:.1f} APG | "
        f"{row_a['steals_per_game']:.1f} SPG | "
        f"{row_a['blocks_per_game']:.1f} BPG | "
        f"{int(row_a['games_played'])} GP"
    )
    print(
        f"{team_b}: "
        f"{row_b['points_per_game']:.1f} PPG | "
        f"{row_b['rebounds_per_game']:.1f} RPG | "
        f"{row_b['assists_per_game']:.1f} APG | "
        f"{row_b['steals_per_game']:.1f} SPG | "
        f"{row_b['blocks_per_game']:.1f} BPG | "
        f"{int(row_b['games_played'])} GP"
    )

    print("\nTEAM ADVANTAGES")
    print("---------------------------------------------")
    print(compare_team_metric("Scoring", team_a, team_b, row_a["points_per_game"], row_b["points_per_game"], 3))
    print(compare_team_metric("Rebounding", team_a, team_b, row_a["rebounds_per_game"], row_b["rebounds_per_game"], 2))
    print(compare_team_metric("Playmaking", team_a, team_b, row_a["assists_per_game"], row_b["assists_per_game"], 2))
    print(compare_team_metric("Defensive Activity", team_a, team_b, row_a["defensive_activity"], row_b["defensive_activity"], 1))

    print("\nMATCHUP INSIGHTS")
    print("---------------------------------------------")
    for insight in generate_matchup_insights(team_a, team_b, row_a, row_b):
        print(f"- {insight}")

    print_lineup(team_a, lineup_a)
    print_lineup(team_b, lineup_b)

    print("\nLINEUP CONTEXT")
    print("---------------------------------------------")
    for insight in generate_lineup_context(team_a, lineup_profile_a):
        print(f"- {insight}")
    for insight in generate_lineup_context(team_b, lineup_profile_b):
        print(f"- {insight}")

    if missing_a or missing_b or warnings_a or warnings_b:
        print("\nLINEUP WARNINGS")
        print("---------------------------------------------")
        if missing_a:
            print(f"{team_a} missing from player stats: {missing_a}")
        if missing_b:
            print(f"{team_b} missing from player stats: {missing_b}")
        for w in warnings_a:
            print(f"{team_a} warning: {w}")
        for w in warnings_b:
            print(f"{team_b} warning: {w}")


if __name__ == "__main__":
    main()