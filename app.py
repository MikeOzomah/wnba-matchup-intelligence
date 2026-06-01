import base64
from pathlib import Path
from datetime import datetime
import subprocess
import sys

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import requests

def get_matchup_from_api(team_a, team_b):
    try:
        matchup = f"{team_a}_vs_{team_b}"
        url = f"http://127.0.0.1:8000/report/{matchup}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

# ============================================================
# FILE PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PLAYER_STATS_FILE = BASE_DIR / "data" / "player_box_scores.csv"
TEAM_STATS_FILE = BASE_DIR / "data" / "full_wnba_team_stats.csv"
STARTER_FILE = BASE_DIR / "data" / "starter_reference.csv"
LOGO_DIR = BASE_DIR / "assets" / "logos"

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="WNBA Matchup Intelligence",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top left, #14245c 0%, #07101f 45%, #030712 100%);
    color: #f8fafc;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}

h1, h2, h3 {
    font-family: Impact, Haettenschweiler, 'Arial Narrow Bold', sans-serif;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #f8fafc;
}

[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(148, 163, 184, 0.25);
    border-radius: 16px;
    padding: 16px;
}

.pro-card {
    background: linear-gradient(135deg, rgba(30,41,59,.88), rgba(15,23,42,.92));
    border: 1px solid rgba(148,163,184,.25);
    border-radius: 18px;
    padding: 20px 24px;
    margin: 14px 0;
    box-shadow: 0 12px 35px rgba(0,0,0,.28);
}

.section-title {
    font-family: Impact, Haettenschweiler, 'Arial Narrow Bold', sans-serif;
    font-size: 30px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 18px;
}

.blue-title {
    color: #3b82f6;
}

.small-muted {
    color: #94a3b8;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Matchup History */
.history-row-4 {
    display: grid;
    grid-template-columns: 1.6fr 1.5fr 1fr .7fr;
    gap: 20px;
    align-items: center;
}

.history-header {
    color: #94a3b8;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.history-team {
    display: flex;
    align-items: center;
    gap: 12px;
}

.score-red {
    color: #ff3b5c;
    font-size: 24px;
    font-weight: 800;
}

.score-blue {
    color: #3b82f6;
    font-size: 24px;
    font-weight: 800;
}

.score-sep {
    color: #94a3b8;
    padding: 0 8px;
    font-weight: 800;
}

.margin-green {
    color: #22c55e;
    font-weight: 800;
}

.winner-a {
    color: #ff3b5c;
    font-weight: 900;
}

.winner-b {
    color: #3b82f6;
    font-weight: 900;
}

/* Series Summary */
.series-card {
    margin-top: 22px;
    padding: 22px;
    border: 1px solid rgba(148,163,184,.22);
    border-radius: 16px;
    background: rgba(2,6,23,.35);
}

.series-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
    text-align: center;
    align-items: center;
}

.series-number {
    font-size: 40px;
    font-weight: 900;
    line-height: 1.1;
}

.series-note {
    margin-top: 18px;
    color: #cbd5e1;
    font-size: 14px;
    text-align: center;
}

.red {
    color: #ff3b5c;
}

.blue {
    color: #3b82f6;
}

.green {
    color: #22c55e;
}

