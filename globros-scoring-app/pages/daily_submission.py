import streamlit as st
import pandas as pd
from datetime import datetime, date
import random
from config import GAMES, PLAYERS, CELEBRATION_MESSAGES, CELEBRATION_GIFS, BAD_SCORE_MESSAGES, BAD_SCORE_GIFS
from scoring_engine import calculate_daily_results, calculate_special_score, format_results_for_display
from data_manager import save_daily_results, check_date_exists

def show():
    st.title("📅 Daily Score Submission")
    
    # Date selection
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_date = st.date_input(
            "Select Date:",
            value=date.today(),
            help="Choose the date for these scores"
        )
    
    with col2:
        if check_date_exists(selected_date.strftime("%Y-%m-%d")):
            st.warning(f"⚠️ Data already exists for {selected_date}. Submitting will overwrite existing data.")
    
    st.markdown("---")
    
    # Player participation selection
    st.subheader("👥 Player Participation")
    st.write("Select which players participated today:")
    
    # Initialize session state for participation
    if 'player_participation' not in st.session_state:
        st.session_state.player_participation = {player: True for player in PLAYERS}
    
    participation_cols = st.columns(len(PLAYERS))
    for i, player in enumerate(PLAYERS):
        with participation_cols[i]:
            st.session_state.player_participation[player] = st.checkbox(
                f"✅ {player}",
                value=st.session_state.player_participation[player],
                key=f"participation_{player}"
            )
    
    # Get list of participating players
    participating_players = [player for player in PLAYERS if st.session_state.player_participation[player]]
    
    if not participating_players:
        st.error("❌ At least one player must participate!")
        return
    
    st.markdown("---")
    
    # Score input section
    st.subheader("🎮 Enter Scores for Participating Players")
    
    # Initialize session state for scores
    if 'scores_data' not in st.session_state:
        st.session_state.scores_data = {}
        for game in GAMES.keys():
            st.session_state.scores_data[game] = {}
            for player in PLAYERS:
                st.session_state.scores_data[game][player] = None
    
    # Create input fields for each game - only for participating players
    for game in GAMES.keys():
        st.markdown(f"### 🌍 {game}")
        
        if GAMES[game]["type"] == "standard":
            # Standard games - simple number input
            cols = st.columns(len(participating_players))
            for i, player in enumerate(participating_players):
                with cols[i]:
                    if game == "Travle":
                        score = st.number_input(
                            f"{player}",
                            min_value=-1,
                            max_value=100,
                            value=-1,
                            key=f"{game}_{player}",
                            help="Enter score (-1 to 100)"
                        )
                    else:
                        score = st.number_input(
                            f"{player}",
                            min_value=1,
                            max_value=100,
                            value=1,
                            key=f"{game}_{player}",
                            help="Enter score (1 to 100)"
                        )
                    st.session_state.scores_data[game][player] = score
            
            # Set non-participating players to None
            for player in PLAYERS:
                if player not in participating_players:
                    st.session_state.scores_data[game][player] = None
        
        else:
            # Special games (NoBordle, ImpossiBordle)
            cols = st.columns(len(participating_players))
            for i, player in enumerate(participating_players):
                with cols[i]:
                    st.markdown(f"**{player}**")
                    
                    # Correct/Incorrect selection
                    correct = st.radio(
                        "Result:",
                        ["Correct", "Incorrect"],
                        key=f"{game}_{player}_result",
                        horizontal=True
                    )
                    
                    if correct == "Correct":
                        guesses = st.number_input(
                            "Number of guesses:",
                            min_value=1,
                            max_value=20,
                            value=1,
                            key=f"{game}_{player}_guesses"
                        )
                        raw_score = calculate_special_score(True, guesses, game)
                    else:
                        distance = st.number_input(
                            "Distance (miles):",
                            min_value=0.0,
                            value=0.0,
                            key=f"{game}_{player}_distance"
                        )
                        raw_score = calculate_special_score(False, distance, game)
                    
                    st.session_state.scores_data[game][player] = raw_score
                    st.caption(f"Calculated score: {raw_score:.2f}")
            
            # Set non-participating players to None
            for player in PLAYERS:
                if player not in participating_players:
                    st.session_state.scores_data[game][player] = None
    
    st.markdown("---")
    
    # Calculate results button
    if st.button("🧮 Calculate Results", type="primary"):
        # Prepare data for calculation - no validation needed since all fields have default values
        scores_for_calculation = {}
        for game in GAMES.keys():
            scores_for_calculation[game] = [
                st.session_state.scores_data[game][player] for player in PLAYERS
            ]
        
        # Calculate results
        results = calculate_daily_results(scores_for_calculation)
        st.session_state.current_results = results
        st.session_state.current_date = selected_date.strftime("%Y-%m-%d")
        
        # Display results
        display_results(results)

