import copy
from freecell_bot import BoardState, FreecellBot
from constants import *


# Freecell logic
class FreeCell:
    def __init__(self):

        self.tableau = [[] for _ in range(TABLEAU_COUNT)]
        self.free_cells = [None] * 4
        self.foundations = {suit: [] for suit in TYPES}

        self.board_state = BoardState(self.tableau, self.free_cells, self.foundations)
        self.board_state.deal_cards()

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
        self.history.append(copy.deepcopy((self.tableau, self.free_cells, self.foundations)))

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

    def play_bot(self):

        bot = FreecellBot()

        for state in bot.get_plays(self):
            state.display()


    def play_human(self):
        while not self.is_winner():
            self.board_state.display()

            print("\n" + str(self.board_state.calculate_heuristic()) + "\n")

            print("\nMove types:")
            print(" - freecell [tableau_index]: Move top card from tableau to freecell")
            print(" - tableau [freecell_index] [tableau_index]: Move card from freecell to tableau")
            print(" - move [from_tableau] [to_tableau]: Move card from one tableau column to another")
            print(" - foundation [tableau_index]: Move top card from tableau to foundation")
            print(" - freecell-foundation [freecell_index]: Move card from freecell to foundation")
            print(" - undo: return to your last move")
            print(" - supermove [from_tableau] [to_tableau] [num_cards(negative)]: Move a sequence of cards from tableau")
            print(" - quit: Exit the game")
            move = input("Enter move: ")

            parts = move.split()

            temp = None

            if parts[0] == "freecell" and len(parts) == 2:

                temp = self.move_to_freecell(int(parts[1]) - 1)

            elif parts[0] == "tableau" and len(parts) == 3:

                temp =  self.move_to_tableau(int(parts[1]) - 1, int(parts[2]) - 1)

            elif parts[0] == "move" and len(parts) == 3:

                temp = self.move_tableau_to_tableau(int(parts[1]) - 1, int(parts[2]) - 1)

            elif parts[0] == "foundation" and len(parts) == 2:

                temp = self.move_to_foundation(int(parts[1]) - 1)

            elif parts[0] == "freecell-foundation" and len(parts) == 2:

                temp = self.move_freecell_to_foundation(int(parts[1]) - 1)

            elif parts[0] == "supermove" and len(parts) == 4:

                temp = self.move_supermove(int(parts[1]) - 1, int(parts[2]) - 1, int(parts[3]))

            elif parts[0] == 'undo':
                self.undo()
            elif parts[0] == "quit":
                break
            else:
                print("Invalid command!")

            if temp is not None:
                self.board_state = temp

        print("Game Over!")
