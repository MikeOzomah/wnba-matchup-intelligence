import requests
import pandas as pd
from datetime import datetime, timedelta

# Automatically pull games from season start through today
START_DATE = datetime(2026, 5, 8)
END_DATE = datetime.today()

DATES = []

current_date = START_DATE
while current_date <= END_DATE:
    DATES.append(current_date.strftime("%Y%m%d"))
    current_date += timedelta(days=1)

games = []

for DATE in DATES:
    scoreboard_url = (
        f"https://site.api.espn.com/apis/site/v2/"
        f"sports/basketball/wnba/scoreboard?dates={DATE}"
    )

    scoreboard_data = requests.get(scoreboard_url).json()

    for event in scoreboard_data.get("events", []):
        raw_date = event.get("date")

        if raw_date is None:
            continue

        parsed_date = datetime.strptime(raw_date, "%Y-%m-%dT%H:%MZ")
        game_date = parsed_date.strftime("%A, %B %d, %Y")

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

        boxscore_teams = summary_data.get("boxscore", {}).get("teams", [])

        if not boxscore_teams:
            continue

        for idx, team_box in enumerate(boxscore_teams):
            team_name = team_box["team"]["displayName"]
            team_abbr = team_box["team"]["abbreviation"]

            opponent_box = boxscore_teams[1] if idx == 0 else boxscore_teams[0]
            opponent_name = opponent_box["team"]["displayName"]

            competitor = [
                c for c in competitors
                if c["team"]["displayName"] == team_name
            ][0]

            stats = {}

            for stat in team_box.get("statistics", []):
                stats[stat["name"]] = stat.get("displayValue")

            games.append({
                "game_id": game_id,
                "date": game_date,
                "team": team_name,
                "opponent": opponent_name,
                "team_abbr": team_abbr,

                "fg": stats.get("fieldGoalsMade-fieldGoalsAttempted"),
                "fg_pct": stats.get("fieldGoalPct"),

                "3pt": stats.get("threePointFieldGoalsMade-threePointFieldGoalsAttempted"),
                "3p_pct": stats.get("threePointFieldGoalPct"),

                "ft": stats.get("freeThrowsMade-freeThrowsAttempted"),
                "ft_pct": stats.get("freeThrowPct"),

                "oreb": stats.get("offensiveRebounds"),
                "dreb": stats.get("defensiveRebounds"),
                "reb": stats.get("totalRebounds"),

                "ast": stats.get("assists"),
                "stl": stats.get("steals"),
                "blk": stats.get("blocks"),
                "to": stats.get("turnovers"),
                "pf": stats.get("fouls"),
                "pts": competitor.get("score")
            })

df = pd.DataFrame(games)

# Remove duplicate team-game rows if script pulls same game more than once
if not df.empty:
    df = df.drop_duplicates(subset=["game_id", "team"])

print(df.head())
print("\nDataset shape:")
print(df.shape)

df.to_csv("../data/full_wnba_team_stats.csv", index=False)

print("\nFull WNBA team stats extracted successfully.")