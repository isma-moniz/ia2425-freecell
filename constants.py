# Card constants
TYPES = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
CARD_VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}

# Game constants
TABLEAU_COUNT = 8
CARD_STRING_SIZE = 24
FREECELL_COUNT = 4
VICTORY_SCORE = 9999999999

# Phase-based weight profiles
WEIGHT_PROFILES = {
    "early": {
        "FOUNDATION_MULTIPLIER": 10000,
        "CARD_EXCAVATION_MULTIPLIER": 300,
        "TABLEAU_EMPTY_SCORE": 100,
        "FREECELL_MULTIPLIER": 25,
        "ORDER_MULTIPLIER": 5,
        "MOVE_COUNT_SCORE": 2
    },
    "mid": {
        "FOUNDATION_MULTIPLIER": 12000,
        "CARD_EXCAVATION_MULTIPLIER": 200,
        "TABLEAU_EMPTY_SCORE": 60,
        "FREECELL_MULTIPLIER": 20,
        "ORDER_MULTIPLIER": 15,
        "MOVE_COUNT_SCORE": 3
    },
    "late": {
        "FOUNDATION_MULTIPLIER": 15000,
        "CARD_EXCAVATION_MULTIPLIER": 100,
        "TABLEAU_EMPTY_SCORE": 20,
        "FREECELL_MULTIPLIER": 15,
        "ORDER_MULTIPLIER": 5,
        "MOVE_COUNT_SCORE": 5
    }
}

# Default weights (fallback)
DEFAULT_WEIGHTS = {
    "FOUNDATION_MULTIPLIER": 10000,
    "CARD_EXCAVATION_MULTIPLIER": 200,
    "TABLEAU_EMPTY_SCORE": 40,
    "FREECELL_MULTIPLIER": 20,
    "ORDER_MULTIPLIER": 0,
    "MOVE_COUNT_SCORE": 2
}