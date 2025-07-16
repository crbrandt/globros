import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from data_manager import load_historical_data, get_daily_winners, get_player_statistics
from config import PLAYERS, GAMES

def show():
    st.title("👥 Player Statistics")
    
    # Load data
    df = load_historical_data()
    winners_df = get_daily_winners()
    stats = get_player_statistics()
    
    if df.empty:
        st.info("📝 No player data available yet. Submit some daily scores to see player statistics!")
        return
    
    # Player selector
    st.subheader("🎯 Select Player for Detailed Analysis")
    selected_player = st.selectbox("Choose a player:", PLAYERS)
    
    if selected_player:
        show_player_details(selected_player, df, winners_df, stats)
    
    st.markdown("---")
    
    # Head-to-head comparison
    st.subheader("⚔️ Head-to-Head Comparison")
    
    col1, col2 = st.columns(2)
    with col1:
        player1 = st.selectbox("Player 1:", PLAYERS, key="p1")
    with col2:
        player2 = st.selectbox("Player 2:", [p for p in PLAYERS if p != player1], key="p2")
    
    if player1 and player2:
        show_head_to_head(player1, player2, df, winners_df, stats)

def show_player_details(player, df, winners_df, stats):
    """Show detailed statistics for a specific player."""
    
    st.subheader(f"📊 {player}'s Performance Profile")
    
    # Player summary metrics
    player_wins = len(winners_df[winners_df["winner"] == player]) if not winners_df.empty else 0
    total_games = stats.get("total_games_played", 0)
    win_rate = (player_wins / total_games * 100) if total_games > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Wins", player_wins)
    with col2:
        st.metric("Win Rate", f"{win_rate:.1f}%")
    with col3:
        st.metric("Games Played", total_games)
    with col4:
        # Calculate average rank
        if "player_performance_trends" in stats and player in stats["player_performance_trends"]:
            scores = stats["player_performance_trends"][player]["scores"]
            avg_score = np.mean(scores) if scores else 0
            st.metric("Avg Score", f"{avg_score:.2f}")
        else:
            st.metric("Avg Score", "N/A")
    
    # Player's game performance
    if "average_scores_by_game" in stats:
        st.subheader(f"🎮 {player}'s Game Performance")
        
        player_game_data = []
        for game, player_avgs in stats["average_scores_by_game"].items():
            if player in player_avgs:
                player_game_data.append({
                    "Game": game,
                    "Average Score": player_avgs[player],
                    "Weight": GAMES[game]["weight"]
                })
        
        if player_game_data:
            game_df = pd.DataFrame(player_game_data)
            
            # Create radar chart for game performance
            fig_radar = go.Figure()
            
            fig_radar.add_trace(go.Scatterpolar(
                r=game_df["Average Score"],
                theta=game_df["Game"],
                fill='toself',
                name=player,
                line_color='rgb(32, 201, 151)'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, max(game_df["Average Score"]) * 1.1]
                    )),
                showlegend=True,
                title=f"{player}'s Game Performance Radar"
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Game performance table
            st.dataframe(game_df.round(2), use_container_width=True)
    
    # Performance over time
    if "player_performance_trends" in stats and player in stats["player_performance_trends"]:
        st.subheader(f"📈 {player}'s Performance Trend")
        
        trend_data = stats["player_performance_trends"][player]
        if trend_data["dates"]:
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=trend_data["dates"],
                y=trend_data["scores"],
                mode='lines+markers',
                name=player,
                line=dict(color='rgb(32, 201, 151)', width=3),
                marker=dict(size=8)
            ))
            
            # Add trend line
            x_numeric = list(range(len(trend_data["dates"])))
            z = np.polyfit(x_numeric, trend_data["scores"], 1)
            p = np.poly1d(z)
            
            fig_trend.add_trace(go.Scatter(
                x=trend_data["dates"],
                y=p(x_numeric),
                mode='lines',
                name='Trend',
                line=dict(color='red', dash='dash')
            ))
            
            fig_trend.update_layout(
                title=f"{player}'s Score Trend Over Time",
                xaxis_title="Date",
                yaxis_title="Total Weighted Score",
                template="plotly_white"
            )
            
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Performance insights
            if len(trend_data["scores"]) > 1:
                recent_avg = np.mean(trend_data["scores"][-5:]) if len(trend_data["scores"]) >= 5 else np.mean(trend_data["scores"])
                overall_avg = np.mean(trend_data["scores"])
                
                if recent_avg < overall_avg:
                    st.success(f"📈 {player} is improving! Recent average ({recent_avg:.2f}) is better than overall average ({overall_avg:.2f})")
                elif recent_avg > overall_avg:
                    st.warning(f"📉 {player}'s recent performance ({recent_avg:.2f}) is below their overall average ({overall_avg:.2f})")
                else:
                    st.info(f"➡️ {player} is maintaining consistent performance around {overall_avg:.2f}")

