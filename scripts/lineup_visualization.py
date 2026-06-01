import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PLAYER_STATS_FILE = BASE_DIR / "data" / "player_box_scores.csv"
STARTER_FILE = BASE_DIR / "data" / "starter_reference.csv"


def clean_name(name):
    return str(name).strip()


def name_matches(rotowire_name, full_name):
    rotowire_name = clean_name(rotowire_name)
    full_name = clean_name(full_name)

    if rotowire_name == full_name:
        return True

    # Match abbreviated names like "K. Mitchell" to "Kelsey Mitchell"
    if "." in rotowire_name:
        parts = rotowire_name.split()
        if len(parts) >= 2:
            first_initial = parts[0].replace(".", "")
            last_name = parts[-1]

            full_parts = full_name.split()
            if len(full_parts) >= 2:
                return (
                    full_parts[0].startswith(first_initial)
                    and full_parts[-1] == last_name
                )

    return False


def load_data():
    player_df = pd.read_csv(PLAYER_STATS_FILE)
    starter_df = pd.read_csv(STARTER_FILE)

    player_df = player_df.rename(columns={
        "player": "player_name",
        "min": "MIN",
        "pts": "PTS",
        "reb": "REB",
        "ast": "AST",
    })

    print("Columns:", list(player_df.columns))

    return player_df, starter_df

def choose_team(teams):
    print("\nAvailable teams:")
    for team in teams:
        print(f"- {team}")

    return input("\nEnter team name: ").strip()


def get_team_starters(team_name, starter_df):
    row = starter_df[starter_df["team"] == team_name]

    if row.empty:
        return []

    return row.iloc[0][
        ["starter_1", "starter_2", "starter_3", "starter_4", "starter_5"]
    ].tolist()


def filter_to_starters(team_df, starter_names):
    matched_rows = []
    missing_starters = []

    for starter in starter_names:
        match = team_df[
            team_df["player_name"].apply(lambda x: name_matches(starter, x))
        ]

        if not match.empty:
            matched_rows.append(match.iloc[0])
        else:
            missing_starters.append(starter)

    if matched_rows:
        lineup_df = pd.DataFrame(matched_rows)
    else:
        lineup_df = pd.DataFrame()

    return lineup_df, missing_starters


def create_lineup_profile(team_name, player_df, starter_df):
    team_df = player_df[player_df["team"] == team_name].copy()

    if team_df.empty:
        print(f"\nNo player data found for {team_name}.")
        return

    starter_names = get_team_starters(team_name, starter_df)

    if not starter_names:
        print(f"\nNo RotoWire starters found for {team_name}. Using top 5 by minutes.")
        lineup_df = team_df.sort_values("MIN", ascending=False).head(5)
        missing_starters = []
    else:
        lineup_df, missing_starters = filter_to_starters(team_df, starter_names)

        if lineup_df.empty:
            print(f"\nNo starter matches found for {team_name}. Using top 5 by minutes.")
            lineup_df = team_df.sort_values("MIN", ascending=False).head(5)

    print("\nPROJECTED STARTERS USED")
    print("---------------------------------------------")
    for _, player in lineup_df.iterrows():
        print(
            f"- {player['player_name']} | {player['position']} | "
            f"{player['PTS']} PTS | {player['AST']} AST | {player['REB']} REB"
        )

    if missing_starters:
        print("\nLINEUP WARNING")
        print("---------------------------------------------")
        print("These RotoWire starters were not found in your player stats file:")
        for name in missing_starters:
            print(f"- {name}")

    scoring = lineup_df["PTS"].mean()
    playmaking = lineup_df["AST"].mean()
    rebounding = lineup_df["REB"].mean()

    categories = ["Scoring", "Playmaking", "Rebounding"]
    values = [scoring, playmaking, rebounding]

    plt.figure(figsize=(7, 5))
    plt.bar(categories, values)
    plt.title(f"{team_name} Starting Lineup Profile")
    plt.xlabel("Categories")
    plt.ylabel("Average Per Starter")
    plt.tight_layout()
    plt.show()


def main():
    player_df, starter_df = load_data()

    teams = sorted(player_df["team"].dropna().unique())
    team_name = choose_team(teams)

    create_lineup_profile(team_name, player_df, starter_df)


if __name__ == "__main__":
    main()