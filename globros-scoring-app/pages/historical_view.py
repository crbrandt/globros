import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from data_manager import load_historical_data, get_player_statistics
from daily_winners import load_daily_winners
from config import PLAYERS, GAMES

def calculate_stats_from_dataframes(df_scores, df_winners):
    """
    Calculate comprehensive player statistics from GitHub dataframes.
    
    Args:
        df_scores (pd.DataFrame): Historical scores data
        df_winners (pd.DataFrame): Daily winners data
    
    Returns:
        dict: Dictionary with various statistics
    """
    try:
        if df_scores.empty:
            return {}
        
        stats = {
            "total_games_played": len(df_scores["date"].unique()),
            "win_counts": df_winners["winner"].value_counts().to_dict() if not df_winners.empty else {},
            "average_scores_by_game": {},
            "player_performance_trends": {},
            "game_difficulty_analysis": {}
        }
        
        # Average scores by game and player
        for game in GAMES.keys():
            game_data = df_scores[df_scores["game"] == game]
            if not game_data.empty:
                # Filter out empty/null raw scores
                game_data_clean = game_data[game_data["raw_score"].notna() & (game_data["raw_score"] != "")]
                if not game_data_clean.empty:
                    # Convert to numeric if needed
                    game_data_clean["raw_score"] = pd.to_numeric(game_data_clean["raw_score"], errors='coerce')
                    avg_scores = game_data_clean.groupby("player")["raw_score"].mean().to_dict()
                    stats["average_scores_by_game"][game] = avg_scores
        
        # Player performance trends (total weighted scores over time)
        daily_totals = df_scores.groupby(["date", "player"])["normalized_weighted_score"].sum().reset_index()
        for player in PLAYERS:
            player_data = daily_totals[daily_totals["player"] == player].sort_values("date")
            stats["player_performance_trends"][player] = {
                "dates": player_data["date"].tolist(),
                "scores": player_data["normalized_weighted_score"].tolist()
            }
        
        # Game difficulty analysis (average raw scores)
        for game in GAMES.keys():
            game_data = df_scores[df_scores["game"] == game]
            if not game_data.empty:
                # Filter out empty/null raw scores and convert to numeric
                game_data_clean = game_data[game_data["raw_score"].notna() & (game_data["raw_score"] != "")]
                if not game_data_clean.empty:
                    game_data_clean["raw_score"] = pd.to_numeric(game_data_clean["raw_score"], errors='coerce')
                    game_data_clean = game_data_clean[game_data_clean["raw_score"].notna()]
                    
                    if not game_data_clean.empty:
                        stats["game_difficulty_analysis"][game] = {
                            "average_score": game_data_clean["raw_score"].mean(),
                            "median_score": game_data_clean["raw_score"].median(),
                            "std_dev": game_data_clean["raw_score"].std()
                        }
        
        return stats
    
    except Exception as e:
        st.error(f"Error calculating statistics: {e}")
        return {}