/* Insight Box */
.insight-box {
    background: rgba(30, 64, 175, .28);
    border-left: 5px solid #22c55e;
    border-radius: 14px;
    padding: 18px 22px;
    margin: 12px 0;
}
</style>
""", unsafe_allow_html=True)



# ============================================================
# TEAM COLORS
# ============================================================

TEAM_COLORS = {
    "Atlanta Dream": "#FF2A7F",
    "Chicago Sky": "#00AEEF",
    "Connecticut Sun": "#FF6A00",
    "Dallas Wings": "#0072CE",
    "Golden State Valkyries": "#8A2BE2",
    "Indiana Fever": "#FF1744",
    "Las Vegas Aces": "#D9D9D9",
    "Los Angeles Sparks": "#F7D13D",
    "Minnesota Lynx": "#00A3E0",
    "New York Liberty": "#66E0D5",
    "Phoenix Mercury": "#FF6600",
    "Portland Fire": "#FF2A7F",
    "Seattle Storm": "#2DD4BF",
    "Toronto Tempo": "#B026FF",
    "Washington Mystics": "#1E5BFF",
}

GOLD = "#D6A84F"
BG = "#050914"
PANEL = "#101827"
PANEL_2 = "#151F33"


def get_team_color(team):
    return TEAM_COLORS.get(team, "#AAAAAA")


# ============================================================
# CSS -- ESPN / PREMIUM SPORTS STYLE
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;600;700;800&display=swap');

.stApp {
    background:
        radial-gradient(circle at top left, rgba(38, 58, 105, 0.55), transparent 35%),
        linear-gradient(180deg, #050914 0%, #070B16 45%, #04060D 100%);
    color: #F4F4F5;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

h1, h2, h3, h4 {
    font-family: 'Oswald', sans-serif !important;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #F8FAFC !important;
}

p, span, div, label {
    color: #E5E7EB !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #08101E, #050914);
    border-right: 1px solid rgba(214,168,79,0.22);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #F8FAFC !important;
}

/* Select boxes */
div[data-baseweb="select"] > div {
    background-color: #111827 !important;
    border: 1px solid rgba(214,168,79,0.35) !important;
    border-radius: 10px !important;
    color: white !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    background: #0B1220 !important;
    border: 1px solid rgba(214,168,79,0.18) !important;
    border-radius: 0px !important;
    margin-right: 6px !important;
    padding: 12px 22px !important;
}

button[data-baseweb="tab"] p {
    font-family: 'Oswald', sans-serif !important;
    letter-spacing: 1.1px !important;
    text-transform: uppercase !important;
    color: #CBD5E1 !important;
    font-size: 16px !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 3px solid #D6A84F !important;
    background: #111827 !important;
}

button[data-baseweb="tab"][aria-selected="true"] p {
    color: #D6A84F !important;
}

.block-container {
    padding-top: 2rem;
    max-width: 1400px;
}

/* Header */
.app-kicker {
    color: #D6A84F !important;
    font-family: 'Oswald', sans-serif;
    letter-spacing: 4px;
    font-size: 15px;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.main-title {
    font-family: 'Oswald', sans-serif;
    letter-spacing: 2px;
    font-size: 52px;
    font-weight: 700;
    color: #F8FAFC !important;
    line-height: 1.0;
    margin-bottom: 8px;
}

.subtitle {
    color: #94A3B8 !important;
    font-size: 18px;
    margin-bottom: 24px;
}

/* Cards */
.hero-card {
    background:
        linear-gradient(135deg, rgba(17,24,39,0.96), rgba(8,13,27,0.94));
    border: 1px solid rgba(214,168,79,0.28);
    border-radius: 18px;
    padding: 30px;
    margin-bottom: 28px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.45);
}

.section-card {
    background: linear-gradient(180deg, rgba(17,24,39,0.92), rgba(10,15,30,0.94));
    border: 1px solid rgba(148,163,184,0.18);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 20px;
}

.verdict-card {
    background: linear-gradient(135deg, rgba(214,168,79,0.18), rgba(17,24,39,0.95));
    border: 1px solid rgba(214,168,79,0.45);
    border-left: 6px solid #D6A84F;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 20px;
}

.insight-card {
    background: rgba(15,23,42,0.92);
    border-left: 5px solid #22C55E;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 12px;
    font-weight: 650;
}

.warning-card {
    background: rgba(15,23,42,0.92);
    border-left: 5px solid #F59E0B;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 12px;
    font-weight: 650;
}

.player-card {
    background: rgba(15,23,42,0.88);
    border: 1px solid rgba(148,163,184,0.18);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 14px;
}

.player-name {
    font-family: 'Oswald', sans-serif;
    font-size: 22px;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    color: #F8FAFC !important;
}

.player-role {
    color: #D6A84F !important;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.player-statline {
    color: #CBD5E1 !important;
    font-size: 13px;
    font-weight: 700;
    margin: 8px 0 10px 0;
}

.scout-chip {
    display: inline-block;
    background: rgba(214,168,79,0.13);
    border: 1px solid rgba(214,168,79,0.25);
    border-radius: 999px;
    padding: 5px 10px;
    margin: 3px 3px 3px 0;
    font-size: 12px;
    font-weight: 700;
    color: #FDE68A !important;
}

.concern-chip {
    display: inline-block;
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 999px;
    padding: 5px 10px;
    margin: 3px 3px 3px 0;
    font-size: 12px;
    font-weight: 700;
    color: #FCA5A5 !important;
}

.logo-circle {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Oswald', sans-serif;
    font-size: 30px;
    font-weight: 800;
    color: #050914 !important;
    margin: auto;
    border: 2px solid rgba(255,255,255,0.25);
}

.metric-label {
    font-family: 'Oswald', sans-serif;
    color: #94A3B8 !important;
    letter-spacing: 1.3px;
    text-transform: uppercase;
    font-size: 14px;
}

.metric-number {
    font-family: 'Oswald', sans-serif;
    font-size: 42px;
    font-weight: 800;
    color: #F8FAFC !important;
    line-height: 1.05;
}

.gold-line {
    height: 2px;
    background: linear-gradient(90deg, transparent, #D6A84F, transparent);
    margin: 14px 0 26px 0;
}

.small-muted {
    color: #94A3B8 !important;
    font-size: 13px;

.winner-badge {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(148, 163, 184, 0.25);
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: .6px;

.team-record {
    color: #94a3b8;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 1px;
    margin-top: -10px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_team_game_stats(file_mtime):
    if not TEAM_STATS_FILE.exists():
        st.error(f"Could not find {TEAM_STATS_FILE}")
        st.stop()

    df = pd.read_csv(TEAM_STATS_FILE)

    return df

@st.cache_data
def load_player_stats(file_mtime):
    if not PLAYER_STATS_FILE.exists():
        st.error(f"Could not find {PLAYER_STATS_FILE}")
        st.stop()

    df = pd.read_csv(PLAYER_STATS_FILE)

    df = df.rename(columns={
        "player": "player_name",
        "pts": "PTS",
        "reb": "REB",
        "ast": "AST",
        "stl": "STL",
        "blk": "BLK",
        "min": "MIN",
    })

    required = [
        "game_id", "season_phase", "team", "player_name", "position",
        "MIN", "PTS", "REB", "AST", "STL", "BLK"
    ]

    missing = [col for col in required if col not in df.columns]
    if missing:
        st.error(f"Missing columns in player_box_scores.csv: {missing}")
        st.stop()

    for col in ["MIN", "PTS", "REB", "AST", "STL", "BLK"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df[
        df["season_phase"]
        .astype(str)
        .str.lower()
        .str.contains("regular")
    ].copy()

    return df


@st.cache_data
def load_starters():
    if not STARTER_FILE.exists():
        return pd.DataFrame()
    return pd.read_csv(STARTER_FILE)


# ============================================================
# NAME MATCHING
# ============================================================

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


# ============================================================
# PROFILE BUILDERS
# ============================================================

def get_team_identity(team):
    identities = {
        "Atlanta Dream": "Glass-Crashing Pressure Team",
        "Chicago Sky": "Interior Control Team",
        "Dallas Wings": "Fast-Paced Scoring Team",
        "Indiana Fever": "Elite Offensive Engine",
        "Las Vegas Aces": "Shot Quality Machine",
        "Minnesota Lynx": "Balanced Contender",
        "New York Liberty": "Spacing & Creation Team",
        "Phoenix Mercury": "Perimeter Firepower",
        "Seattle Storm": "Veteran Execution Team",
        "Washington Mystics": "Defensive Grind Team",
        "Connecticut Sun": "Physical Rebounding Team",
        "Los Angeles Sparks": "Transition Attack Team",
        "Golden State Valkyries": "Expansion Development Team"
    }

    return identities.get(team, "Balanced Team")

def get_team_record(team_games_df, team):
    games = team_games_df[team_games_df["team"] == team].copy()

    if games.empty:
        return "0-0"

    wins = 0
    losses = 0

    for _, row in games.iterrows():
        game_id = row["game_id"]
        opponent = row["opponent"]
        team_pts = pd.to_numeric(row["pts"], errors="coerce")

        opp_row = team_games_df[
            (team_games_df["game_id"] == game_id) &
            (team_games_df["team"] == opponent)
        ]

        if opp_row.empty:
            continue

        opp_pts = pd.to_numeric(opp_row.iloc[0]["pts"], errors="coerce")

        if pd.isna(team_pts) or pd.isna(opp_pts):
            continue

        if team_pts > opp_pts:
            wins += 1
        elif team_pts < opp_pts:
            losses += 1

    return f"{wins}-{losses}"

def build_team_profiles(df):
    game_totals = df.groupby(["team", "game_id"], as_index=False).agg({
        "PTS": "sum",
        "REB": "sum",
        "AST": "sum",
        "STL": "sum",
        "BLK": "sum",
    })

    numeric_cols = ["PTS", "REB", "AST", "STL", "BLK"]

    for col in numeric_cols:
        game_totals[col] = pd.to_numeric(game_totals[col], errors="coerce")

    profiles = game_totals.groupby("team", as_index=False)[numeric_cols].mean()
    profiles["DEF"] = profiles["STL"] + profiles["BLK"]
    return profiles


def build_player_profiles(df):
    return df.groupby(["team", "player_name", "position"], as_index=False).agg({
        "MIN": "mean",
        "PTS": "mean",
        "REB": "mean",
        "AST": "mean",
        "STL": "mean",
        "BLK": "mean",
    })


def get_projected_lineup(team_name, player_profiles, starters_df):
    team_players = player_profiles[player_profiles["team"] == team_name].copy()

    if starters_df.empty:
        return team_players.sort_values("MIN", ascending=False).head(5)

    starter_row = starters_df[starters_df["team"] == team_name]

    if starter_row.empty:
        return team_players.sort_values("MIN", ascending=False).head(5)

    starter_names = starter_row.iloc[0][
        ["starter_1", "starter_2", "starter_3", "starter_4", "starter_5"]
    ].tolist()

    matched_rows = []

    for name in starter_names:
        match = team_players[
            team_players["player_name"].apply(lambda x: name_matches(name, x))
        ]

        if not match.empty:
            matched_rows.append(match.iloc[0])

    if matched_rows:
        return pd.DataFrame(matched_rows)

    return team_players.sort_values("MIN", ascending=False).head(5)


def calculate_lineup_profile(lineup_df):
    return {
        "scoring": lineup_df["PTS"].mean(),
        "playmaking": lineup_df["AST"].mean(),
        "rebounding": lineup_df["REB"].mean(),
        "defense": lineup_df["STL"].mean() + lineup_df["BLK"].mean(),
    }


# ============================================================
# PLAYER SCOUTING ENGINE
# ============================================================

def player_role(player):
    pts = player["PTS"]
    ast = player["AST"]
    reb = player["REB"]
    defense = player["STL"] + player["BLK"]
    pos = str(player["position"]).upper()

    if pts >= 18 and ast >= 4:
        return "Primary Offensive Engine"
    if pts >= 18:
        return "Primary Scoring Option"
    if ast >= 5:
        return "Lead Creator / Table Setter"
    if reb >= 9:
        return "Interior Anchor / Glass Cleaner"
    if defense >= 2:
        return "Defensive Activity Piece"
    if pts >= 10:
        return "Secondary Scoring Option"
    if "C" in pos or "F" in pos:
        return "Frontcourt Rotation Piece"
    return "Rotation Guard / Connector"


def player_strengths(player):
    strengths = []

    if player["PTS"] >= 18:
        strengths.append("high-volume scoring")
    elif player["PTS"] >= 12:
        strengths.append("reliable scoring punch")

    if player["AST"] >= 5:
        strengths.append("primary creation")
    elif player["AST"] >= 3:
        strengths.append("secondary playmaking")

    if player["REB"] >= 9:
        strengths.append("elite rebounding")
    elif player["REB"] >= 5:
        strengths.append("solid rebounding")

    if player["STL"] >= 1.5:
        strengths.append("steal pressure")

    if player["BLK"] >= 1.5:
        strengths.append("rim protection")

    if player["STL"] + player["BLK"] >= 2:
        strengths.append("defensive disruption")

    if not strengths:
        strengths.append("low-usage stability")

    return strengths


def player_concerns(player):
    concerns = []

    if player["PTS"] < 6:
        concerns.append("limited scoring impact")

    if player["AST"] < 1.5:
        concerns.append("limited creation")

    if player["REB"] < 3 and str(player["position"]).upper() in ["F", "C"]:
        concerns.append("low rebounding for role")

    if player["STL"] + player["BLK"] < 0.8:
        concerns.append("low defensive event creation")

    if player["MIN"] < 18:
        concerns.append("smaller rotation sample")

    if not concerns:
        concerns.append("no major statistical concern")

    return concerns


def player_profile_summary(player):
    role = player_role(player)
    strengths = player_strengths(player)
    concerns = player_concerns(player)

    return role, strengths, concerns


# ============================================================
# INTELLIGENCE ENGINES
# ============================================================

def score_team(row):
    return (
        row["PTS"] * 0.35
        + row["REB"] * 0.25
        + row["AST"] * 0.20
        + row["DEF"] * 0.20
    )


def determine_matchup_edge(team_a, team_b, row_a, row_b):
    score_a = score_team(row_a)
    score_b = score_team(row_b)

    if abs(score_a - score_b) < 1.5:
        return "Even Matchup"

    return team_a if score_a > score_b else team_b


def confidence_score(row_a, row_b):
    gap = abs(score_team(row_a) - score_team(row_b))
    return round(50 + min(gap * 3.5, 35), 1)


def generate_matchup_factors(team_a, team_b, row_a, row_b):
    factors = [
        ("Scoring Pressure", "PTS", row_a["PTS"], row_b["PTS"]),
        ("Glass Control", "REB", row_a["REB"], row_b["REB"]),
        ("Creation Flow", "AST", row_a["AST"], row_b["AST"]),
        ("Defensive Disruption", "DEF", row_a["DEF"], row_b["DEF"]),
        ("Steal Pressure", "STL", row_a["STL"], row_b["STL"]),
        ("Rim Protection", "BLK", row_a["BLK"], row_b["BLK"]),
    ]

    output = []

    for label, stat, a_val, b_val in factors:
        diff = a_val - b_val

        if abs(diff) < 0.5:
            winner = "Even"
        else:
            winner = team_a if diff > 0 else team_b

        output.append({
            "label": label,
            "stat": stat,
            "team_a_value": a_val,
            "team_b_value": b_val,
            "diff": diff,
            "winner": winner
        })

    return output


def generate_matchup_insights(team_a, team_b, row_a, row_b):
    insights = []

    if row_a["PTS"] > row_b["PTS"] + 3:
        insights.append(("PRIMARY EDGE", f"{team_a} has the stronger scoring profile."))
    elif row_b["PTS"] > row_a["PTS"] + 3:
        insights.append(("PRIMARY EDGE", f"{team_b} has the stronger scoring profile."))

    if row_a["REB"] > row_b["REB"] + 2:
        insights.append(("POSSESSION EDGE", f"{team_a} can tilt the game through rebounding and second chances."))
    elif row_b["REB"] > row_a["REB"] + 2:
        insights.append(("POSSESSION EDGE", f"{team_b} can tilt the game through rebounding and second chances."))

    if row_a["AST"] > row_b["AST"] + 2:
        insights.append(("CREATION EDGE", f"{team_a} has the cleaner ball-movement profile."))
    elif row_b["AST"] > row_a["AST"] + 2:
        insights.append(("CREATION EDGE", f"{team_b} has the cleaner ball-movement profile."))

    if row_a["DEF"] > row_b["DEF"] + 1:
        insights.append(("DISRUPTION EDGE", f"{team_a} creates more defensive events through steals and blocks."))
    elif row_b["DEF"] > row_a["DEF"] + 1:
        insights.append(("DISRUPTION EDGE", f"{team_b} creates more defensive events through steals and blocks."))

    if not insights:
        insights.append(("BALANCED PROFILE", "This matchup is tight by team averages. Execution, turnovers, and shot quality may decide it."))

    return insights


def generate_game_script(team_a, team_b, row_a, row_b):
    script = []

    scoring_team = team_a if row_a["PTS"] > row_b["PTS"] else team_b
    rebounding_team = team_a if row_a["REB"] > row_b["REB"] else team_b
    creation_team = team_a if row_a["AST"] > row_b["AST"] else team_b
    defense_team = team_a if row_a["DEF"] > row_b["DEF"] else team_b

    script.append(f"{scoring_team} wants the game to lean into scoring pace and shot-making pressure.")
    script.append(f"{rebounding_team} can shift possessions through rebounding control and second-chance opportunities.")
    script.append(f"{creation_team} has the cleaner team creation profile and may generate easier looks.")
    script.append(f"{defense_team}'s defensive activity can create momentum swings through steals and blocks.")

    if scoring_team != rebounding_team:
        script.append("This matchup has a pace-versus-possession tension: one side owns scoring rhythm, while the other can control the glass.")

    return script


def generate_what_to_watch(team_a, team_b, row_a, row_b):
    watch = []

    if abs(row_a["PTS"] - row_b["PTS"]) >= 5:
        high = team_a if row_a["PTS"] > row_b["PTS"] else team_b
        low = team_b if high == team_a else team_a
        watch.append(f"Can {low} keep pace with {high}'s scoring profile?")

    if abs(row_a["REB"] - row_b["REB"]) >= 4:
        high = team_a if row_a["REB"] > row_b["REB"] else team_b
        watch.append(f"Does {high}'s rebounding edge turn into extra possessions?")

    if abs(row_a["AST"] - row_b["AST"]) >= 3:
        high = team_a if row_a["AST"] > row_b["AST"] else team_b
        watch.append(f"Can {high}'s ball movement create cleaner shots?")

    if abs(row_a["DEF"] - row_b["DEF"]) >= 2:
        high = team_a if row_a["DEF"] > row_b["DEF"] else team_b
        watch.append(f"Can {high}'s defensive disruption force momentum-changing possessions?")

    if not watch:
        watch.append("Which team wins the small margins: turnovers, second chances, and late-clock shot quality?")

    return watch


def generate_lineup_identity(team_name, lineup_profile):
    insights = []

    if lineup_profile["scoring"] >= 12:
        insights.append(f"{team_name}'s projected lineup has strong scoring punch.")
    elif lineup_profile["scoring"] >= 8:
        insights.append(f"{team_name}'s projected lineup has enough scoring to stay competitive.")
    else:
        insights.append(f"{team_name}'s projected lineup may need cleaner offensive creation.")

    if lineup_profile["playmaking"] >= 4:
        insights.append(f"{team_name}'s projected lineup has strong connective playmaking.")
    elif lineup_profile["playmaking"] >= 2:
        insights.append(f"{team_name} likely depends on one or two primary creators.")
    else:
        insights.append(f"{team_name}'s projected lineup may become stagnant under pressure.")

    if lineup_profile["rebounding"] >= 6:
        insights.append(f"{team_name}'s projected lineup has strong rebounding presence.")
    elif lineup_profile["rebounding"] >= 3:
        insights.append(f"{team_name}'s lineup is solid but not dominant on the glass.")
    else:
        insights.append(f"{team_name}'s lineup may be vulnerable on the boards.")

    if lineup_profile["defense"] >= 2:
        insights.append(f"{team_name}'s projected lineup can create disruption defensively.")

    return insights


def lineup_vs_lineup_summary(team_a, team_b, profile_a, profile_b):
    rows = [
        ("Scoring", profile_a["scoring"], profile_b["scoring"]),
        ("Creation", profile_a["playmaking"], profile_b["playmaking"]),
        ("Rebounding", profile_a["rebounding"], profile_b["rebounding"]),
        ("Defensive Activity", profile_a["defense"], profile_b["defense"]),
    ]

    output = []

    for label, a_val, b_val in rows:
        if abs(a_val - b_val) < 0.5:
            edge = "Even"
        else:
            edge = team_a if a_val > b_val else team_b

        output.append((label, a_val, b_val, edge))

    return output


# ============================================================
# LOGOS
# ============================================================

def safe_file_name(name):
    return (
        str(name)
        .lower()
        .replace(" ", "_")
        .replace("'", "")
        .replace(".", "")
        .replace("-", "_")
    )


def get_logo_path(team):
    base_name = safe_file_name(team)


    possible_files = [
        LOGO_DIR / f"{base_name}.png",
        LOGO_DIR / f"{base_name}.svg",
        LOGO_DIR / f"{base_name}.jpg",
        LOGO_DIR / f"{base_name}.jpeg",
        LOGO_DIR / f"{base_name}.webp",
    ]

    for path in possible_files:
        if path.exists():
            return path

    return None


def image_to_data_uri(path):
    with open(path, "rb") as f:
        data = f.read()

    encoded = base64.b64encode(data).decode()
    suffix = path.suffix.lower()

    if suffix == ".svg" or data.strip().startswith(b"<svg"):
        mime = "image/svg+xml"
    elif suffix == ".jpg" or suffix == ".jpeg":
        mime = "image/jpeg"
    elif suffix == ".webp":
        mime = "image/webp"
    else:
        mime = "image/png"

    return f"data:{mime};base64,{encoded}"


def render_logo_or_initial(team, color):
    # Defensive: always return valid HTML, never None or raw text
    if not team or not isinstance(team, str) or team.strip() == "":
        initials = "?"
    else:
        initials = "".join([word[0] for word in team.split()[:2]]).upper()

    logo_path = get_logo_path(team)
    if logo_path and logo_path.exists():
        try:
            logo_uri = image_to_data_uri(logo_path)
            return f"""
            <img src=\"{logo_uri}\"
                 style=\"width:110px;height:110px;object-fit:contain;border-radius:50%;padding:10px;background:rgba(15,23,42,0.95);border:2px solid rgba(214,168,79,0.45);box-shadow:0 0 25px rgba(214,168,79,0.25);\">
            """
        except Exception:
            pass
    # Always return a clean initials badge if logo missing or error
    return f"""
    <div class=\"logo-circle\" style=\"background:{color};\">{initials}</div>
    """


# ============================================================
# VISUALS
# ============================================================

def matchup_bar_chart(team_a, team_b, row_a, row_b):
    color_a = get_team_color(team_a)
    color_b = get_team_color(team_b)

    stats = [
        ("PTS", row_a["PTS"], row_b["PTS"]),
        ("REB", row_a["REB"], row_b["REB"]),
        ("AST", row_a["AST"], row_b["AST"]),
        ("STL", row_a["STL"], row_b["STL"]),
        ("BLK", row_a["BLK"], row_b["BLK"]),
    ]

    labels = [s[0] for s in stats]
    values_a = [-s[1] for s in stats]
    values_b = [s[2] for s in stats]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=labels,
        x=values_a,
        orientation="h",
        marker=dict(color=color_a),
        text=[f"{abs(v):.1f}" for v in values_a],
        textposition="outside",
        hoverinfo="skip",
        name=team_a,
    ))

    fig.add_trace(go.Bar(
        y=labels,
        x=values_b,
        orientation="h",
        marker=dict(color=color_b),
        text=[f"{v:.1f}" for v in values_b],
        textposition="outside",
        hoverinfo="skip",
        name=team_b,
    ))

    max_val = max([max(abs(a), abs(b)) for _, a, b in stats]) * 1.25

    fig.update_layout(
        title=f"{team_a} vs {team_b}",
        barmode="relative",
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8,13,27,0.96)",
        font=dict(color="white", size=14, family="Inter"),
        showlegend=False,
        xaxis=dict(
            range=[-max_val, max_val],
            showgrid=False,
            zeroline=True,
            zerolinecolor="rgba(214,168,79,0.55)",
            showticklabels=False,
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False,
            tickfont=dict(color="white", size=13),
        ),
        margin=dict(l=60, r=60, t=70, b=30),
    )

    return fig


def factor_bar_chart(factors, team_a, team_b):
    labels = [f["label"] for f in factors]
    values = [f["diff"] for f in factors]

    colors = []
    for v in values:
        if v > 0:
            colors.append(get_team_color(team_a))
        elif v < 0:
            colors.append(get_team_color(team_b))
        else:
            colors.append("#777777")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(color=colors),
        text=[f"{v:+.1f}" for v in values],
        textposition="outside",
        hoverinfo="skip",
    ))

    max_abs = max(abs(min(values)), abs(max(values))) * 1.35 if values else 1

    fig.update_layout(
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8,13,27,0.96)",
        font=dict(color="white", size=13, family="Inter"),
        showlegend=False,
        xaxis=dict(
            range=[-max_abs, max_abs],
            zeroline=True,
            zerolinecolor="rgba(214,168,79,0.55)",
            showgrid=False,
        ),
        yaxis=dict(autorange="reversed", showgrid=False),
        margin=dict(l=170, r=80, t=30, b=30),
    )

    return fig


def player_radar_chart(player_a_row, player_b_row, team_a, team_b):
    categories = ["PTS", "REB", "AST", "STL", "BLK"]

    max_values = {
        "PTS": 30,
        "REB": 15,
        "AST": 10,
        "STL": 5,
        "BLK": 5,
    }

    values_a = [min(player_a_row[c] / max_values[c], 1) for c in categories]
    values_b = [min(player_b_row[c] / max_values[c], 1) for c in categories]

    values_a.append(values_a[0])
    values_b.append(values_b[0])

    radar_categories = categories + [categories[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_a,
        theta=radar_categories,
        fill="toself",
        name=player_a_row["player_name"],
        line=dict(color=get_team_color(team_a), width=3),
        fillcolor=get_team_color(team_a),
        opacity=0.55,
    ))

    fig.add_trace(go.Scatterpolar(
        r=values_b,
        theta=radar_categories,
        fill="toself",
        name=player_b_row["player_name"],
        line=dict(color=get_team_color(team_b), width=3),
        fillcolor=get_team_color(team_b),
        opacity=0.55,
    ))

    fig.update_layout(
        height=560,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8,13,27,0.96)",
        font=dict(color="white", family="Inter"),
        polar=dict(
            bgcolor="rgba(8,13,27,0.96)",
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                showticklabels=False,
                gridcolor="rgba(255,255,255,0.16)",
            ),
            angularaxis=dict(
                gridcolor="rgba(214,168,79,0.25)",
                tickfont=dict(color="white", size=13),
            ),
        ),
        legend=dict(
            orientation="h",
            y=-0.1,
            x=0.5,
            xanchor="center",
        ),
        margin=dict(l=30, r=30, t=30, b=50),
    )

    return fig


# ============================================================
# RENDER HELPERS
# ============================================================
def team_logo_html(team_name, size=32):
    logo_path = get_logo_path(team_name)

    if not logo_path or not Path(logo_path).exists():
        return ""

    logo_path = Path(logo_path)
    encoded = base64.b64encode(logo_path.read_bytes()).decode()

    suffix = logo_path.suffix.lower()

    if suffix == ".svg":
        mime = "image/svg+xml"
    elif suffix in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    elif suffix == ".webp":
        mime = "image/webp"
    else:
        mime = "image/png"

    return (
        f"<img src='data:{mime};base64,{encoded}' "
        f"style='height:{size}px; width:{size}px; object-fit:contain;' />"
    )


def render_pro_matchup_history(team_games_df, team_a, team_b, limit=5):
    matchup_games = team_games_df[
        (
            ((team_games_df["team"] == team_a) & (team_games_df["opponent"] == team_b))
            |
            ((team_games_df["team"] == team_b) & (team_games_df["opponent"] == team_a))
        )
    ].copy()

    if matchup_games.empty:
        st.info("No matchup history available yet.")
        return

    matchup_games = matchup_games.sort_values("date", ascending=False)

    rows_html = ""
    processed = set()
    displayed = 0
    team_a_wins = 0
    team_b_wins = 0
    margins = []
    last_winner = None
    biggest_margin = 0
    biggest_winner = None

    for game_id in matchup_games["game_id"].unique():
        game_rows = matchup_games[matchup_games["game_id"] == game_id]

        if game_id in processed or len(game_rows) != 2:
            continue

        processed.add(game_id)

        row1 = game_rows.iloc[0]
        row2 = game_rows.iloc[1]

        pts1 = int(row1["pts"])
        pts2 = int(row2["pts"])

        if pts1 >= pts2:
            winner = row1["team"]
            winner_pts = pts1
            loser_pts = pts2
        else:
            winner = row2["team"]
            winner_pts = pts2
            loser_pts = pts1

        margin = winner_pts - loser_pts
        winner_class = "winner-a" if winner == team_a else "winner-b"

        if winner == team_a:
            team_a_wins += 1
        else:
            team_b_wins += 1

        margins.append(margin)

        if last_winner is None:
            last_winner = winner

        if margin > biggest_margin:
            biggest_margin = margin
            biggest_winner = winner

        rows_html += f"""<div class="history-row history-row-4">
    <div>{row1["date"]}</div>
    <div class="{winner_class} winner-badge">{winner}</div>
    <div><span class="score-red">{winner_pts}</span><span class="score-sep">--</span><span class="score-blue">{loser_pts}</span></div>
    <div class="margin-green">+{margin}</div>
    </div>
    """

        displayed += 1
        if displayed >= limit:
            break

    avg_margin = sum(margins) / len(margins) if margins else 0

    if team_a_wins > team_b_wins:
        series_text = f"{team_a} leads series {team_a_wins}-{team_b_wins}"
    elif team_b_wins > team_a_wins:
        series_text = f"{team_b} leads series {team_b_wins}-{team_a_wins}"
    else:
        series_text = "Series tied"

    last_winner_text = last_winner if last_winner else "N/A"
    biggest_win_text = f"{biggest_winner} by {biggest_margin}" if biggest_winner else "N/A"

    html = f"""<div class="pro-card">
