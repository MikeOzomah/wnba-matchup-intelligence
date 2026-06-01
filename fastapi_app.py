from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

from scripts.matchup_api import get_report
from scripts.core_engine import (
    get_team_profile,
    get_player_profile,
    get_matchup_report,
    get_lineup_analysis,
    get_team_style
)
from scripts import player_matchup_engine

app = FastAPI(
    title="WNBA Matchup API",
    description="Generate WNBA team matchup reports",
    version="1.0.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "WNBA Matchup API",
        "usage": "GET /report/{team_a}_vs_{team_b}",
        "example": "GET /report/Dallas%20Wings_vs_Indiana%20Fever"
    }


@app.get("/report/{input_value}")
async def report(input_value: str):
    """
    Generate a matchup report for two teams.
    
    Provide teams in format: Team+A_vs_Team+B or use URL encoding for spaces.
    Example: Dallas%20Wings_vs_Indiana%20Fever
    """
    # Convert underscores back to spaces
    formatted_input = input_value.replace("_", " ")
    
    result = get_report(formatted_input)
    
    return result


@app.get("/team/{team_name}")
async def team_profile(team_name: str):
    result = get_team_profile(team_name)
    if not result["data"]:
        raise HTTPException(status_code=404, detail=result["warning"] or "Team not found.")
    return result

@app.get("/player/{player_name}")
async def player_profile(player_name: str):
    result = get_player_profile(player_name)
    if not result["data"]:
        raise HTTPException(status_code=404, detail=result["warning"] or "Player not found.")
    return result

@app.get("/matchup/{team_a}/{team_b}")
async def matchup_report(team_a: str, team_b: str):
    result = get_matchup_report(team_a, team_b)
    if not result["data"]:
        raise HTTPException(status_code=404, detail=result["warning"] or "Matchup not found.")
    return result

@app.get("/lineup/{team_name}")
async def lineup_analysis(team_name: str):
    result = get_lineup_analysis(team_name)
    if not result["data"]:
        raise HTTPException(status_code=404, detail=result["warning"] or "Lineup not found.")
    return result

@app.get("/style/{team_name}")
async def team_style(team_name: str):
    result = get_team_style(team_name)
    if not result["data"]:
        raise HTTPException(status_code=404, detail=result["warning"] or "Style not found.")
    return result

@app.get("/player-matchup/{player_name}/{opponent_team}")
async def player_matchup(player_name: str, opponent_team: str):
    """
    Analyze a player's matchup against an opponent team.
    Returns JSON with player info, team info, archetypes, and matchup keys.
    """
    try:
        player_row = player_matchup_engine.get_player_row(player_name)
    except SystemExit:
        raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading player: {str(e)}")

    try:
        team_row = player_matchup_engine.get_team_row(opponent_team)
    except SystemExit:
        raise HTTPException(status_code=404, detail=f"Opponent team '{opponent_team}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading team: {str(e)}")

    try:
        archetypes = player_matchup_engine.classify_archetypes(player_row)
        keys = player_matchup_engine.generate_matchup_keys(
            player_name,
            team_row["team"],
            archetypes,
            team_row
        )
        summary = player_matchup_engine.generate_archetype_summary(
            player_name,
            player_row["team"],
            archetypes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating matchup analysis: {str(e)}")

    return {
        "player": player_name,
        "player_team": player_row["team"],
        "opponent_team": team_row["team"],
        "archetypes": archetypes,
        "player_summary": summary,
        "matchup_keys": keys,
        "player_stats": {k: player_row[k] for k in player_row.index if k not in ("player", "team")},
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