def display_results(results):
    """Display calculated results with celebration."""
    
    # Winner announcement with celebration - handle ties
    celebration_msg = random.choice(CELEBRATION_MESSAGES)
    celebration_gif = random.choice(CELEBRATION_GIFS)
    
    if results.get("is_tie", False):
        winners = results["winners"]
        if len(winners) == len(PLAYERS):
            winner_text = "EVERYONE WINS!"
            celebration_msg = "🤝 Perfect Tie! Everyone's a Geography Champion! 🤝"
        elif len(winners) == 2:
            winner_text = f"{winners[0]} & {winners[1]} TIE!"
        elif len(winners) == 3:
            winner_text = f"{winners[0]}, {winners[1]} & {winners[2]} TIE!"
        else:
            winner_text = f"{', '.join(winners[:-1])} & {winners[-1]} TIE!"
    else:
        winner = results["winner"]
        winner_text = f"{winner} WINS!"
    
    st.markdown(f"""
    <div class="winner-announcement">
        <h2>{celebration_msg}</h2>
        <h1>🏆 {winner_text} 🏆</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Display celebration GIF
    st.image(celebration_gif, width=300)
    
    
    st.markdown("---")
    
    # Detailed results
    st.subheader("📊 Detailed Results")
    
    # Create results table with humor for bad scores - only participating players
    results_data = []
    for i, player in enumerate(PLAYERS):
        # Check if player participated in any game
        participated = any(
            results["raw_scores"][game][i] is not None 
            for game in results["raw_scores"]
        )
        
        if participated:
            row = {"Player": player, "Total Score": f"{results['total_scores'][i]:.3f}"}
            for game in GAMES.keys():
                if game in results["raw_scores"]:
                    raw = results["raw_scores"][game][i]
                    weighted = results["normalized_weighted"][game][i]
                    
                    if raw is not None:
                        # Check for bad scores and add humor
                        raw_display = str(raw)
                        if game in ["Worldle", "Globle", "Countryle"] and raw >= 10:
                            raw_display = f"{raw} 😬"
                        elif game == "Travle" and raw >= 3:
                            raw_display = f"{raw} 😬"
                        
                        row[f"{game} (Raw)"] = raw_display
                        row[f"{game} (Weighted)"] = f"{weighted:.3f}"
                    else:
                        row[f"{game} (Raw)"] = "N/A"
                        row[f"{game} (Weighted)"] = "N/A"
            results_data.append(row)
    
    # Sort by total score for display
    results_data.sort(key=lambda x: float(x["Total Score"]))
    
    # Add rank with proper tie handling
    current_rank = 1
    prev_score = None
    for i, row in enumerate(results_data):
        current_score = float(row["Total Score"])
        
        # If this score is different from previous, update rank
        if prev_score is not None and current_score != prev_score:
            current_rank = i + 1
        
        medal = "🥇" if current_rank == 1 else "🥈" if current_rank == 2 else "🥉" if current_rank == 3 else "🏅"
        row["Rank"] = f"{current_rank} {medal}"
        prev_score = current_score
    
    # Reorder columns
    columns = ["Rank", "Player", "Total Score"]
    for game in GAMES.keys():
        if f"{game} (Raw)" in results_data[0]:
            columns.extend([f"{game} (Raw)", f"{game} (Weighted)"])
    
    df = pd.DataFrame(results_data)[columns]
    st.dataframe(df, use_container_width=True)
    
    # Display individual humor messages for bad scores
    bad_scores_found = []
    for i, player in enumerate(PLAYERS):
        for game in GAMES.keys():
            if game in results["raw_scores"]:
                raw = results["raw_scores"][game][i]
                if game in ["Worldle", "Globle", "Countryle"] and raw >= 10:
                    humor_msg = random.choice(BAD_SCORE_MESSAGES)
                    bad_scores_found.append(f"**{player}** in {game}: {humor_msg}")
                elif game == "Travle" and raw >= 3:
                    humor_msg = random.choice(BAD_SCORE_MESSAGES)
                    bad_scores_found.append(f"**{player}** in {game}: {humor_msg}")
    
    if bad_scores_found:
        st.markdown("### 😅 Score Commentary")
        for comment in bad_scores_found:
            st.markdown(f"• {comment}")
    
    st.markdown("---")
    
    # Save to records button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Submit to Official Records", type="primary", use_container_width=True):
            if save_daily_results(st.session_state.current_date, st.session_state.current_results):
                st.success("✅ Results saved to official records!")
                st.balloons()
                
                # Clear the form
                for game in GAMES.keys():
                    for player in PLAYERS:
                        st.session_state.scores_data[game][player] = None
                
                # Clear results from session state
                if 'current_results' in st.session_state:
                    del st.session_state.current_results
                if 'current_date' in st.session_state:
                    del st.session_state.current_date
                
                st.rerun()
            else:
                st.error("❌ Error saving results. Please try again.")

# Initialize the page
if __name__ == "__main__":
    show()