<div class="section-title">Recent Matchup History</div>
<div class="history-row history-header history-row-4">
<div>Date</div>
<div>Winner</div>
<div>Final Score</div>
<div>Margin</div>
</div>
{rows_html}
<div class="series-card">
<div class="section-title blue-title">Series Summary</div>
<div class="series-grid">
<div>
<div class="small-muted">{team_a}</div>
<div class="series-number red">{team_a_wins}</div>
<div class="small-muted">Wins</div>
</div>
<div>
<div class="small-muted">Series Record</div>
<div class="series-number"><span class="red">{team_a_wins}</span><span class="score-sep">--</span><span class="blue">{team_b_wins}</span></div>
<div class="small-muted">Last {displayed} Meetings</div>
</div>
<div>
<div class="small-muted">{team_b}</div>
<div class="series-number blue">{team_b_wins}</div>
<div class="small-muted">Wins</div>
</div>
<div>
<div class="small-muted">Average Margin</div>
<div class="series-number green">+{avg_margin:.1f}</div>
<div class="small-muted">Points Per Game</div>
</div>
</div>
<div class="series-note">{series_text} | Last winner: {last_winner_text} | Biggest win: {biggest_win_text}</div>
</div>
</div>"""

    st.markdown(html, unsafe_allow_html=True)

def render_player_trend(player_name, raw_df):
    player_games = raw_df[
        raw_df["player_name"] == player_name
    ].copy()

    if player_games.empty:
        return

    last_5_ppg = player_games.tail(5)["PTS"].mean()
    season_ppg = player_games["PTS"].mean()
    games_played = player_games["game_id"].nunique()

    trend_diff = last_5_ppg - season_ppg

    if trend_diff >= 2:
        trend_label = "Trending Up"
    elif trend_diff <= -2:
        trend_label = "Cooling Down"
    else:
        trend_label = "Stable"

    st.caption(
        f"Trend: {trend_label} | "
        f"Last 5 PPG: {last_5_ppg:.1f} | "
        f"Season PPG: {season_ppg:.1f} | "
        f"Games: {games_played}"
    )


def render_snapshot(team, row):
    st.markdown(
        f"""
        <div class="section-card">
            <h3>{team}</h3>
            <div class="metric-label">PPG</div>
            <div class="metric-number">{row['PTS']:.1f}</div>
            <br>
            <div class="metric-label">RPG</div>
            <div class="metric-number">{row['REB']:.1f}</div>
            <br>
            <div class="metric-label">APG</div>
            <div class="metric-number">{row['AST']:.1f}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_player_scouting_card(player, expanded=True):
    role, strengths, concerns = player_profile_summary(player)

    strength_html = "".join(
        [f"<span class='scout-chip'>{s}</span>" for s in strengths]
    )

    concern_html = "".join(
        [f"<span class='concern-chip'>{c}</span>" for c in concerns]
    )

    detail = ""
    if expanded:
        detail = f"""
        <div class="small-muted">Strengths</div>
        <div>{strength_html}</div>
        <br>
        <div class="small-muted">Concerns</div>
        <div>{concern_html}</div>
        """

    st.markdown(
        f"""
        <div class="player-card">
            <div class="player-name">{player['player_name']}</div>
            <div class="player-role">{role} · {player['position']}</div>
            <div class="player-statline">
                {player['PTS']:.1f} PTS | {player['REB']:.1f} REB | {player['AST']:.1f} AST |
                {player['STL']:.1f} STL | {player['BLK']:.1f} BLK | {player['MIN']:.1f} MIN
            </div>
            {detail}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_rotation_card(player):
    role, strengths, concerns = player_profile_summary(player)
    top_strengths = ", ".join(strengths[:2])

    st.markdown(
        f"""
        <div class="player-card">
            <div class="player-name" style="font-size:19px;">{player['player_name']}</div>
            <div class="player-role">{role}</div>
            <div class="player-statline">
                {player['MIN']:.1f} MIN · {player['PTS']:.1f} PTS · {player['REB']:.1f} REB · {player['AST']:.1f} AST
            </div>
            <div class="small-muted">Profile: {top_strengths}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# APP DATA
# ============================================================

raw_df = load_player_stats(PLAYER_STATS_FILE.stat().st_mtime)
team_games_df = load_team_game_stats(TEAM_STATS_FILE.stat().st_mtime)
starters_df = load_starters()

# DATA FRESHNESS BADGE
last_updated = datetime.fromtimestamp(
    PLAYER_STATS_FILE.stat().st_mtime
).strftime("%b %d, %Y %I:%M %p")

st.caption(
    f"Data freshness: {last_updated} | "
    f"Player records: {len(raw_df):,} | "
    f"Games loaded: {raw_df['game_id'].nunique()}"
)

if st.button("Refresh WNBA Data"):
    with st.spinner("Running WNBA data pipeline..."):
        result = subprocess.run(
            [sys.executable, str(BASE_DIR / "scripts" / "run_pipeline.py")],
            capture_output=True,
            text=True
        )

    if result.returncode == 0:
        st.cache_data.clear()
        st.success("WNBA data refreshed successfully.")
        st.code(result.stdout)
        st.rerun()
    else:
        st.error("Pipeline failed.")
        st.subheader("Pipeline output")
        st.code(result.stdout if result.stdout else "No stdout captured.")
        st.subheader("Pipeline error")
        st.code(result.stderr if result.stderr else "No stderr captured.")


team_profiles = build_team_profiles(raw_df)
player_profiles = build_player_profiles(raw_df)

teams = sorted(team_profiles["team"].dropna().unique())


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("### MATCHUP CONTROLS")
team_a = st.sidebar.selectbox("Select Team A", teams, index=0)
team_b = st.sidebar.selectbox("Select Team B", teams, index=1 if len(teams) > 1 else 0)

if team_a == team_b:
    st.warning("Select two different teams.")
    st.stop()


# ============================================================
# SELECTED DATA
# ============================================================

api_matchup_data = get_matchup_from_api(team_a, team_b)


row_a = team_profiles[team_profiles["team"] == team_a].iloc[0]
row_b = team_profiles[team_profiles["team"] == team_b].iloc[0]

lineup_a = get_projected_lineup(team_a, player_profiles, starters_df)
lineup_b = get_projected_lineup(team_b, player_profiles, starters_df)

lineup_profile_a = calculate_lineup_profile(lineup_a)
lineup_profile_b = calculate_lineup_profile(lineup_b)

edge = determine_matchup_edge(team_a, team_b, row_a, row_b)
confidence = confidence_score(row_a, row_b)

# Use API data for header if available, else fall back to local logic
if api_matchup_data and isinstance(api_matchup_data, dict):

    # Extract team names from "matchup"
    matchup_str = api_matchup_data.get("matchup", "")
    if " vs " in matchup_str:
        api_team_a, api_team_b = matchup_str.split(" vs ")
    else:
        api_team_a, api_team_b = team_a, team_b

    # Get edge from team_advantages
    advantages = api_matchup_data.get("team_advantages", [])
    if advantages:
        api_edge = advantages[0].get("advantage", edge)
    else:
        api_edge = edge

    # No confidence in API -> keep local
    api_confidence = confidence

else:
    api_team_a = team_a
    api_team_b = team_b
    api_edge = edge
    api_confidence = confidence


color_a = get_team_color(team_a)
color_b = get_team_color(team_b)

# Helper to get logo path or None
def get_logo_uri(team):
    logo_path = get_logo_path(team)
    if logo_path and logo_path.exists():
        try:
            return image_to_data_uri(logo_path)
        except Exception:
            return None
    return None

logo_a_uri = get_logo_uri(team_a)
logo_b_uri = get_logo_uri(team_b)

def initials_badge(team, color):
    initials = "?" if not team or not isinstance(team, str) or team.strip() == "" else "".join([word[0] for word in team.split()[:2]]).upper()
    return f'<div class="logo-circle" style="background:{color};">{initials}</div>'

team_a_players = player_profiles[player_profiles["team"] == team_a].sort_values("MIN", ascending=False)
team_b_players = player_profiles[player_profiles["team"] == team_b].sort_values("MIN", ascending=False)

factors = generate_matchup_factors(team_a, team_b, row_a, row_b)

if api_matchup_data:
    st.sidebar.success("FastAPI connected")
else:
    st.sidebar.warning("Using local Streamlit logic")

# ============================================================
# HEADER
# ============================================================


# Render hero card with Streamlit columns and st.image for logos
st.markdown("""
<div class="app-kicker">WNBA 2026 · MATCHUP SCOUTING · LINEUP INTELLIGENCE</div>

<div class="main-title">MATCHUP INTELLIGENCE</div>

<div class="subtitle">
Team profiles, projected lineups, player roles, matchup factors, and scouting notes.
</div>

<div style="
    color:#94a3b8;
    font-size:13px;
    letter-spacing:.8px;
    margin-top:8px;
    margin-bottom:12px;
">
Created by Michael Ozomah * Independent Basketball Analytics
</div>

<div class="gold-line"></div>

<div class="hero-card" style="margin-bottom:28px;">
</div>
""", unsafe_allow_html=True)

team_a_record = get_team_record(team_games_df, team_a)
team_b_record = get_team_record(team_games_df, team_b)

identity_a = get_team_identity(team_a)
identity_b = get_team_identity(team_b)

hero_cols = st.columns([1.2, 2, 1.2])
with hero_cols[0]:
    if logo_a_uri:
        st.image(logo_a_uri, width=110)
    else:
        st.markdown(initials_badge(team_a, color_a), unsafe_allow_html=True)

    st.markdown(
        f'<h2 style="color:{color_a}!important;">{team_a}</h2>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="team-record">{team_a_record}</div>',
        unsafe_allow_html=True
    )


with hero_cols[1]:
    st.markdown(
        '<div class="app-kicker">HEAD-TO-HEAD REPORT</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<h2>{team_a} vs {team_b}</h2>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<h3 style="color:#D6A84F!important;">EDGE: {edge}</h3>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div style="font-family:Oswald;font-size:24px;font-weight:800;">CONFIDENCE: {confidence}%</div>',
        unsafe_allow_html=True
    )


with hero_cols[2]:
    if logo_b_uri:
        st.image(logo_b_uri, width=110)
    else:
        st.markdown(initials_badge(team_b, color_b), unsafe_allow_html=True)

    st.markdown(
        f'<h2 style="color:{color_b}!important;">{team_b}</h2>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="team-record">{team_b_record}</div>',
        unsafe_allow_html=True
    )



# ============================================================
# TABS
# ============================================================

matchup_tab, lineup_tab, players_tab, intelligence_tab = st.tabs(
    ["MATCHUP", "LINEUPS", "PLAYERS", "INTELLIGENCE"]
)


# ============================================================
# MATCHUP TAB
# ============================================================

with matchup_tab:
    st.markdown("<h2>Team Matchup Comparison</h2>", unsafe_allow_html=True)
    st.plotly_chart(matchup_bar_chart(team_a, team_b, row_a, row_b), use_container_width=True)

    st.markdown("<h2>Matchup Verdict</h2>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="verdict-card">
            <div class="app-kicker">MODEL READ</div>
            <h2 style="margin-top:0;">{edge}</h2>
            <p style="font-size:17px;">
            This edge is based on scoring pressure, glass control, creation flow, and defensive disruption.
            The goal is not certainty -- it is identifying which team owns more matchup leverage.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        render_snapshot(team_a, row_a)
    with col2:
        render_snapshot(team_b, row_b)

    st.markdown("<h2>Matchup Factors</h2>", unsafe_allow_html=True)
    st.plotly_chart(factor_bar_chart(factors, team_a, team_b), use_container_width=True)

    st.markdown("<h2>Matchup Insights</h2>", unsafe_allow_html=True)
    # Use FastAPI data for matchup insights and advantages if available
    if api_matchup_data and isinstance(api_matchup_data, dict):
        api_insights = api_matchup_data.get("matchup_insights")
        api_advantages = api_matchup_data.get("team_advantages")
        if api_insights and isinstance(api_insights, list):
            for insight in api_insights:
                # If API insight is a dict with tag/text, render as before
                if isinstance(insight, dict) and "tag" in insight and "text" in insight:
                    st.markdown(f"<div class='insight-card'><b>{insight['tag']}</b>: {insight['text']}</div>", unsafe_allow_html=True)
                else:
                    # Otherwise, treat as plain text
                    st.markdown(f"<div class='insight-card'>{insight}</div>", unsafe_allow_html=True)
        elif api_advantages and isinstance(api_advantages, list):
            for adv in api_advantages:
                tag = adv.get("type", "ADVANTAGE")
                text = adv.get("advantage", str(adv))
                st.markdown(f"<div class='insight-card'><b>{tag}</b>: {text}</div>", unsafe_allow_html=True)
        else:
            # Fallback to local logic if API keys missing
            for tag, text in generate_matchup_insights(team_a, team_b, row_a, row_b):
                st.markdown(f"<div class='insight-card'><b>{tag}</b>: {text}</div>", unsafe_allow_html=True)
    else:
        for tag, text in generate_matchup_insights(team_a, team_b, row_a, row_b):
            st.markdown(f"<div class='insight-card'><b>{tag}</b>: {text}</div>", unsafe_allow_html=True)


# ============================================================
# LINEUPS TAB
# ============================================================

with lineup_tab:
    st.markdown("<h2>Projected Starters Scouting Report</h2>", unsafe_allow_html=True)

    lineup_col1, lineup_col2 = st.columns(2)

    with lineup_col1:
        st.markdown(f"<h3>{team_a}</h3>", unsafe_allow_html=True)
        for _, player in lineup_a.iterrows():
            render_player_scouting_card(player, expanded=True)

    with lineup_col2:
        st.markdown(f"<h3>{team_b}</h3>", unsafe_allow_html=True)
        for _, player in lineup_b.iterrows():
            render_player_scouting_card(player, expanded=True)

    st.markdown("<h2>Lineup vs Lineup Breakdown</h2>", unsafe_allow_html=True)

    for label, a_val, b_val, winner in lineup_vs_lineup_summary(team_a, team_b, lineup_profile_a, lineup_profile_b):
        st.markdown(
            f"""
            <div class="section-card">
                <div class="app-kicker">{label}</div>
                <h3>{team_a}: {a_val:.2f} &nbsp; | &nbsp; {team_b}: {b_val:.2f}</h3>
                <p><b style="color:#D6A84F!important;">EDGE:</b> {winner}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<h2>Lineup Identity</h2>", unsafe_allow_html=True)

    identity_col1, identity_col2 = st.columns(2)

    with identity_col1:
        st.markdown(f"<h3>{team_a}</h3>", unsafe_allow_html=True)
        for insight in generate_lineup_identity(team_a, lineup_profile_a):
            st.markdown(f"<div class='insight-card'>{insight}</div>", unsafe_allow_html=True)

    with identity_col2:
        st.markdown(f"<h3>{team_b}</h3>", unsafe_allow_html=True)
        for insight in generate_lineup_identity(team_b, lineup_profile_b):
            st.markdown(f"<div class='insight-card'>{insight}</div>", unsafe_allow_html=True)


# ============================================================
# PLAYERS TAB
# ============================================================

render_pro_matchup_history(
    team_games_df,
    team_a,
    team_b
)

with players_tab:
    st.markdown("<h2>Player Radar Comparison</h2>", unsafe_allow_html=True)

    radar_col1, radar_col2 = st.columns(2)

    with radar_col1:
        player_a_name = st.selectbox(
            f"Select {team_a} Player",
            team_a_players["player_name"].tolist(),
            key="player_a_select"
        )

    with radar_col2:
        player_b_name = st.selectbox(
            f"Select {team_b} Player",
            team_b_players["player_name"].tolist(),
            key="player_b_select"
        )

    player_a_row = team_a_players[team_a_players["player_name"] == player_a_name].iloc[0]
    player_b_row = team_b_players[team_b_players["player_name"] == player_b_name].iloc[0]

    st.plotly_chart(
        player_radar_chart(player_a_row, player_b_row, team_a, team_b),
        use_container_width=True
    )

    st.markdown("<h2>Selected Player Reports</h2>", unsafe_allow_html=True)

    player_report_col1, player_report_col2 = st.columns(2)
    with player_report_col1:
        render_player_trend(player_a_name, raw_df)
        render_player_scouting_card(player_a_row, expanded=True)

    with player_report_col2:
        render_player_trend(player_b_name, raw_df)
        render_player_scouting_card(player_b_row, expanded=True)

    st.markdown("<h2>Top Rotation Scouting</h2>", unsafe_allow_html=True)

    rot_col1, rot_col2 = st.columns(2)

    with rot_col1:
        st.markdown(f"<h3>{team_a}</h3>", unsafe_allow_html=True)
        for _, player in team_a_players.head(8).iterrows():
            render_rotation_card(player)

    with rot_col2:
        st.markdown(f"<h3>{team_b}</h3>", unsafe_allow_html=True)
        for _, player in team_b_players.head(8).iterrows():
            render_rotation_card(player)


# ============================================================
# INTELLIGENCE TAB
# ============================================================

with intelligence_tab:
    st.markdown("<h2>Game Script Projection</h2>", unsafe_allow_html=True)

    for line in generate_game_script(team_a, team_b, row_a, row_b):
        st.markdown(f"<div class='insight-card'>{line}</div>", unsafe_allow_html=True)

    st.markdown("<h2>What To Watch</h2>", unsafe_allow_html=True)

    for item in generate_what_to_watch(team_a, team_b, row_a, row_b):
        st.markdown(f"<div class='warning-card'>{item}</div>", unsafe_allow_html=True)

    st.markdown("<h2>Scouting Summary</h2>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="section-card">
            <div class="app-kicker">{team_a}</div>
            <h3>{team_a} wins if...</h3>
            <p>{team_a} controls its strongest statistical advantages and prevents {team_b} from forcing the game into its preferred rhythm.</p>
            <hr>
            <div class="app-kicker">{team_b}</div>
            <h3>{team_b} wins if...</h3>
            <p>{team_b} wins the swing categories, limits transition moments, and neutralizes the primary matchup edges shown above.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
