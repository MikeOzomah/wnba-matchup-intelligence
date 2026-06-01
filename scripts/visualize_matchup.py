import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PLAYER_STATS_FILE = BASE_DIR / "data" / "player_box_scores.csv"

TEAM_COLORS = {
    "Atlanta Dream": "#E31837",
    "Chicago Sky": "#418FDE",
    "Connecticut Sun": "#F05023",
    "Dallas Wings": "#002B5C",
    "Golden State Valkyries": "#6A0DAD",
    "Indiana Fever": "#C8102E",
    "Las Vegas Aces": "#000000",
    "Los Angeles Sparks": "#FDB927",
    "Minnesota Lynx": "#005083",
    "New York Liberty": "#86CEBC",
    "Phoenix Mercury": "#E56020",
    "Portland Fire": "#C8102E",
    "Seattle Storm": "#2C5234",
    "Toronto Tempo": "#6C1D45",
    "Washington Mystics": "#002B5C",
}


def load_player_stats():
    df = pd.read_csv(PLAYER_STATS_FILE)

    df = df.rename(columns={
        "player": "player_name",
        "pts": "PTS",
        "reb": "REB",
        "ast": "AST",
        "stl": "STL",
        "blk": "BLK",
    })

    for col in ["PTS", "REB", "AST", "STL", "BLK"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df[
        df["season_phase"]
        .astype(str)
        .str.lower()
        .str.contains("regular")
    ].copy()

    return df


def build_team_profiles(df):
    game_totals = df.groupby(["team", "game_id"], as_index=False).agg({
        "PTS": "sum",
        "REB": "sum",
        "AST": "sum",
        "STL": "sum",
        "BLK": "sum",
    })

    team_profiles = game_totals.groupby("team", as_index=False).agg({
        "PTS": "mean",
        "REB": "mean",
        "AST": "mean",
        "STL": "mean",
        "BLK": "mean",
    })

    return team_profiles


def plot_matchup(team_a, team_b, profiles):
    row_a = profiles[profiles["team"] == team_a].iloc[0]
    row_b = profiles[profiles["team"] == team_b].iloc[0]

    stats = [
        ("PTS", row_a["PTS"], row_b["PTS"]),
        ("REB", row_a["REB"], row_b["REB"]),
        ("AST", row_a["AST"], row_b["AST"]),
        ("STL", row_a["STL"], row_b["STL"]),
        ("BLK", row_a["BLK"], row_b["BLK"]),
    ]

    color_a = TEAM_COLORS.get(team_a, "#00ffcc")
    color_b = TEAM_COLORS.get(team_b, "#ff3366")

    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.patch.set_facecolor("#0b0b0b")
    ax.set_facecolor("#0b0b0b")
    ax.axis("off")

    max_val = max([max(a, b) for _, a, b in stats]) * 1.3

    ax.set_xlim(-max_val, max_val)
    ax.set_ylim(-0.5, len(stats) + 1.2)

    ax.axvline(0, color="white", linewidth=1, alpha=0.25)

    y = len(stats)

    for label, val_a, val_b in stats:
        # Background track
        ax.barh(y, max_val, color="#161616", height=0.6)
        ax.barh(y, -max_val, color="#161616", height=0.6)

        # Main bars
        ax.barh(y, -val_a, color=color_a, height=0.6, alpha=0.95)
        ax.barh(y, val_b, color=color_b, height=0.6, alpha=0.95)

        winner_a = val_a > val_b
        winner_b = val_b > val_a

        # Center stat label
        ax.text(
            0,
            y,
            label,
            ha="center",
            va="center",
            color="#dddddd",
            fontsize=11,
            weight="bold",
            bbox=dict(facecolor="#111111", edgecolor="none", pad=2),
        )

        # Dynamic spacing to avoid overlap
        offset = max_val * 0.02

        ax.text(
            -val_a - offset,
            y,
            f"{val_a:.1f}",
            ha="right",
            va="center",
            color="#00ff88" if winner_a else "white",
            fontsize=11,
            weight="bold" if winner_a else "normal",
        )

        ax.text(
            val_b + offset,
            y,
            f"{val_b:.1f}",
            ha="left",
            va="center",
            color="#00ff88" if winner_b else "white",
            fontsize=11,
            weight="bold" if winner_b else "normal",
        )

        y -= 1.2

    ax.text(
        -max_val * 0.75,
        len(stats) + 0.75,
        team_a,
        color=color_a,
        fontsize=18,
        weight="bold",
        ha="left",
    )

    ax.text(
        max_val * 0.75,
        len(stats) + 0.75,
        team_b,
        color=color_b,
        fontsize=18,
        weight="bold",
        ha="right",
    )

    plt.title(
        f"{team_a} vs {team_b}",
        color="white",
        fontsize=15,
        pad=18,
        weight="bold",
    )

    plt.tight_layout()
    plt.show()


def choose_team(teams, label):
    print(f"\nAvailable teams for {label}:")
    for team in teams:
        print(f"- {team}")

    return input(f"\nEnter {label}: ").strip()


def main():
    df = load_player_stats()
    profiles = build_team_profiles(df)

    teams = sorted(profiles["team"].unique())

    team_a = choose_team(teams, "Team A")
    team_b = choose_team(teams, "Team B")

    plot_matchup(team_a, team_b, profiles)


if __name__ == "__main__":
    main()