def show_head_to_head(player1, player2, df, winners_df, stats):
    """Show head-to-head comparison between two players."""
    
    st.subheader(f"⚔️ {player1} vs {player2}")
    
    # Head-to-head wins
    if not winners_df.empty:
        p1_wins = len(winners_df[winners_df["winner"] == player1])
        p2_wins = len(winners_df[winners_df["winner"] == player2])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{player1} Wins", p1_wins)
        with col2:
            st.metric(f"{player2} Wins", p2_wins)
        with col3:
            if p1_wins > p2_wins:
                leader = f"{player1} leads"
            elif p2_wins > p1_wins:
                leader = f"{player2} leads"
            else:
                leader = "Tied"
            st.metric("Head-to-Head", leader)
    
    # Game-by-game comparison
    if "average_scores_by_game" in stats:
        st.subheader("🎮 Game-by-Game Comparison")
        
        comparison_data = []
        for game, player_avgs in stats["average_scores_by_game"].items():
            if player1 in player_avgs and player2 in player_avgs:
                comparison_data.append({
                    "Game": game,
                    player1: player_avgs[player1],
                    player2: player_avgs[player2],
                    "Difference": player_avgs[player1] - player_avgs[player2]
                })
        
        if comparison_data:
            comp_df = pd.DataFrame(comparison_data)
            
            # Create comparison bar chart
            fig_comp = go.Figure()
            
            fig_comp.add_trace(go.Bar(
                name=player1,
                x=comp_df["Game"],
                y=comp_df[player1],
                marker_color='rgb(55, 83, 109)'
            ))
            
            fig_comp.add_trace(go.Bar(
                name=player2,
                x=comp_df["Game"],
                y=comp_df[player2],
                marker_color='rgb(26, 118, 255)'
            ))
            
            fig_comp.update_layout(
                title=f"Average Scores: {player1} vs {player2}",
                xaxis_title="Game",
                yaxis_title="Average Score",
                barmode='group',
                template="plotly_white"
            )
            
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Comparison table
            st.dataframe(comp_df.round(2), use_container_width=True)
            
            # Who's better at each game
            st.subheader("🏆 Game Advantages")
            for _, row in comp_df.iterrows():
                game = row["Game"]
                diff = row["Difference"]
                if abs(diff) < 0.1:
                    st.write(f"**{game}**: Very close! ({abs(diff):.2f} difference)")
                elif diff < 0:
                    st.write(f"**{game}**: {player2} is better by {abs(diff):.2f} points")
                else:
                    st.write(f"**{game}**: {player1} is better by {diff:.2f} points")
    
    # Performance trends comparison
    if "player_performance_trends" in stats:
        if player1 in stats["player_performance_trends"] and player2 in stats["player_performance_trends"]:
            st.subheader("📈 Performance Trends Comparison")
            
            p1_trend = stats["player_performance_trends"][player1]
            p2_trend = stats["player_performance_trends"][player2]
            
            fig_trends = go.Figure()
            
            if p1_trend["dates"]:
                fig_trends.add_trace(go.Scatter(
                    x=p1_trend["dates"],
                    y=p1_trend["scores"],
                    mode='lines+markers',
                    name=player1,
                    line=dict(color='rgb(55, 83, 109)', width=3)
                ))
            
            if p2_trend["dates"]:
                fig_trends.add_trace(go.Scatter(
                    x=p2_trend["dates"],
                    y=p2_trend["scores"],
                    mode='lines+markers',
                    name=player2,
                    line=dict(color='rgb(26, 118, 255)', width=3)
                ))
            
            fig_trends.update_layout(
                title=f"Performance Trends: {player1} vs {player2}",
                xaxis_title="Date",
                yaxis_title="Total Weighted Score",
                template="plotly_white"
            )
            
            st.plotly_chart(fig_trends, use_container_width=True)

if __name__ == "__main__":
    show()
