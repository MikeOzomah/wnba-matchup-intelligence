from nba_api.stats.endpoints import leaguedashteamstats
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "data" / "team_stat_rankings.csv"


def rank_desc(df, col):
    return df[col].rank(ascending=False, method="min").astype(int)


def main():
    print("Pulling official WNBA stats via nba_api...")

    # LeagueID = '10' is WNBA
    data = leaguedashteamstats.LeagueDashTeamStats(
        league_id_nullable="10",
        season="2026",
        season_type_all_star="Regular Season",
        per_mode_detailed="PerGame"
    )

    df = data.get_data_frames()[0]
    print(
        df[df["TEAM_NAME"] == "Atlanta Dream"][
            [
                "TEAM_NAME",
                "GP",
                "PTS", "PTS_RANK",
                "REB", "REB_RANK",
                "AST", "AST_RANK",
                "BLK", "BLK_RANK",
                "STL", "STL_RANK",
                "FG_PCT", "FG_PCT_RANK",
                "FG3M", "FG3M_RANK",
                "FG3_PCT", "FG3_PCT_RANK",
                "FT_PCT", "FT_PCT_RANK",
            ]
        ]
    )

    print("Columns found:")
    print(df.columns.tolist())

    rankings = pd.DataFrame()
    rankings["team"] = df["TEAM_NAME"]

    rankings["points_rank"] = df["PTS_RANK"]
    rankings["rebounds_rank"] = df["REB_RANK"]
    rankings["assists_rank"] = df["AST_RANK"]
    rankings["blocks_rank"] = df["BLK_RANK"]
    rankings["steals_rank"] = df["STL_RANK"]
    rankings["fg_pct_rank"] = df["FG_PCT_RANK"]
    rankings["three_pm_rank"] = df["FG3M_RANK"]
    rankings["three_pct_rank"] = df["FG3_PCT_RANK"]
    rankings["ft_pct_rank"] = df["FT_PCT_RANK"]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    rankings.to_csv(OUTPUT_FILE, index=False)

    print(f"\nSaved rankings to {OUTPUT_FILE}")
    print(rankings)


if __name__ == "__main__":
    main()