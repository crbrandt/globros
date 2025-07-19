import pandas as pd
import os
from datetime import datetime
from config import PLAYERS

# Daily placements CSV path
PLACEMENTS_CSV_PATH = "data/daily_placements.csv"
PLACEMENTS_COLUMNS = ["date", "player", "placement", "total_score", "participants"]

def ensure_placements_csv_exists():
    """
    Create the daily placements CSV file with headers if it doesn't exist.
    Only creates empty file if no file exists at all.
    """
    if not os.path.exists(PLACEMENTS_CSV_PATH):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(PLACEMENTS_CSV_PATH), exist_ok=True)
        
        # Create empty DataFrame with proper columns
        df = pd.DataFrame(columns=PLACEMENTS_COLUMNS)
        df.to_csv(PLACEMENTS_CSV_PATH, index=False)
        print(f"Created empty placements CSV file: {PLACEMENTS_CSV_PATH}")
    else:
        print(f"Placements CSV file already exists: {PLACEMENTS_CSV_PATH}")

def save_daily_placements(date, results):
    """
    Save daily placements for all participating players.
    
    Args:
        date (str): Date in YYYY-MM-DD format
        results (dict): Results from scoring_engine.calculate_daily_results
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ensure_placements_csv_exists()
        
        # Get participating players with their scores
        participating_players = []
        player_scores = []
        for i, player in enumerate(PLAYERS):
            participated = any(
                results["raw_scores"][game][i] is not None 
                for game in results["raw_scores"]
            )
            if participated:
                participating_players.append(player)
                player_scores.append((player, results["total_scores"][i]))
        
        # Sort by total score (lower is better)
        player_scores.sort(key=lambda x: x[1])
        
        # Create placement data with proper tie handling
        rows = []
        current_rank = 1
        prev_score = None
        
        for i, (player, score) in enumerate(player_scores):
            # If this score is different from previous, update rank
            if prev_score is not None and score != prev_score:
                current_rank = i + 1
            
            rows.append({
                "date": date,
                "player": player,
                "placement": current_rank,
                "total_score": score,
                "participants": ",".join(participating_players)
            })
            prev_score = score
        
        # Convert to DataFrame
        new_data = pd.DataFrame(rows)
        
        # Read existing data
        existing_data = pd.read_csv(PLACEMENTS_CSV_PATH)
        
        # Remove any existing data for this date (in case of updates)
        existing_data = existing_data[existing_data["date"] != date]
        
        # Combine and save
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        combined_data.to_csv(PLACEMENTS_CSV_PATH, index=False)
        
        return True
    
    except Exception as e:
        print(f"Error saving placements data: {e}")
        import traceback
        traceback.print_exc()
        return False

# Keep the old function name for backward compatibility
def save_daily_winner(date, results):
    """Backward compatibility wrapper."""
    return save_daily_placements(date, results)

def load_daily_placements():
    """
    Load daily placements data.
    
    Returns:
        pd.DataFrame: Daily placements data
    """
    try:
        if os.path.exists(PLACEMENTS_CSV_PATH):
            df = pd.read_csv(PLACEMENTS_CSV_PATH)
            print(f"Loaded placements CSV with {len(df)} rows from {PLACEMENTS_CSV_PATH}")
            if len(df) > 0:
                print(f"Placements data: {df.head()}")
            return df
        else:
            print(f"Placements CSV file does not exist: {PLACEMENTS_CSV_PATH}")
            ensure_placements_csv_exists()
            return pd.DataFrame(columns=PLACEMENTS_COLUMNS)
    except Exception as e:
        print(f"Error loading placements data: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame(columns=PLACEMENTS_COLUMNS)

# Keep the old function name for backward compatibility
def load_daily_winners():
    """Backward compatibility wrapper - returns winners only (placement = 1)."""
    try:
        placements_df = load_daily_placements()
        if placements_df.empty:
            return pd.DataFrame(columns=["date", "winner"])
        
        # Filter to only winners (placement = 1) and rename column
        winners_df = placements_df[placements_df["placement"] == 1].copy()
        winners_df = winners_df.rename(columns={"player": "winner"})
        return winners_df[["date", "winner"]]
    except Exception as e:
        print(f"Error loading winners data: {e}")
        return pd.DataFrame(columns=["date", "winner"])