def show():
    st.title("📚 Historical Records")
    
    try:
        # Load data directly from GitHub
        data_dir = "https://raw.githubusercontent.com/crbrandt/globros/refs/heads/main/globros-scoring-app/data/"
        scores_url = data_dir + "scores_history.csv"
        winners_url = data_dir + "daily_winners.csv"
        
        df_scores_data = pd.read_csv(scores_url)
        df_winners_data = pd.read_csv(winners_url)
        
        # Use the GitHub dataframes
        df = df_scores_data
        winners_df = df_winners_data
        
        if df.empty:
            st.info("📝 No historical data available yet. Submit some daily scores to see statistics!")
            return
        
        # Calculate stats from the GitHub data
        stats = calculate_stats_from_dataframes(df, winners_df)
        
    except Exception as e:
        st.error(f"❌ Error loading historical data: {str(e)}")
        st.info("Please check that GitHub data files are accessible.")
        return
    
    # Summary statistics
    st.subheader("📊 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Games Played", stats.get("total_games_played", 0))
    with col2:
        if winners_df.empty:
            most_wins_player = "N/A"
            most_wins_count = 0
        else:
            win_counts = winners_df["winner"].value_counts()
            most_wins_player = win_counts.index[0] if len(win_counts) > 0 else "N/A"
            most_wins_count = win_counts.iloc[0] if len(win_counts) > 0 else 0
        st.metric("Most Wins", f"{most_wins_player} ({most_wins_count})")
    with col3:
        unique_dates = len(df["date"].unique())
        st.metric("Days Recorded", unique_dates)
    with col4:
        total_scores = len(df)
        st.metric("Total Score Entries", total_scores)
    
    st.markdown("---")
    
    # Win frequency chart
    if not winners_df.empty:
        st.subheader("🏆 Win Distribution")
        
        win_counts = winners_df["winner"].value_counts()
        
        # Create pie chart
        fig_pie = px.pie(
            values=win_counts.values,
            names=win_counts.index,
            title="Daily Wins by Player",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Win counts table
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("🥇 Win Counts")
            win_df = pd.DataFrame({
                "Player": win_counts.index,
                "Wins": win_counts.values,
                "Win Rate": [f"{(count/len(winners_df)*100):.1f}%" for count in win_counts.values]
            })
            st.dataframe(win_df, use_container_width=True)
    
    st.markdown("---")
    
    # Performance trends
    st.subheader("📈 Performance Trends")
    
    if "player_performance_trends" in stats and stats["player_performance_trends"]:
        # Create line chart for performance over time
        fig_trends = go.Figure()
        
        colors = px.colors.qualitative.Set2
        for i, player in enumerate(PLAYERS):
            if player in stats["player_performance_trends"]:
                trend_data = stats["player_performance_trends"][player]
                if trend_data["dates"]:
                    fig_trends.add_trace(go.Scatter(
                        x=trend_data["dates"],
                        y=trend_data["scores"],
                        mode='lines+markers',
                        name=player,
                        line=dict(color=colors[i % len(colors)], width=3),
                        marker=dict(size=8)
                    ))
        
        fig_trends.update_layout(
            title="Player Performance Over Time (Lower is Better)",
            xaxis_title="Date",
            yaxis_title="Total Weighted Score",
            hovermode='x unified',
            template="plotly_white"
        )
        
        st.plotly_chart(fig_trends, use_container_width=True)
    
    st.markdown("---")
    
    # Game-specific analysis
    st.subheader("🎮 Game Analysis")
    
    # Average scores by game
    if "average_scores_by_game" in stats:
        st.subheader("📊 Average Raw Scores by Game")
        
        game_avg_data = []
        for game, player_avgs in stats["average_scores_by_game"].items():
            for player, avg_score in player_avgs.items():
                game_avg_data.append({
                    "Game": game,
                    "Player": player,
                    "Average Score": avg_score
                })
        
        if game_avg_data:
            game_avg_df = pd.DataFrame(game_avg_data)
            
            # Create grouped bar chart
            fig_games = px.bar(
                game_avg_df,
                x="Game",
                y="Average Score",
                color="Player",
                barmode="group",
                title="Average Raw Scores by Game and Player",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_games.update_layout(template="plotly_white")
            st.plotly_chart(fig_games, use_container_width=True)
    
    # Game difficulty analysis
    if "game_difficulty_analysis" in stats:
        st.subheader("🎯 Game Difficulty Analysis")
        
        difficulty_data = []
        for game, analysis in stats["game_difficulty_analysis"].items():
            difficulty_data.append({
                "Game": game,
                "Average Score": analysis["average_score"],
                "Median Score": analysis["median_score"],
                "Standard Deviation": analysis["std_dev"]
            })
        
        if difficulty_data:
            difficulty_df = pd.DataFrame(difficulty_data)
            st.dataframe(difficulty_df.round(2), use_container_width=True)
    
    st.markdown("---")
    
    # Recent games table
    st.subheader("📅 Recent Games")
    
    if not winners_df.empty:
        recent_winners = winners_df.tail(10).sort_values("date", ascending=False)
        recent_winners["date"] = pd.to_datetime(recent_winners["date"]).dt.strftime("%Y-%m-%d")
        recent_winners.columns = ["Date", "Winner"]
        st.dataframe(recent_winners, use_container_width=True)
    
    st.markdown("---")
    
    # Raw data export
    st.subheader("📤 Data Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Download Historical Data"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"globros_scores_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🏆 Download Winners Data"):
            if not winners_df.empty:
                csv = winners_df.to_csv(index=False)
                st.download_button(
                    label="💾 Download Winners CSV",
                    data=csv,
                    file_name=f"globros_winners_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    # Show raw data table (optional)
    with st.expander("🔍 View Raw Data"):
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    show()
