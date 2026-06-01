import requests
import sys
import pandas as pd
from datetime import datetime, timedelta

# Pull from beginning of preseason through today
START_DATE = datetime(2026, 4, 30)
END_DATE = datetime.today()

DATES = []

current_date = START_DATE
while current_date <= END_DATE:
    DATES.append(current_date.strftime("%Y%m%d"))
    current_date += timedelta(days=1)

players = []

for DATE in DATES:
    scoreboard_url = (
        f"https://site.api.espn.com/apis/site/v2/"
        f"sports/basketball/wnba/scoreboard?dates={DATE}"
    )

    try:
        scoreboard_data = requests.get(scoreboard_url, timeout=30).json()
    except requests.exceptions.RequestException as e:
        print(f"[WARNING] ESPN request failed: {e}")
        sys.exit(1)

    for event in scoreboard_data.get("events", []):
        raw_date = event.get("date")

        if raw_date is None:
            continue

        parsed_date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%MZ")
        game_date = parsed_date.strftime("%A, %B %d, %Y")

        # Label preseason vs regular season
        if parsed_date < datetime(2026, 5, 8):
            season_phase = "preseason"
        else:
            season_phase = "regular_season"

        event_id = event["id"]
        competition = event["competitions"][0]
        competitors = competition["competitors"]

        away_team = [c for c in competitors if c.get("homeAway") == "away"][0]
        home_team = [c for c in competitors if c.get("homeAway") == "home"][0]

        away_abbr = away_team["team"]["abbreviation"]
        home_abbr = home_team["team"]["abbreviation"]

        game_id = f"{parsed_date.strftime('%Y%m%d')}_{away_abbr}_{home_abbr}"

        summary_url = (
            f"https://site.api.espn.com/apis/site/v2/"
            f"sports/basketball/wnba/summary?event={event_id}"
        )

        summary_data = requests.get(summary_url).json()

        boxscore_players = summary_data.get("boxscore", {}).get("players", [])

        if not boxscore_players:
            continue

        for team_block in boxscore_players:
            team_name = team_block["team"]["displayName"]

            opponent_name = [
                c["team"]["displayName"]
                for c in competitors
                if c["team"]["displayName"] != team_name
            ][0]

            for stat_group in team_block.get("statistics", []):
                stat_names = stat_group.get("names", [])
                athletes = stat_group.get("athletes", [])

                for athlete in athletes:
                    player_name = athlete["athlete"]["displayName"]

                    position = athlete["athlete"].get("position", {})
                    position_abbr = position.get("abbreviation")

                    values = athlete.get("stats", [])
                    stat_dict = dict(zip(stat_names, values))

                    players.append({
                        "game_id": game_id,
                        "date": game_date,
                        "season_phase": season_phase,
                        "team": team_name,
                        "opponent": opponent_name,
                        "player": player_name,
                        "position": position_abbr,

                        "min": stat_dict.get("MIN"),
                        "fg": stat_dict.get("FG"),
                        "3pt": stat_dict.get("3PT"),
                        "ft": stat_dict.get("FT"),
                        "oreb": stat_dict.get("OREB"),
                        "dreb": stat_dict.get("DREB"),
                        "reb": stat_dict.get("REB"),
                        "ast": stat_dict.get("AST"),
                        "stl": stat_dict.get("STL"),
                        "blk": stat_dict.get("BLK"),
                        "to": stat_dict.get("TO"),
                        "pf": stat_dict.get("PF"),
                        "pts": stat_dict.get("PTS"),
                        "plus_minus": stat_dict.get("+/-")
                    })

df = pd.DataFrame(players)

VALID_WNBA_TEAMS = [
    "Atlanta Dream",
    "Chicago Sky",
    "Connecticut Sun",
    "Dallas Wings",
    "Golden State Valkyries",
    "Indiana Fever",
    "Las Vegas Aces",
    "Los Angeles Sparks",
    "Minnesota Lynx",
    "New York Liberty",
    "Phoenix Mercury",
    "Portland Fire",
    "Seattle Storm",
    "Toronto Tempo",
    "Washington Mystics"
]

# Keep only official WNBA teams
df = df[df["team"].isin(VALID_WNBA_TEAMS)]

# Remove duplicate player rows
if not df.empty:
    df = df.drop_duplicates(
        subset=["game_id", "team", "player"]
    )

print(df.head())
print("\nDataset shape:")
print(df.shape)

print("\nTeams found:")
print(df["team"].unique())

print("\nSeason phases:")
print(df["season_phase"].value_counts())

df.to_csv("../data/player_box_scores.csv", index=False)

print("\nPlayer box score data extracted successfully.")