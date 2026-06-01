
import pandas as pd
from pathlib import Path
from scripts.name_resolution import resolve_name

BASE_DIR = Path(__file__).resolve().parent.parent

PLAYER_STATS_FILE = BASE_DIR / "data" / "player_box_scores.csv"
STARTER_FILE = BASE_DIR / "data" / "starter_reference.csv"


def clean_name(name):
    return str(name).strip()


    # Deprecated: replaced by resolve_name
    raise NotImplementedError("Use resolve_name from name_resolution.py instead.")


def load_player_stats():
    if not PLAYER_STATS_FILE.exists():
        raise FileNotFoundError(f"Could not find {PLAYER_STATS_FILE}")

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

    required_columns = [
        "game_id",
        "date",
        "season_phase",
        "team",
        "opponent",
        "player_name",
        "position",
        "MIN",
        "PTS",
        "REB",
        "AST",
        "STL",
        "BLK",
    ]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Missing columns in player_box_scores.csv: {missing_columns}\n"
            f"Available columns: {df.columns.tolist()}"
        )

    for col in ["MIN", "PTS", "REB", "AST", "STL", "BLK"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df[
        df["season_phase"].astype(str).str.lower().str.contains("regular")
    ].copy()

    return df


def load_starter_reference():
    if not STARTER_FILE.exists():
        print("No starter_reference.csv found. Falling back to minutes/custom lineup only.")
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


    matched_rows = []
    missing = []
    warnings = []
    player_list = team_players["player_name"].tolist()
    for name in custom_names:
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
    return pd.DataFrame(), custom_names, warnings


    if starter_reference.empty:
        return team_players.sort_values("MIN", ascending=False).head(5).copy(), [], []

    team_starter_row = starter_reference[starter_reference["team"] == team_name]

    if team_starter_row.empty:
        return team_players.sort_values("MIN", ascending=False).head(5).copy(), [], []

    starter_names = team_starter_row.iloc[0][["starter_1", "starter_2", "starter_3", "starter_4", "starter_5"]].tolist()
    return get_custom_lineup(team_players, starter_names)


def calculate_lineup_profile(lineup_df):
    if lineup_df.empty:
        return {
            "scoring": 0,
            "playmaking": 0,
            "rebounding": 0,
            "defensive_activity": 0,
        }

    return {
        "scoring": lineup_df["PTS"].mean(),
        "playmaking": lineup_df["AST"].mean(),
        "rebounding": lineup_df["REB"].mean(),
        "defensive_activity": lineup_df["STL"].mean() + lineup_df["BLK"].mean(),
    }


def generate_lineup_insights(profile):
    insights = []

    scoring = profile["scoring"]
    playmaking = profile["playmaking"]
    rebounding = profile["rebounding"]
    defensive_activity = profile["defensive_activity"]

    if scoring >= 12:
        insights.append("High-scoring lineup -- this group has strong point production.")
    elif scoring >= 8:
        insights.append("Solid scoring lineup -- enough offensive firepower to stay competitive.")
    else:
        insights.append("Low-scoring lineup -- may need cleaner creation or stronger shot quality.")

    if playmaking >= 4:
        insights.append("Strong playmaking profile -- offense can flow through multiple passers.")
    elif playmaking >= 2:
        insights.append("Moderate playmaking -- likely depends on one or two main creators.")
    else:
        insights.append("Limited playmaking -- offense may become stagnant under pressure.")

    if rebounding >= 6:
        insights.append("Strong rebounding profile -- this lineup can control possessions.")
    elif rebounding >= 3:
        insights.append("Average rebounding profile -- not a major weakness, but not dominant.")
    else:
        insights.append("Weak rebounding profile -- vulnerable to second-chance points.")

    if defensive_activity >= 2:
        insights.append("Active defensive profile -- this group can create disruption through steals and blocks.")
    elif defensive_activity >= 1:
        insights.append("Moderate defensive activity -- some disruption, but not a clear defensive-pressure lineup.")
    else:
        insights.append("Low defensive activity -- this group may rely more on positioning than disruption.")

    if scoring >= 8 and playmaking < 3:
        insights.append("Scorer-heavy but creation-light -- this lineup may rely on individual shot-making.")

    if rebounding >= 6 and playmaking < 3:
        insights.append("Physical lineup, but not necessarily a smooth-flowing offensive group.")

    return insights


def print_player_line(player):
    print(
        f"- {player['player_name']} | {player['position']} | "
        f"{player['PTS']:.1f} PTS | {player['AST']:.1f} AST | "
        f"{player['REB']:.1f} REB | {player['STL']:.1f} STL | {player['BLK']:.1f} BLK"
    )


def analyze_lineup(team_name, lineup_df, missing_players, player_profiles, lineup_label):
    print("\n" + "=" * 70)
    print("LINEUP ECOSYSTEM ENGINE")
    print("=" * 70)

    print(f"\nTeam: {team_name}")
    print(f"Lineup Type: {lineup_label}")

    if lineup_df.empty:
        print("\nNo players found for this lineup.")
        return

    print("\nLINEUP PLAYERS")
    print("---------------------------------------------")

    for _, player in lineup_df.iterrows():
        print_player_line(player)

    if missing_players:
        print("\nLINEUP WARNING")
        print("---------------------------------------------")
        print("These players were not found in your player stats file:")
        for name in missing_players:
            print(f"- {name}")

    profile = calculate_lineup_profile(lineup_df)

    print("\nLINEUP PROFILE")
    print("---------------------------------------------")
    print(f"Scoring Average Per Player: {profile['scoring']:.2f}")
    print(f"Playmaking Average Per Player: {profile['playmaking']:.2f}")
    print(f"Rebounding Average Per Player: {profile['rebounding']:.2f}")
    print(f"Defensive Activity Per Player: {profile['defensive_activity']:.2f}")

    print("\nLINEUP INSIGHTS")
    print("---------------------------------------------")

    for insight in generate_lineup_insights(profile):
        print(f"- {insight}")

    top_rotation = player_profiles[player_profiles["team"] == team_name].sort_values(
        "MIN",
        ascending=False
    ).head(8)

    print("\nTOP ROTATION BY MINUTES")
    print("---------------------------------------------")

    for _, player in top_rotation.iterrows():
        print_player_line(player)


def choose_team(teams):
    print("\nAvailable teams:")
    for team in teams:
        print(f"- {team}")

    return input("\nEnter team name exactly as shown: ").strip()


def main():
    print("Looking for player stats at:", PLAYER_STATS_FILE)
    print("Looking for starters at:", STARTER_FILE)

    raw_player_stats = load_player_stats()
    starter_reference = load_starter_reference()

    if raw_player_stats.empty:
        print("\nNo regular-season player rows found.")
        return

    player_profiles = build_player_profiles(raw_player_stats)

    teams = sorted(player_profiles["team"].dropna().unique())

    team_name = choose_team(teams)

    team_players = player_profiles[player_profiles["team"] == team_name].copy()

    if team_players.empty:
        print(f"\nNo data found for {team_name}")
        return

    use_custom = input("\nUse custom lineup? yes/no: ").strip().lower()

    if use_custom in ["yes", "y"]:
        custom_input = input("\nEnter 5 players separated by commas: ").strip()

        custom_names = [
            name.strip()
            for name in custom_input.split(",")
            if name.strip()
        ]

        if len(custom_names) != 5:
            print("\nPlease enter exactly 5 players.")
            return

        lineup_df, missing_players = get_custom_lineup(team_players, custom_names)
        lineup_label = "Custom Lineup"

    else:
        lineup_df, missing_players = get_projected_starters(
            team_players,
            team_name,
            starter_reference
        )
        lineup_label = "RotoWire Projected Starters"

    analyze_lineup(
        team_name,
        lineup_df,
        missing_players,
        player_profiles,
        lineup_label,
    )


if __name__ == "__main__":
    main()