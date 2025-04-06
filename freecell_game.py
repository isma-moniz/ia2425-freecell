import copy
from copy import deepcopy

from freecell_bot import BoardState, FreecellBot
from constants import *
import time


# Freecell logic
class FreeCell:
    def __init__(self):

        self.tableau = [[] for _ in range(TABLEAU_COUNT)]
        self.free_cells = [None] * 4
        self.foundations = {suit: [] for suit in TYPES}

        self.board_state = BoardState(self.tableau, self.free_cells, self.foundations, initialize_deck=True)
        self.board_state.deal_cards()
        self.history = []

    def get_board(self):
        return self.board_state


    def move_to_freecell(self, tableau_idx):

        temp = self.clone_boardState()

        if temp.move_to_freecell(tableau_idx):
            return temp
        else:
            return None

    def move_to_tableau(self, freecell_idx, tableau_idx):

        temp = self.clone_boardState()

        if temp.move_to_tableau(freecell_idx, tableau_idx):
            return temp
        else:
            return None

    def move_tableau_to_tableau(self, from_idx, to_idx):

        temp = self.clone_boardState()

        if temp.move_tableau_to_tableau(from_idx, to_idx):
            return temp
        else:
            return None

    def is_valid_tableau_move(self, tableau_idx, card):

        return self.board_state.is_valid_tableau_move(tableau_idx, card)

    def move_to_foundation(self, tableau_idx):

        temp = self.clone_boardState()

        if temp.move_to_foundation(tableau_idx):
            return temp
        else:
            return None

    def move_freecell_to_foundation(self, freecell_idx):


        temp = self.clone_boardState()

        if temp.move_freecell_to_foundation(freecell_idx):
            return temp
        else:
            return None

    def is_valid_foundation_move(self, card):

        temp = self.clone_boardState()

        if temp.move_freecell_to_foundation(card):
            return temp
        else:
            return None

    def is_winner(self):
        return self.board_state.is_winner()

    def save_state(self):
        self.history.append((deepcopy(self.tableau), deepcopy(self.free_cells), deepcopy(self.foundations)))

    def undo(self):
        if self.history:
            self.tableau, self.free_cells, self.foundations = self.history.pop()
            print("Undo successful!")
        else:
            print("No moves to undo!")


    def get_empty_cells_and_cascades(self):
        return self.board_state.get_empty_cells_and_cascades()

    def move_supermove(self, source_tableau_idx, target_tableau_idx, no_cards):

        temp = self.clone_boardState()

        if temp.move_supermove(source_tableau_idx, target_tableau_idx, no_cards):
            return temp
        else:
            return None

    def clone_boardState(self):
        return self.board_state.clone()

