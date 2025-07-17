# Game configuration and settings

# Players (sorted alphabetically)
PLAYERS = ["Anthony", "Cole", "Joseph", "Katherine"]

# Games and their weights
GAMES = {
    "Worldle": {"type": "standard", "weight": 1.2},
    "Globle": {"type": "standard", "weight": 0.8},
    "Countryle": {"type": "standard", "weight": 0.8},
    "Travle": {"type": "standard", "weight": 0.9},
    "Geogrid": {"type": "standard", "weight": 0.8},
    "NoBordle": {"type": "special", "weight": 1.1},
    "ImpossiBordle": {"type": "special", "weight": 0.9}
}

# Score ranges for validation
SCORE_RANGES = {
    "Worldle": (1, 100),
    "Globle": (1, 100),
    "Countryle": (1, 100),
    "Travle": (-1, 100),
    "NoBordle": None,  # Special handling
    "ImpossiBordle": None  # Special handling
}

# Celebration messages and GIFs
CELEBRATION_MESSAGES = [
    "🎉 Congratulations! You're the Geography Champion! 🎉",
    "🌍 World Domination Achieved! 🌍",
    "🏆 Geography Genius Alert! 🏆",
    "🎊 Master of Maps and Borders! 🎊",
    "🌟 Global Knowledge Supreme! 🌟",
    "🗺️ Atlas Master Extraordinaire! 🗺️",
    "🧭 Navigation Ninja Strikes Again! 🧭",
    "🌎 Planetary Prowess Personified! 🌎",
    "🎯 Bullseye on the Globe! 🎯",
    "🚀 Launched into Geographic Glory! 🚀"
]

CELEBRATION_GIFS = [
    "https://media.giphy.com/media/26u4cqiYI30juCOGY/giphy.gif",  # Earth spinning
    "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif",  # Celebration
    "https://media.giphy.com/media/26BRv0ThflsHCqDrG/giphy.gif",  # Trophy
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",  # Confetti
    "https://media.giphy.com/media/3o6Zt6KHxJTbXCnSvu/giphy.gif",  # Globe
    "https://media.giphy.com/media/xT9IgG50Fb7Mi0prBC/giphy.gif",  # Victory dance
    "https://media.giphy.com/media/26BRBKqUiq586bRVm/giphy.gif",  # Fireworks
    "https://media.giphy.com/media/3o7abA4a0QCXtSxGN2/giphy.gif",  # Applause
    "https://media.giphy.com/media/l0MYEqEzwMWFCg8rm/giphy.gif",  # Success
    "https://media.giphy.com/media/26BRwW3ckGjcZmsxO/giphy.gif"   # Champion
]

# Bad score humor messages
BAD_SCORE_MESSAGES = [
    "Yikes! 😬 Did you use a blindfold?",
    "Oof! 🤦‍♂️ Geography isn't for everyone...",
    "Wowza! 😅 That's... impressively off-target!",
    "Ouch! 🙈 Time to buy an atlas?",
    "Sheesh! 🤯 Even a dart-throwing monkey might do better!",
    "Crikey! 😵 Did you confuse Earth with Mars?",
    "Blimey! 🤪 That's a special kind of lost!",
    "Golly! 🤷‍♀️ GPS would be crying right now!",
    "Zoinks! 😱 That score needs its own zip code!",
    "Jiminy! 🤭 Even Google Maps is confused!",
    "Holy moly! 🫨 That's geographically... creative!",
    "Good grief! 😬 Did you spin the globe with your eyes closed?",
    "Sweet mercy! 🤦‍♀️ That's not even in the right hemisphere!",
    "Great Scott! 😵‍💫 Time travel couldn't fix that score!",
    "Heavens! 🙄 That's astronomically off!"
]

BAD_SCORE_GIFS = [
    "https://media.giphy.com/media/3o7aCRloybJlXpNjSU/giphy.gif",  # Facepalm
    "https://media.giphy.com/media/32mC2kXYWCsg0/giphy.gif",      # Confused
    "https://media.giphy.com/media/l3q2K5jinAlChoCLS/giphy.gif",   # Shaking head
    "https://media.giphy.com/media/26tn33aiTi1jkl6H6/giphy.gif",  # Disappointed
    "https://media.giphy.com/media/3o7abwbzKeaRksvVaE/giphy.gif", # Cringe
    "https://media.giphy.com/media/l0HlvtIPzPdt2usKs/giphy.gif",  # Awkward
    "https://media.giphy.com/media/26ufcVAp3AiJJsrIs/giphy.gif",  # Yikes
    "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif", # Oh no
]

# CSV file path
CSV_FILE_PATH = "data/scores_history.csv"

# CSV columns
CSV_COLUMNS = ["date", "game", "player", "raw_score", "normalized_unweighted_score", "normalized_weighted_score"]
