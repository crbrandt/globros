import pandas as pd
import os
from datetime import datetime
from config import CSV_FILE_PATH, CSV_COLUMNS, PLAYERS, GAMES

def ensure_csv_exists():
    """
    Create the CSV file with headers if it doesn't exist.
    Only creates empty file if no file exists at all.
    """
    if not os.path.exists(CSV_FILE_PATH):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)
        
        # Create empty DataFrame with proper columns
        df = pd.DataFrame(columns=CSV_COLUMNS)
        df.to_csv(CSV_FILE_PATH, index=False)
        print(f"Created empty CSV file: {CSV_FILE_PATH}")
    else:
        print(f"CSV file already exists: {CSV_FILE_PATH}")

def save_daily_results(date, results):
    """
    Save daily results to CSV file.
    
    Args:
        date (str): Date in YYYY-MM-DD format
        results (dict): Results from scoring_engine.calculate_daily_results
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ensure_csv_exists()
        
        # Prepare data for CSV
        rows = []
        
        for game in GAMES.keys():
            if game in results["raw_scores"]:
                for i, player in enumerate(PLAYERS):
                    # Handle None values properly for CSV storage
                    raw_score = results["raw_scores"][game][i]
                    norm_unweighted = results["normalized_unweighted"][game][i]
                    norm_weighted = results["normalized_weighted"][game][i]
                    
                    row = {
                        "date": date,
                        "game": game,
                        "player": player,
                        "raw_score": raw_score if raw_score is not None else "",
                        "normalized_unweighted_score": norm_unweighted if norm_unweighted is not None else "",
                        "normalized_weighted_score": norm_weighted if norm_weighted is not None else ""
                    }
                    rows.append(row)
        
        # Convert to DataFrame
        new_data = pd.DataFrame(rows)
        
        # Read existing data
        existing_data = pd.read_csv(CSV_FILE_PATH)
        
        # Remove any existing data for this date (in case of updates)
        existing_data = existing_data[existing_data["date"] != date]
        
        # Combine and save
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        combined_data.to_csv(CSV_FILE_PATH, index=False)
        
        return True
    
    except Exception as e:
        print(f"Error saving data: {e}")
        import traceback
        traceback.print_exc()
        return False

def load_historical_data():
    """
    Load all historical data from CSV.
    
    Returns:
        pd.DataFrame: Historical data or empty DataFrame if file doesn't exist
    """
    try:
        ensure_csv_exists()
        return pd.read_csv(CSV_FILE_PATH)
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=CSV_COLUMNS)

def get_daily_winners():
    """
    Get list of daily winners from historical data.
    
    Returns:
        pd.DataFrame: DataFrame with date and winner columns
    """
    try:
        df = load_historical_data()
        if df.empty:
            return pd.DataFrame(columns=["date", "winner"])
        
        # Group by date and calculate total scores for each player
        daily_totals = df.groupby(["date", "player"])["normalized_weighted_score"].sum().reset_index()
        
        # Find winner for each date (lowest total score)
        winners = daily_totals.loc[daily_totals.groupby("date")["normalized_weighted_score"].idxmin()]
        winners = winners[["date", "player"]].rename(columns={"player": "winner"})
        
        return winners.sort_values("date")
    
    except Exception as e:
        print(f"Error getting daily winners: {e}")
        return pd.DataFrame(columns=["date", "winner"])

def get_player_statistics():
    """
    Calculate comprehensive player statistics.
    
    Returns:
        dict: Dictionary with various statistics
    """
    try:
        df = load_historical_data()
        if df.empty:
            return {}
        
        winners_df = get_daily_winners()
        
        stats = {
            "total_games_played": len(df["date"].unique()),
            "win_counts": winners_df["winner"].value_counts().to_dict(),
            "average_scores_by_game": {},
            "player_performance_trends": {},
            "game_difficulty_analysis": {}
        }
        
        # Average scores by game and player
        for game in GAMES.keys():
            game_data = df[df["game"] == game]
            if not game_data.empty:
                avg_scores = game_data.groupby("player")["raw_score"].mean().to_dict()
                stats["average_scores_by_game"][game] = avg_scores
        
        # Player performance trends (total weighted scores over time)
        daily_totals = df.groupby(["date", "player"])["normalized_weighted_score"].sum().reset_index()
        for player in PLAYERS:
            player_data = daily_totals[daily_totals["player"] == player].sort_values("date")
            stats["player_performance_trends"][player] = {
                "dates": player_data["date"].tolist(),
                "scores": player_data["normalized_weighted_score"].tolist()
            }
        
        # Game difficulty analysis (average raw scores)
        for game in GAMES.keys():
            game_data = df[df["game"] == game]
            if not game_data.empty:
                stats["game_difficulty_analysis"][game] = {
                    "average_score": game_data["raw_score"].mean(),
                    "median_score": game_data["raw_score"].median(),
                    "std_dev": game_data["raw_score"].std()
                }
        
        return stats
    
    except Exception as e:
        print(f"Error calculating statistics: {e}")
        return {}

def check_date_exists(date):
    """
    Check if data for a specific date already exists.
    
    Args:
        date (str): Date in YYYY-MM-DD format
    
    Returns:
        bool: True if data exists for this date
    """
    try:
        df = load_historical_data()
        return date in df["date"].values
    except:
        return False

def delete_date_data(date):
    """
    Delete all data for a specific date.
    
    Args:
        date (str): Date in YYYY-MM-DD format
    
    Returns:
        bool: True if successful
    """
    try:
        ensure_csv_exists()
        df = pd.read_csv(CSV_FILE_PATH)
        df = df[df["date"] != date]
        df.to_csv(CSV_FILE_PATH, index=False)
        return True
    except Exception as e:
        print(f"Error deleting data: {e}")
        return False
