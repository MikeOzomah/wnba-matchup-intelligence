import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

scripts = [
    "extract_data.py",
    "extract_player_data.py",
    "clean_data.py",
    "clean_player_data.py",
    "advanced_metrics.py",
    "defensive_metrics.py",
    "team_style_classifications.py",
    "player_influence_engine.py",
    "team_player_synergy.py",
    "matchup_analysis.py",
    "style_matchup_engine.py",
    "tactical_consequences.py",
    "matchup_environment_engine.py",
    "player_matchup_engine.py",
]

print("\nStarting full WNBA analytics pipeline...\n")

for script in scripts:
    script_path = SCRIPT_DIR / script
    print(f"Running {script}...")

    if not script_path.exists():
        print(f"\nERROR: Could not find {script_path}")
        sys.exit(1)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(SCRIPT_DIR),
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(f"\nERROR running {script}")
        print(result.stderr)
        sys.exit(result.returncode)

    print(f"{script} completed successfully.\n")

print("Full WNBA analytics pipeline finished.")