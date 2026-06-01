# Test import and function call for player_matchup_engine.py
from scripts import player_matchup_engine

def test_import_and_function():
    # Should not print or run anything on import
    # Test get_player_row (will fail gracefully if player not found)
    try:
        row = player_matchup_engine.get_player_row("Alyssa Thomas")
        print("get_player_row works. Example output:", row.to_dict())
    except Exception as e:
        print("get_player_row failed:", e)

if __name__ == "__main__":
    test_import_and_function()
