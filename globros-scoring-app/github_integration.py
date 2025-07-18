import streamlit as st
import pandas as pd
from github import Github
from datetime import datetime
import io

# GitHub configuration
REPO_NAME = "crbrandt/globros"
SCORES_FILE_PATH = "globros-scoring-app/data/scores_history.csv"
WINNERS_FILE_PATH = "globros-scoring-app/data/daily_winners.csv"
GITHUB_TOKEN = "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"  # Replace with your actual token

def get_github_token():
    """Get GitHub token - hardcoded for simplicity."""
    return GITHUB_TOKEN

def update_github_csv(file_path, new_data, commit_message):
    """
    Update a CSV file in GitHub repository with new data.
    
    Args:
        file_path (str): Path to the CSV file in the repository
        new_data (pd.DataFrame): New data to append
        commit_message (str): Commit message for the update
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        github_token = get_github_token()
        if not github_token or github_token == "your_github_token_here":
            st.error("❌ GitHub token not configured. Please update GITHUB_TOKEN in github_integration.py")
            return False
        
        st.info(f"🔄 Updating {file_path} with {len(new_data)} rows...")
        
        # Initialize GitHub client
        g = Github(github_token)
        repo = g.get_repo(REPO_NAME)

        # Try to get existing content
        try:
            contents = repo.get_contents(file_path)
            # Read existing CSV data
            existing_csv = contents.decoded_content.decode('utf-8')
            existing_data = pd.read_csv(io.StringIO(existing_csv))
            
            # Remove any existing data for the same date (to handle updates)
            if 'date' in new_data.columns and 'date' in existing_data.columns:
                dates_to_update = new_data['date'].unique()
                existing_data = existing_data[~existing_data['date'].isin(dates_to_update)]
            
            # Append new data
            updated_data = pd.concat([existing_data, new_data], ignore_index=True)
            
        except Exception as e:
            # If file doesn't exist or can't be read, create new DataFrame
            st.warning(f"Could not read existing file, creating new one: {e}")
            updated_data = new_data

        # Convert DataFrame to CSV string
        csv_buffer = updated_data.to_csv(index=False)

        # Update or create file on GitHub
        if 'contents' in locals():
            repo.update_file(
                file_path,
                commit_message,
                csv_buffer,
                contents.sha
            )
            st.success(f"✅ Successfully updated {file_path}")
        else:
            repo.create_file(
                file_path,
                commit_message,
                csv_buffer
            )
            st.success(f"✅ Successfully created {file_path}")
        
        return True

    except Exception as e:
        st.error(f"❌ Error updating GitHub: {str(e)}")
        return False

def save_results_to_github(date, results):
    """
    Save daily results to both GitHub CSV files.
    
    Args:
        date (str): Date in YYYY-MM-DD format
        results (dict): Results from scoring_engine.calculate_daily_results
    
    Returns:
        bool: True if both files updated successfully
    """
    from config import GAMES, PLAYERS
    
    try:
        # Prepare scores data
        scores_rows = []
        for game in GAMES.keys():
            if game in results["raw_scores"]:
                for i, player in enumerate(PLAYERS):
                    raw_score = results["raw_scores"][game][i]
                    norm_unweighted = results["normalized_unweighted"][game][i]
                    norm_weighted = results["normalized_weighted"][game][i]
                    
                    if raw_score is not None:  # Only include participating players
                        scores_rows.append({
                            "date": date,
                            "game": game,
                            "player": player,
                            "raw_score": raw_score,
                            "normalized_unweighted_score": norm_unweighted,
                            "normalized_weighted_score": norm_weighted
                        })
        
        scores_df = pd.DataFrame(scores_rows)
        
        # Prepare winners data
        participating_players = []
        for i, player in enumerate(PLAYERS):
            participated = any(
                results["raw_scores"][game][i] is not None 
                for game in results["raw_scores"]
            )
            if participated:
                participating_players.append(player)
        
        if results.get("is_tie", False):
            # Handle ties - create entry for each winner
            winners_rows = []
            for winner in results["winners"]:
                winner_index = PLAYERS.index(winner)
                winners_rows.append({
                    "date": date,
                    "winner": winner,
                    "total_score": results["total_scores"][winner_index],
                    "participants": ",".join(participating_players)
                })
        else:
            # Single winner
            winner = results["winner"]
            winner_index = PLAYERS.index(winner)
            winners_rows = [{
                "date": date,
                "winner": winner,
                "total_score": results["total_scores"][winner_index],
                "participants": ",".join(participating_players)
            }]
        
        winners_df = pd.DataFrame(winners_rows)
        
        # Update both files
        commit_message = f"Update Globros scores for {date}"
        
        success1 = update_github_csv(SCORES_FILE_PATH, scores_df, commit_message)
        success2 = update_github_csv(WINNERS_FILE_PATH, winners_df, commit_message)
        
        return success1 and success2
        
    except Exception as e:
        st.error(f"❌ Error preparing data for GitHub: {str(e)}")
        return False

def setup_github_token_instructions():
    """Display instructions for setting up GitHub token."""
    with st.expander("🔧 GitHub Setup Instructions"):
        st.markdown("""
        To save data directly to your GitHub repository, you need a Personal Access Token:
        
        1. **Go to GitHub Settings**: Visit https://github.com/settings/tokens
        2. **Generate New Token**: Click "Generate new token (classic)"
        3. **Set Permissions**: Select these scopes:
           - `repo` (Full control of private repositories)
           - `public_repo` (Access public repositories)
        4. **Copy Token**: Copy the generated token
        5. **Add to Streamlit**: 
           - **Option A**: Enter it in the field above
           - **Option B**: Add to Streamlit secrets as `GITHUB_TOKEN`
        
        ⚠️ **Security Note**: Never share your token publicly!
        """)
