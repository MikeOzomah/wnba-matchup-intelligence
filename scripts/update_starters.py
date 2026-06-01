import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent.parent

URL = "https://www.rotowire.com/wnba/lineups.php"
OUTPUT_FILE = BASE_DIR / "data" / "starter_reference.csv"

TEAM_MAP = {
    "SEA": "Seattle Storm",
    "TOR": "Toronto Tempo",
    "LVA": "Las Vegas Aces",
    "CON": "Connecticut Sun",
    "CHI": "Chicago Sky",
    "GSV": "Golden State Valkyries",
    "IND": "Indiana Fever",
    "LAS": "Los Angeles Sparks",
    "ATL": "Atlanta Dream",
    "DAL": "Dallas Wings",
    "NYL": "New York Liberty",
    "MIN": "Minnesota Lynx",
    "PHO": "Phoenix Mercury",
    "WAS": "Washington Mystics",
    "POR": "Portland Fire",
}


def clean_player_name(name):
    return (
        str(name)
        .replace(" GTD", "")
        .replace(" OUT", "")
        .replace(" Q", "")
        .strip()
    )


def get_text_lines():
    response = requests.get(URL, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    return [
        line.strip()
        for line in soup.get_text("\n").split("\n")
        if line.strip()
    ]


def find_matchup_starts(text_lines):
    matchup_starts = []

    for i in range(len(text_lines) - 1):
        first = text_lines[i]
        second = text_lines[i + 1]

        if first in TEAM_MAP and second in TEAM_MAP:
            matchup_starts.append(i)

    return matchup_starts


def extract_expected_lineup(chunk, team_name):
    starters = []

    try:
        start = chunk.index("Expected Lineup") + 1
    except ValueError:
        return []

    i = start

    while i < len(chunk) and len(starters) < 5:
        line = chunk[i]

        if line == "Projected Minutes":
            break

        if line in ["G", "F", "C", "None"]:
            if i + 1 < len(chunk):
                player_name = clean_player_name(chunk[i + 1])

                if player_name not in ["Projected Minutes", "MAY NOT PLAY"]:
                    starters.append(player_name)

            i += 2
        else:
            i += 1

    if len(starters) != 5:
        print(f"WARNING: Could not find 5 starters for {team_name}. Found: {starters}")

    return starters


def fetch_rotowire_lineups():
    text_lines = get_text_lines()
    matchup_starts = find_matchup_starts(text_lines)

    rows = []

    for idx, start in enumerate(matchup_starts):
        end = matchup_starts[idx + 1] if idx + 1 < len(matchup_starts) else len(text_lines)
        game_chunk = text_lines[start:end]

        away_abbr = game_chunk[0]
        home_abbr = game_chunk[1]

        teams = [TEAM_MAP[away_abbr], TEAM_MAP[home_abbr]]

        expected_indexes = [
            i for i, line in enumerate(game_chunk)
            if line == "Expected Lineup"
        ]

        if len(expected_indexes) < 2:
            print(f"WARNING: Missing expected lineups for {teams}")
            continue

        for team_idx, team_name in enumerate(teams):
            lineup_start = expected_indexes[team_idx]
            lineup_end = (
                expected_indexes[team_idx + 1]
                if team_idx + 1 < len(expected_indexes)
                else len(game_chunk)
            )

            lineup_chunk = game_chunk[lineup_start:lineup_end]
            starters = extract_expected_lineup(lineup_chunk, team_name)

            if len(starters) == 5:
                rows.append({
                    "team": team_name,
                    "starter_1": starters[0],
                    "starter_2": starters[1],
                    "starter_3": starters[2],
                    "starter_4": starters[3],
                    "starter_5": starters[4],
                    "source": "RotoWire Daily Lineups",
                    "updated": date.today().isoformat()
                })

    return pd.DataFrame(rows)


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    starters_df = fetch_rotowire_lineups()

    if starters_df.empty:
        print("No starters found. RotoWire page structure may have changed.")
        return

    starters_df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved starters to {OUTPUT_FILE}")
    print(starters_df)


if __name__ == "__main__":
    main()