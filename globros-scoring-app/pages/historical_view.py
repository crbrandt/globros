import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from data_manager import load_historical_data, get_player_statistics
from daily_winners import load_daily_winners
from config import PLAYERS, GAMES

def show():
    st.title("📚 Historical Records")
    
    try:
        # Load data with error handling and debugging
        import os
        
        # Get the directory of the current script
        # script_dir = "https://raw.githubusercontent.com/crbrandt/globros/main/globros-scoring-app/"
        # scores_url = script_dir + "scores_history.csv"
        # winners_url = script_dir + "daily_winners.csv"
        
        # Navigate to the correct data directory
        data_dir = "https://raw.githubusercontent.com/crbrandt/globros/refs/heads/main/globros-scoring-app/data/"
        scores_url = data_dir + "scores_history.csv"
        winners_url = data_dir + "scores_history.csv"
        df_data =  pd.read_csv(scores_url, index_col=0)
        df_data
        
        st.write("🔍 **Debug Info:**")
        # st.write(f"- Script directory: `{script_dir}`")
        st.write(f"- Data directory path: `{data_dir}`")
        st.write(f"- Data directory exists: `{os.path.exists(data_dir)}`")
        
        if os.path.exists(data_dir):
            st.write(f"- Files in data directory: `{os.listdir(data_dir)}`")
        
        # Use the correct paths for your CSV files
        scores_path = os.path.join(data_dir, 'scores_history.csv')
        winners_path = os.path.join(data_dir, 'daily_winners.csv')
        
        st.write(f"- scores_history.csv exists: `{os.path.exists(scores_path)}`")
        st.write(f"- daily_winners.csv exists: `{os.path.exists(winners_path)}`")
        
        # Try to read raw file contents
        try:
            with open('data/scores_history.csv', 'r') as f:
                content = f.read()
                st.write(f"- scores_history.csv raw content (first 200 chars): `{content[:200]}`")
        except Exception as e:
            st.write(f"- Error reading scores_history.csv: `{e}`")
            
        try:
            with open('data/daily_winners.csv', 'r') as f:
                content = f.read()
                st.write(f"- daily_winners.csv raw content: `{content}`")
        except Exception as e:
            st.write(f"- Error reading daily_winners.csv: `{e}`")
        
        df = load_historical_data()
        winners_df = load_daily_winners()
        stats = get_player_statistics()
        
        st.write(f"- Historical data rows loaded: `{len(df)}`")
        st.write(f"- Winners data rows loaded: `{len(winners_df)}`")
        st.write("---")
        
        if df.empty:
            st.info("📝 No historical data available yet. Submit some daily scores to see statistics!")
            return
    except Exception as e:
        st.error(f"❌ Error loading historical data: {str(e)}")
        st.info("Please check that data files exist and are accessible.")
        import traceback
        st.code(traceback.format_exc())
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
