import pandas as pd
import os
from datetime import datetime
from config import PLAYERS

# Daily winners CSV path
WINNERS_CSV_PATH = "data/daily_winners.csv"
WINNERS_COLUMNS = ["date", "winner", "total_score", "participants"]

def ensure_winners_csv_exists():
    """
    Create the daily winners CSV file with headers if it doesn't exist.
    """
    if not os.path.exists(WINNERS_CSV_PATH):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(WINNERS_CSV_PATH), exist_ok=True)
        
        # Create empty DataFrame with proper columns
        df = pd.DataFrame(columns=WINNERS_COLUMNS)
        df.to_csv(WINNERS_CSV_PATH, index=False)

def save_daily_winner(date, results):
    """
    Save daily winner information to separate CSV.
    
    Args:
        date (str): Date in YYYY-MM-DD format
        results (dict): Results from scoring_engine.calculate_daily_results
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ensure_winners_csv_exists()
        
        # Get participating players
        participating_players = []
        for i, player in enumerate(PLAYERS):
            participated = any(
                results["raw_scores"][game][i] is not None 
                for game in results["raw_scores"]
            )
            if participated:
                participating_players.append(player)
        
        # Prepare winner data
        if results.get("is_tie", False):
            # Handle ties - create entry for each winner
            winners = results["winners"]
            rows = []
            for winner in winners:
                winner_index = PLAYERS.index(winner)
                row = {
                    "date": date,
                    "winner": winner,
                    "total_score": results["total_scores"][winner_index],
                    "participants": ",".join(participating_players)
                }
                rows.append(row)
        else:
            # Single winner
            winner = results["winner"]
            winner_index = PLAYERS.index(winner)
            rows = [{
                "date": date,
                "winner": winner,
                "total_score": results["total_scores"][winner_index],
                "participants": ",".join(participating_players)
            }]
        
        # Convert to DataFrame
        new_data = pd.DataFrame(rows)
        
        # Read existing data
        existing_data = pd.read_csv(WINNERS_CSV_PATH)
        
        # Remove any existing data for this date (in case of updates)
        existing_data = existing_data[existing_data["date"] != date]
        
        # Combine and save
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        combined_data.to_csv(WINNERS_CSV_PATH, index=False)
        
        return True
    
    except Exception as e:
        print(f"Error saving winner data: {e}")
        import traceback
        traceback.print_exc()
        return False

def load_daily_winners():
    """
    Load daily winners data.
    
    Returns:
        pd.DataFrame: Daily winners data
    """
    try:
        ensure_winners_csv_exists()
        return pd.read_csv(WINNERS_CSV_PATH)
    except Exception as e:
        print(f"Error loading winners data: {e}")
        return pd.DataFrame(columns=WINNERS_COLUMNS)
