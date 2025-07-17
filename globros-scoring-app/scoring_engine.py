import pandas as pd
import numpy as np
import math
from config import GAMES, PLAYERS

def calculate_special_score(correct, guesses_or_distance, game_type):
    """
    Calculate score for NoBordle and ImpossiBordle games.
    
    Args:
        correct (bool): Whether the answer was correct
        guesses_or_distance: Number of guesses if correct, distance in miles if incorrect
        game_type (str): "NoBordle" or "ImpossiBordle"
    
    Returns:
        float: Raw score for the game
    """
    if correct and guesses_or_distance <= 6:
        return guesses_or_distance
    else:
        # S = 8*(1+sqrt(Distance/12500))
        distance = guesses_or_distance if not correct else 0
        return 8 * (1 + math.sqrt(distance / 12500))

def calculate_normalized_score(raw_scores, game):
    """
    Calculate normalized unweighted scores using the formula:
    (Score - Median Score) / (Median Score^0.4)
    
    For Geogrid, scores are divided by 100 before normalization.
    
    Args:
        raw_scores (list): List of raw scores for all players (may contain None for non-participants)
        game (str): Game name
    
    Returns:
        list: Normalized unweighted scores (None for non-participants)
    """
    # Filter out None values for median calculation
    participating_scores = [score for score in raw_scores if score is not None]
    
    if not participating_scores:
        # If no one participated, return all zeros
        return [0.0 if score is not None else None for score in raw_scores]
    
    # Apply Geogrid normalization (divide by 100) before median calculation
    if game == "Geogrid":
        participating_scores = [score / 100.0 for score in participating_scores]
    
    scores_array = np.array(participating_scores, dtype=float)
    median_score = np.median(scores_array)
    
    normalized_scores = []
    for score in raw_scores:
        if score is None:
            normalized_scores.append(None)  # Non-participant
        else:
            try:
                # Apply Geogrid normalization to individual scores as well
                actual_score = score / 100.0 if game == "Geogrid" else float(score)
                
                # Handle division by zero case when median is exactly 0
                if median_score == 0:
                    # When median is 0, scores above 0 are positive, scores below 0 are negative
                    normalized = actual_score  # Simple difference since median is 0
                else:
                    # Use absolute value for the denominator to handle negative medians properly
                    normalized = (actual_score - median_score) / (abs(median_score) ** 0.4)
                normalized_scores.append(normalized)
            except (ValueError, TypeError):
                normalized_scores.append(0.0)
    
    return normalized_scores

def calculate_weighted_scores(normalized_scores, game):
    """
    Apply game weights to normalized scores.
    
    Args:
        normalized_scores (list): List of normalized unweighted scores (may contain None)
        game (str): Game name
    
    Returns:
        list: Weighted scores (None for non-participants)
    """
    weight = GAMES[game]["weight"]
    return [score * weight if score is not None else None for score in normalized_scores]

def calculate_daily_results(scores_data):
    """
    Calculate complete daily results including rankings.
    
    Args:
        scores_data (dict): Dictionary with game names as keys and lists of scores as values
                           Format: {"Worldle": [score1, score2, ...], "Globle": [...], ...}
    
    Returns:
        dict: Complete results with individual scores, totals, and rankings
    """
    results = {
        "players": PLAYERS.copy(),
        "raw_scores": {},
        "normalized_unweighted": {},
        "normalized_weighted": {},
        "total_scores": [0] * len(PLAYERS),
        "rankings": []
    }
    
    # Process each game
    for game, raw_scores in scores_data.items():
        if game not in GAMES:
            continue
            
        # Store raw scores
        results["raw_scores"][game] = raw_scores
        
        # Calculate normalized unweighted scores
        normalized_unweighted = calculate_normalized_score(raw_scores, game)
        results["normalized_unweighted"][game] = normalized_unweighted
        
        # Calculate weighted scores
        weighted_scores = calculate_weighted_scores(normalized_unweighted, game)
        results["normalized_weighted"][game] = weighted_scores
        
        # Add to total scores (only for participating players)
        for i, weighted_score in enumerate(weighted_scores):
            if weighted_score is not None:
                results["total_scores"][i] += weighted_score
    
    # Filter out non-participating players for rankings
    participating_player_totals = []
    for i, player in enumerate(PLAYERS):
        # Check if player participated in any game
        participated = any(
            results["raw_scores"][game][i] is not None 
            for game in results["raw_scores"]
        )
        if participated:
            participating_player_totals.append((player, results["total_scores"][i]))
    
    # Calculate rankings (lower total score is better) - only participating players
    participating_player_totals.sort(key=lambda x: x[1])
    results["rankings"] = participating_player_totals
    
    # Handle ties - find all players with the lowest score among participants
    if participating_player_totals:
        lowest_score = participating_player_totals[0][1]
        winners = [player for player, score in participating_player_totals if score == lowest_score]
    else:
        winners = []
    
    if len(winners) == 1:
        results["winner"] = winners[0]
        results["winners"] = winners
        results["is_tie"] = False
    else:
        results["winner"] = winners[0]  # Keep for backward compatibility
        results["winners"] = winners
        results["is_tie"] = True
    
    return results

def format_results_for_display(results):
    """
    Format results for nice display in Streamlit.
    
    Args:
        results (dict): Results from calculate_daily_results
    
    Returns:
        str: Formatted results string
    """
    output = []
    output.append("## 🌍 Daily Geography Game Results 🌍\n")
    
    # Individual game scores
    for game in GAMES.keys():
        if game in results["raw_scores"]:
            output.append(f"### {game}")
            for i, player in enumerate(results["players"]):
                raw = results["raw_scores"][game][i]
                normalized = results["normalized_unweighted"][game][i]
                weighted = results["normalized_weighted"][game][i]
                output.append(f"- **{player}**: {raw} (normalized: {normalized:.3f}, weighted: {weighted:.3f})")
            output.append("")
    
    # Total scores and rankings
    output.append("### 🏆 Final Rankings")
    for rank, (player, total_score) in enumerate(results["rankings"], 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
        output.append(f"{rank}. {medal} **{player}**: {total_score:.3f}")
    
    return "\n".join(output)

def validate_score_input(game, score, correct=None):
    """
    Validate score input for a given game.
    
    Args:
        game (str): Game name
        score: Score value to validate
        correct (bool): For special games, whether answer was correct
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if game not in GAMES:
        return False, f"Unknown game: {game}"
    
    if GAMES[game]["type"] == "special":
        # Special validation for NoBordle/ImpossiBordle handled in UI
        return True, ""
    
    # Standard game validation
    if game in ["Worldle", "Globle", "Countryle"]:
        if not isinstance(score, (int, float)) or score < 1 or score > 100:
            return False, f"{game} score must be between 1 and 100"
    elif game == "Travle":
        if not isinstance(score, (int, float)) or score < -1 or score > 100:
            return False, f"{game} score must be between -1 and 100"
    elif game == "Geogrid":
        if not isinstance(score, int) or score < 0 or score > 900:
            return False, f"{game} score must be an integer between 0 and 900"
    
    return True, ""
