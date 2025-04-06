# Get the card types and values
TYPES = ['Spades','Clubs','Hearts','Diamonds']
RANKS = ['K','Q','J','A', '2', '3', '4', '5', '6', '7', '8', '9', '10']
CARD_VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}

# Game constants
TABLEAU_COUNT = 8
CARD_STRING_SIZE = 24
FREECELL_COUNT = 4
VICTORY_SCORE = 99999999999

# Default weights (fallback)
DEFAULT_WEIGHTS = {
    # Original weights
    "FOUNDATION_MULTIPLIER": 200,
    "FREECELL_MULTIPLIER": 4,
    "ORDER_MULTIPLIER": 2,
    "TABLEAU_EMPTY_SCORE": 8,
    "CARD_EXCAVATION_MULTIPLIER": 5,
    "MOVE_COUNT_SCORE": 0.2,

    "CHAIN_MULTIPLIER": 3,
    "BLOCKED_CARD_PENALTY": 4,
    "SAME_COLOR_BLOCK_PENALTY": 2.5,
    "BALANCE_MULTIPLIER": 1,
    "POTENTIAL_MOVE_MULTIPLIER": 0.8
}

# Phase-based weight profiles
WEIGHT_PROFILES = {
    "early": {
        # Original weights
        "FOUNDATION_MULTIPLIER": 200,
        "FREECELL_MULTIPLIER": 4,
        "ORDER_MULTIPLIER": 1,
        "TABLEAU_EMPTY_SCORE": 8,
        "CARD_EXCAVATION_MULTIPLIER": 100,
        "MOVE_COUNT_SCORE": 0.2,

        "CHAIN_MULTIPLIER": 1,
        "BLOCKED_CARD_PENALTY": 4,
        "SAME_COLOR_BLOCK_PENALTY": 2.5,
        "BALANCE_MULTIPLIER": 0,
        "POTENTIAL_MOVE_MULTIPLIER": 0.8
    },
    "mid": {
        # Original weights
        "FOUNDATION_MULTIPLIER": 400,
        "FREECELL_MULTIPLIER": 1,
        "ORDER_MULTIPLIER": 1,
        "TABLEAU_EMPTY_SCORE": 2,
        "CARD_EXCAVATION_MULTIPLIER": 150,
        "MOVE_COUNT_SCORE": 0.2,

        "CHAIN_MULTIPLIER": 1,
        "BLOCKED_CARD_PENALTY": 4,
        "SAME_COLOR_BLOCK_PENALTY": 1,
        "BALANCE_MULTIPLIER": 1,
        "POTENTIAL_MOVE_MULTIPLIER": 3
    },
    "late": {
        # Original weights
        "FOUNDATION_MULTIPLIER": 600,
        "FREECELL_MULTIPLIER": 0,
        "ORDER_MULTIPLIER": 2,
        "TABLEAU_EMPTY_SCORE": 0,
        "CARD_EXCAVATION_MULTIPLIER": 200,
        "MOVE_COUNT_SCORE": 0.2,

        "CHAIN_MULTIPLIER": 0,
        "BLOCKED_CARD_PENALTY": 4,
        "SAME_COLOR_BLOCK_PENALTY": 0.5,
        "BALANCE_MULTIPLIER": 0,
        "POTENTIAL_MOVE_MULTIPLIER": 6
    }
}


STAGNATION_THRESHOLD_EARLY = 10
STAGNATION_THRESHOLD_MID = 50
STAGNATION_THRESHOLD_LATE = 100