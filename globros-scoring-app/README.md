# 🌍 Globros Geography Game Scorer

A Streamlit web application for tracking and analyzing daily geography game scores among friends.

## Features

- **Daily Score Submission**: Enter scores for all players across multiple geography games
- **Automated Scoring**: Uses median-based normalization with game-specific weights
- **Historical Records**: View past results, win statistics, and performance trends
- **Player Statistics**: Detailed individual and head-to-head analysis
- **Data Export**: Download historical data as CSV files
- **Celebration System**: Random victory animations and messages

## Supported Games

- **Worldle** (Weight: 1.2)
- **Globle** (Weight: 0.8)
- **Countryle** (Weight: 0.8)
- **Travle** (Weight: 0.9)
- **NoBordle** (Weight: 1.1) - Custom scoring for correct/incorrect answers
- **ImpossiBordle** (Weight: 0.9) - Custom scoring for correct/incorrect answers

## Scoring Algorithm

The app uses a sophisticated scoring system:

1. **Raw Scores**: Direct game scores entered by users
2. **Normalization**: `(Score - Median Score) / (Median Score^0.4)`
3. **Weighting**: Normalized scores multiplied by game-specific weights
4. **Ranking**: Players ranked by total weighted score (lower is better)

### Special Game Scoring (NoBordle/ImpossiBordle)
- **Correct ≤ 6 guesses**: Score = number of guesses
- **Incorrect**: Score = `8 * (1 + sqrt(Distance/12500))`

## Local Development

### Prerequisites
- Python 3.8+
- pip

### Setup
1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run streamlit_app.py
   ```

## Streamlit Cloud Deployment

### Step 1: GitHub Setup
1. Create a new repository on GitHub
2. Upload all files from this project to your repository
3. Ensure the main file is named `streamlit_app.py` (required by Streamlit Cloud)

### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository and branch (usually `main`)
5. Set main file path to `streamlit_app.py`
6. Click "Deploy"

### Step 3: Access Your App
Your app will be available at:
```
https://share.streamlit.io/[your-username]/[your-repo-name]/main/streamlit_app.py
```

## Configuration

### Adding/Removing Players
Edit the `PLAYERS` list in `config.py`:
```python
PLAYERS = ["Anthony", "Joseph", "Katherine", "Cole", "NewPlayer"]
```

### Modifying Game Weights
Edit the `GAMES` dictionary in `config.py`:
```python
GAMES = {
    "Worldle": {"weight": 1.2, "type": "standard"},
    # ... other games
}
```

### Adding New Games
1. Add the game to `GAMES` in `config.py`
2. Add score validation in `SCORE_RANGES`
3. Update the UI in `pages/daily_submission.py` if needed

## File Structure

```
globros-scoring-app/
├── streamlit_app.py          # Main application entry point
├── config.py                 # Configuration and settings
├── scoring_engine.py         # Scoring calculations
├── data_manager.py          # CSV data operations
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── pages/                  # Application pages
│   ├── __init__.py
│   ├── daily_submission.py # Score input and calculation
│   ├── historical_view.py  # Historical data and charts
│   └── player_stats.py     # Player analysis
└── data/                   # Data storage (created automatically)
    └── scores_history.csv  # Historical scores
```

## Data Storage

The application uses a CSV file (`data/scores_history.csv`) with the following structure:

| Column | Description |
|--------|-------------|
| date | Date of the game (YYYY-MM-DD) |
| game | Game name |
| player | Player name |
| raw_score | Original score entered |
| normalized_unweighted_score | Normalized score before weighting |
| normalized_weighted_score | Final weighted score |

## Usage Tips

1. **Daily Submission**: Enter all players' scores for a single date
2. **Score Validation**: The app validates score ranges for each game
3. **Data Persistence**: Scores are saved only when you click "Submit to Official Records"
4. **Historical Analysis**: Use the Historical Records page for trends and statistics
5. **Player Comparison**: Use Player Statistics for detailed individual analysis

## Troubleshooting

### Common Issues
- **Import Errors**: Ensure all files are in the correct directory structure
- **Data Not Saving**: Check that the `data/` directory is writable
- **Charts Not Loading**: Verify plotly is installed correctly

### Support
For issues or feature requests, check the application logs in Streamlit Cloud or run locally to debug.

## License

This project is open source and available under the MIT License.
