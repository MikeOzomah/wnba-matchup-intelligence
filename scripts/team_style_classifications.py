import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parent / "outputs"
INPUT_FILE = OUTPUT_DIR / "defensive_metrics.csv"
STYLE_OUTPUT_FILE = OUTPUT_DIR / "team_style_classifications.csv"
REFERENCE_OUTPUT_FILE = OUTPUT_DIR / "team_style_threshold_reference.csv"

# Load defensive metrics dataset
if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

# Group by team averages
metrics = [
    "possessions",
    "shot_value",
    "offensive_flow",
    "ball_security",
    "defensive_pressure",
    "offensive_rating"
]

team_profiles = df.groupby("team")[metrics].mean().round(3)
team_profiles = team_profiles.reset_index()

# Calculate percentiles using the current league distribution
quantiles = team_profiles[metrics].quantile([0.25, 0.5, 0.75, 0.9])
quantiles.index = ["bottom_25", "median", "top_25", "elite_range"]

reference_df = pd.DataFrame({
    "league_average": team_profiles[metrics].mean(),
    "bottom_25": quantiles.loc["bottom_25"],
    "median": quantiles.loc["median"],
    "top_25": quantiles.loc["top_25"],
    "elite_range": quantiles.loc["elite_range"],
})
reference_df = reference_df.round(3)
reference_df.to_csv(REFERENCE_OUTPUT_FILE)

print("\nWNBA TEAM STYLE THRESHOLDS REFERENCE")
print(reference_df.to_string())
print(f"\nSaved reference thresholds to: {REFERENCE_OUTPUT_FILE}\n")

# Define percentile-based thresholds
thresholds = {
    "possessions": quantiles["possessions"],
    "shot_value": quantiles["shot_value"],
    "offensive_flow": quantiles["offensive_flow"],
    "ball_security": quantiles["ball_security"],
    "defensive_pressure": quantiles["defensive_pressure"],
    "offensive_rating": quantiles["offensive_rating"],
}

# Category helpers

def classify_tempo(value):
    if value >= thresholds["possessions"]["elite_range"]:
        return "Elite Fast Tempo"
    if value >= thresholds["possessions"]["top_25"]:
        return "Fast Tempo"
    if value >= thresholds["possessions"]["bottom_25"]:
        return "Balanced Tempo"
    return "Controlled Tempo"


def classify_shot(value):
    if value >= thresholds["shot_value"]["elite_range"]:
        return "Elite Shot Creation"
    if value >= thresholds["shot_value"]["top_25"]:
        return "High Value Shot Creation"
    if value >= thresholds["shot_value"]["bottom_25"]:
        return "Balanced Shot Profile"
    return "Difficult Shot Environment"


def classify_flow(value):
    if value >= thresholds["offensive_flow"]["elite_range"]:
        return "Elite Offensive Flow"
    if value >= thresholds["offensive_flow"]["top_25"]:
        return "Connected Offensive Flow"
    if value >= thresholds["offensive_flow"]["bottom_25"]:
        return "Moderate Ball Movement"
    return "Stagnant Offensive Flow"


def classify_security(value):
    if value >= thresholds["ball_security"]["elite_range"]:
        return "Elite Ball Security"
    if value >= thresholds["ball_security"]["top_25"]:
        return "Strong Ball Security"
    if value >= thresholds["ball_security"]["bottom_25"]:
        return "Average Ball Protection"
    return "Turnover Vulnerable"


def classify_defense(value):
    if value >= thresholds["defensive_pressure"]["elite_range"]:
        return "Elite Defensive Pressure"
    if value >= thresholds["defensive_pressure"]["top_25"]:
        return "Aggressive Defensive Pressure"
    if value >= thresholds["defensive_pressure"]["bottom_25"]:
        return "Active Defensive Presence"
    return "Low Disruption Defense"


def classify_offense(value):
    if value >= thresholds["offensive_rating"]["elite_range"]:
        return "Elite Offensive Efficiency"
    if value >= thresholds["offensive_rating"]["top_25"]:
        return "Strong Offensive Production"
    if value >= thresholds["offensive_rating"]["bottom_25"]:
        return "Average Offensive Production"
    return "Developing Offensive Structure"

# Store style outputs here
style_rows = []

print("\nWNBA TEAM STYLE CLASSIFICATIONS\n")

for _, row in team_profiles.iterrows():
    team = row["team"]
    possessions = row["possessions"]
    shot_value = row["shot_value"]
    offensive_flow = row["offensive_flow"]
    ball_security = row["ball_security"]
    defensive_pressure = row["defensive_pressure"]
    offensive_rating = row["offensive_rating"]

    if pd.isna(offensive_rating):
        continue

    tempo_style = classify_tempo(possessions)
    shot_profile = classify_shot(shot_value)
    flow_profile = classify_flow(offensive_flow)
    security_profile = classify_security(ball_security)
    defense_profile = classify_defense(defensive_pressure)
    offense_profile = classify_offense(offensive_rating)

    style_rows.append({
        "team": team,
        "possessions": possessions,
        "shot_value": shot_value,
        "offensive_flow": offensive_flow,
        "ball_security": ball_security,
        "defensive_pressure": defensive_pressure,
        "offensive_rating": offensive_rating,
        "tempo_style": tempo_style,
        "shot_profile": shot_profile,
        "flow_profile": flow_profile,
        "security_profile": security_profile,
        "defense_profile": defense_profile,
        "offense_profile": offense_profile,
    })

    print(f"{team}")
    print("-" * 50)
    print(f"Tempo Style: {tempo_style}")
    print(f"Shot Profile: {shot_profile}")
    print(f"Offensive Style: {flow_profile}")
    print(f"Ball Security: {security_profile}")
    print(f"Defense: {defense_profile}")
    print(f"Offensive Identity: {offense_profile}")
    print("\n")

# Convert style rows into DataFrame
style_df = pd.DataFrame(style_rows)

# Save classifications
style_df.to_csv(STYLE_OUTPUT_FILE, index=False)
print(f"Team style classifications saved successfully to: {STYLE_OUTPUT_FILE}")