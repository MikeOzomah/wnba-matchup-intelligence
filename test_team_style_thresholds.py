import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT / "scripts"
OUTPUT_DIR = ROOT / "outputs"
STYLE_SCRIPT = SCRIPTS_DIR / "team_style_classifications.py"
STYLE_CSV = OUTPUT_DIR / "team_style_classifications.csv"
REFERENCE_CSV = OUTPUT_DIR / "team_style_threshold_reference.csv"
INPUT_CSV = OUTPUT_DIR / "defensive_metrics.csv"

EXPECTED_STYLE_COLUMNS = {
    "team",
    "possessions",
    "shot_value",
    "offensive_flow",
    "ball_security",
    "defensive_pressure",
    "offensive_rating",
    "tempo_style",
    "shot_profile",
    "flow_profile",
    "security_profile",
    "defense_profile",
    "offense_profile",
}


def run_style_script() -> str:
    result = subprocess.run(
        [sys.executable, str(STYLE_SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Style script failed with return code {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result.stdout


def load_thresholds() -> pd.DataFrame:
    return pd.read_csv(REFERENCE_CSV, index_col=0)


def classify_tempo(value: float, thresholds: pd.Series) -> str:
    if value >= thresholds["elite_range"]:
        return "Elite Fast Tempo"
    if value >= thresholds["top_25"]:
        return "Fast Tempo"
    if value >= thresholds["bottom_25"]:
        return "Balanced Tempo"
    return "Controlled Tempo"


def classify_shot(value: float, thresholds: pd.Series) -> str:
    if value >= thresholds["elite_range"]:
        return "Elite Shot Creation"
    if value >= thresholds["top_25"]:
        return "High Value Shot Creation"
    if value >= thresholds["bottom_25"]:
        return "Balanced Shot Profile"
    return "Difficult Shot Environment"


def classify_flow(value: float, thresholds: pd.Series) -> str:
    if value >= thresholds["elite_range"]:
        return "Elite Offensive Flow"
    if value >= thresholds["top_25"]:
        return "Connected Offensive Flow"
    if value >= thresholds["bottom_25"]:
        return "Moderate Ball Movement"
    return "Stagnant Offensive Flow"


def classify_security(value: float, thresholds: pd.Series) -> str:
    if value >= thresholds["elite_range"]:
        return "Elite Ball Security"
    if value >= thresholds["top_25"]:
        return "Strong Ball Security"
    if value >= thresholds["bottom_25"]:
        return "Average Ball Protection"
    return "Turnover Vulnerable"


def classify_defense(value: float, thresholds: pd.Series) -> str:
    if value >= thresholds["elite_range"]:
        return "Elite Defensive Pressure"
    if value >= thresholds["top_25"]:
        return "Aggressive Defensive Pressure"
    if value >= thresholds["bottom_25"]:
        return "Active Defensive Presence"
    return "Low Disruption Defense"


def classify_offense(value: float, thresholds: pd.Series) -> str:
    if value >= thresholds["elite_range"]:
        return "Elite Offensive Efficiency"
    if value >= thresholds["top_25"]:
        return "Strong Offensive Production"
    if value >= thresholds["bottom_25"]:
        return "Average Offensive Production"
    return "Developing Offensive Structure"


def test_team_style_threshold_reference_file():
    assert INPUT_CSV.exists(), f"Missing input data: {INPUT_CSV}"
    stdout = run_style_script()

    assert STYLE_CSV.exists(), f"Style output not created: {STYLE_CSV}"
    assert REFERENCE_CSV.exists(), f"Reference output not created: {REFERENCE_CSV}"

    thresholds = load_thresholds()
    expected_columns = {"league_average", "bottom_25", "median", "top_25", "elite_range"}
    assert set(thresholds.columns) == expected_columns
    assert not thresholds.isna().any().any(), "Reference thresholds should not contain NaN"

    for metric in ["possessions", "shot_value", "offensive_flow", "ball_security", "defensive_pressure", "offensive_rating"]:
        assert metric in thresholds.index, f"Missing metric in reference thresholds: {metric}"
        assert thresholds.loc[metric, "bottom_25"] <= thresholds.loc[metric, "median"] <= thresholds.loc[metric, "top_25"] <= thresholds.loc[metric, "elite_range"], (
            f"Invalid percentile ordering for {metric}"
        )


def test_team_style_classification_consistency():
    assert STYLE_CSV.exists(), f"Style output not found: {STYLE_CSV}"
    assert REFERENCE_CSV.exists(), f"Reference output not found: {REFERENCE_CSV}"

    classifications = pd.read_csv(STYLE_CSV)
    thresholds = load_thresholds()

    assert set(classifications.columns) >= EXPECTED_STYLE_COLUMNS, "Output CSV is missing expected columns"
    metric_columns = list(EXPECTED_STYLE_COLUMNS - {"team"})
    assert not classifications[metric_columns].isna().all(axis=1).any(), "At least one row has all metrics missing"

    for _, row in classifications.iterrows():
        tempo_thr = thresholds.loc["possessions"]
        shot_thr = thresholds.loc["shot_value"]
        flow_thr = thresholds.loc["offensive_flow"]
        security_thr = thresholds.loc["ball_security"]
        defense_thr = thresholds.loc["defensive_pressure"]
        offense_thr = thresholds.loc["offensive_rating"]

        assert row["tempo_style"] == classify_tempo(row["possessions"], tempo_thr), f"Tempo label mismatch for {row['team']}"
        assert row["shot_profile"] == classify_shot(row["shot_value"], shot_thr), f"Shot profile mismatch for {row['team']}"
        assert row["flow_profile"] == classify_flow(row["offensive_flow"], flow_thr), f"Flow profile mismatch for {row['team']}"
        assert row["security_profile"] == classify_security(row["ball_security"], security_thr), f"Security profile mismatch for {row['team']}"
        assert row["defense_profile"] == classify_defense(row["defensive_pressure"], defense_thr), f"Defense profile mismatch for {row['team']}"
        assert row["offense_profile"] == classify_offense(row["offensive_rating"], offense_thr), f"Offense profile mismatch for {row['team']}"


def test_downstream_column_compatibility():
    assert STYLE_CSV.exists(), f"Style output not found: {STYLE_CSV}"
    df = pd.read_csv(STYLE_CSV)
    assert len(df) > 0, "Team style classifications should contain rows"
    assert set(df.columns) == EXPECTED_STYLE_COLUMNS, f"Unexpected columns: {set(df.columns)}"
    assert df["team"].nunique() == len(df), "Each team should appear once in classifications"


if __name__ == "__main__":
    print("Running team style threshold tests...")
    test_team_style_threshold_reference_file()
    test_team_style_classification_consistency()
    test_downstream_column_compatibility()
    print("All team style threshold tests passed.")
