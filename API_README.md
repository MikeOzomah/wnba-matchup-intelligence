# WNBA Matchup API

A FastAPI-based REST API that converts your `matchup_engine.py` script into queryable endpoints returning JSON.

## Files

- **`fastapi_app.py`** - FastAPI application with the `/report/{input_value}` endpoint
- **`scripts/matchup_api.py`** - Core logic: `get_report(matchup_input)` function
- **`test_api.py`** - Test suite for the API

## Quick Start

### 1. Install dependencies
```bash
pip install fastapi uvicorn httpx
```

### 2. Run the server
```bash
uvicorn fastapi_app:app --port 8000
```

The API will be available at `http://localhost:8000`

### 3. Use the API

#### Browser / Curl
```bash
curl "http://localhost:8000/report/Dallas%20Wings_vs_Indiana%20Fever"
```

#### Python
```python
from scripts.matchup_api import get_report
import json

result = get_report("Dallas Wings vs Indiana Fever")
print(json.dumps(result, indent=2))
```

#### JavaScript / Fetch
```javascript
fetch('/report/Dallas%20Wings_vs_Indiana%20Fever')
  .then(r => r.json())
  .then(data => console.log(data))
```

## API Documentation

### Endpoint: `/report/{input_value}`

**Method:** `GET`

**Parameters:**
- `input_value` (string, path): Teams in format `Team+A_vs_Team+B`
  - URL encode spaces as `%20`
  - Use underscores `_` as separators (not spaces directly)
  - Example: `Dallas%20Wings_vs_Indiana%20Fever`

**Response (200):**
```json
{
  "matchup": "Team A vs Team B",
  "team_stats": {
    "Team A": {
      "points_per_game": 89.5,
      "rebounds_per_game": 30.5,
      "assists_per_game": 20.5,
      "steals_per_game": 6.0,
      "blocks_per_game": 3.0,
      "games_played": 2
    },
    "Team B": { ... }
  },
  "team_advantages": [
    { "metric": "Scoring", "advantage": "Team A" },
    { "metric": "Rebounding", "advantage": "Team B" },
    ...
  ],
  "matchup_insights": [
    "Team A has the stronger team scoring profile.",
    ...
  ],
  "lineups": {
    "Team A": [
      {
        "player": "Player Name",
        "position": "G",
        "pts": 15.2,
        "ast": 3.4,
        "reb": 4.1,
        "stl": 1.2,
        "blk": 0.5
      },
      ...
    ],
    "Team B": [ ... ]
  },
  "lineup_profiles": {
    "Team A": {
      "scoring": 12.5,
      "playmaking": 3.2,
      "rebounding": 6.1,
      "defensive_activity": 2.3
    },
    "Team B": { ... }
  },
  "lineup_context": {
    "Team A": [
      "Team A's projected lineup has strong individual scoring punch.",
      ...
    ],
    "Team B": [ ... ]
  },
  "warnings": {
    "Team A": [],
    "Team B": ["Missing Player Name", ...]
  }
}
```

**Error Response (400):**
```json
{
  "error": "Team not found. Available teams: [...]",
  "available_teams": ["Team A", "Team B", ...]
}
```

## Testing

Run the test suite:
```bash
python test_api.py
```

This will test:
1. Direct function calls
2. Available teams
3. API endpoint (if server is running)

## Interactive Docs

When the server is running, visit:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

These provide interactive documentation and allow you to test endpoints directly.

## Next Steps

- Add a React/Vue frontend to consume this API
- Add database caching to avoid repeated CSV reads
- Add authentication if needed
- Add more endpoints for player profiles, team stats, etc.
