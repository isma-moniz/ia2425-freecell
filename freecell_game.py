import random
import copy
from colorama import Fore, Style
from freecell_bot import BoardState, FreecellBot
from constants import *

# Cards
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = CARD_VALUES[rank]
        self.color = Fore.RED if suit in ['Hearts', 'Diamonds'] else Fore.BLACK

    def __repr__(self):
        return f'{self.color}{self.rank} of {self.suit}{Style.RESET_ALL}'

# Freecell logic
class FreeCell:
    def __init__(self):
        self.deck = [Card(rank, suit) for suit in TYPES for rank in RANKS]
        self.deck_size = len(self.deck)
        random.shuffle(self.deck)
        self.tableau = [[] for _ in range(TABLEAU_COUNT)]
        self.free_cells = [None] * 4
        self.foundations = {suit: [] for suit in TYPES}
        self.history = []
        self.deal_cards()
        self.board_state = BoardState(self.tableau, self.free_cells, self.foundations)

    def get_board(self):
        return self.board_state

    def deal_cards(self):

        for i in range(self.deck_size):
            pos = i % TABLEAU_COUNT
            self.tableau[pos].append(self.deck.pop())

    def display_card(self, card, last):

        text = str(card)

        if len(text) < CARD_STRING_SIZE:
            pos = (CARD_STRING_SIZE - len(text)) // 2

            text = " " * pos + text

            while len(text) < CARD_STRING_SIZE:
                text += " "


        return text + "|" if not last else text


    def display(self):
        print("\n=== FreeCell Game State ===\n")

        print("Tableau:")
        for i, pile in enumerate(self.tableau):
            pile_str = ' '.join(self.display_card(card, o == len(pile) - 1) for o,card in enumerate(pile)) if pile else "Empty"
            print(f"  {i + 1}: {pile_str}")

        print("\nFree Cells:")
        free_cells_str = ' | '.join(f"{i + 1}: {cell if cell else 'Empty'}" for i, cell in enumerate(self.free_cells))
        print(f"  {free_cells_str}")

        print("\nFoundations:")
        for suit, foundation in self.foundations.items():
            foundation_str = foundation if foundation else "Empty"
            print(f"  {suit}: {foundation_str}")

        print("\n==========================\n")

    def move_to_freecell(self, tableau_idx):
        if self.tableau[tableau_idx]:
            self.save_state()
            card = self.tableau[tableau_idx].pop()
            for i in range(4):
                if not self.free_cells[i]:
                    self.free_cells[i] = card
                    print(f"Moved {card} to free cell {i + 1}")
                    return True
        print("Invalid move!")
        return False

    def move_to_tableau(self, freecell_idx, tableau_idx):
        card = self.free_cells[freecell_idx]
        if card and self.is_valid_tableau_move(tableau_idx, card):
            self.save_state()
            self.tableau[tableau_idx].append(card)
            self.free_cells[freecell_idx] = None
            print(f"Moved {card} to tableau {tableau_idx + 1}")
            return True
        print("Invalid move!")
        return False

    def move_tableau_to_tableau(self, from_idx, to_idx):
        if self.tableau[from_idx]:
            card = self.tableau[from_idx][-1]
            if self.is_valid_tableau_move(to_idx, card):
                self.save_state()
                self.tableau[to_idx].append(self.tableau[from_idx].pop())
                print(f"Moved {card} from tableau {from_idx + 1} to {to_idx + 1}")
                return True
        print("Invalid move!")
        return False

    def is_valid_tableau_move(self, tableau_idx, card):
        if not self.tableau[tableau_idx]:
            return True
        top_card = self.tableau[tableau_idx][-1]
        return (card.value == top_card.value - 1) and (card.color != top_card.color)

    def move_to_foundation(self, tableau_idx):
        if self.tableau[tableau_idx]:
            card = self.tableau[tableau_idx][-1]
            if self.is_valid_foundation_move(card):
                self.save_state()
                self.foundations[card.suit].append(card)
                self.tableau[tableau_idx].pop()
                print(f"Moved {card} to foundation {card.suit}")
                return True
        print("Invalid move!")
        return False

    def move_freecell_to_foundation(self, freecell_idx):
        card = self.free_cells[freecell_idx]
        if card and self.is_valid_foundation_move(card):
            self.save_state()  # Save state before modifying
            self.foundations[card.suit].append(card)
            self.free_cells[freecell_idx] = None
            print(f"Moved {card} to foundation {card.suit}")
            return True
        print("Invalid move!")
        return False

    def is_valid_foundation_move(self, card):
        if not self.foundations[card.suit]:
            return card.rank == 'A'
        top_card = self.foundations[card.suit][-1]
        return card.value == top_card.value + 1

    def is_winner(self):
        return all(len(foundation) == 13 for foundation in self.foundations.values())

    def save_state(self):
        self.history.append(copy.deepcopy((self.tableau, self.free_cells, self.foundations)))

    def undo(self):
        if self.history:
            self.tableau, self.free_cells, self.foundations = self.history.pop()
            print("Undo successful!")
        else:
            print("No moves to undo!")

    def get_empty_cells_and_cascades(self):
        empty_cells = self.free_cells.count(None)
        empty_cascades = sum(1 for pile in self.tableau if not pile)
        return empty_cells, empty_cascades

    def move_supermove(self, source_tableau_idx, target_tableau_idx, no_cards):
        cards_to_move = self.tableau[source_tableau_idx][-no_cards:]

        empty_cells, empty_cascades = self.get_empty_cells_and_cascades()
        max_moveable = (empty_cells + 1) * (2 ** empty_cascades)

        if len(cards_to_move) > max_moveable:
            print(f"Cannot move {len(cards_to_move)} cards. More empty cells or cascades needed.")
            return False

        if not self.is_valid_sequence(cards_to_move):
            print("The selected cards do not form a valid sequence!")
            return False

        if self.tableau[target_tableau_idx]:
            top_card = self.tableau[target_tableau_idx][-1]
            leftmost_card = cards_to_move[0]
            if not (leftmost_card.value == top_card.value - 1 and leftmost_card.color != top_card.color):
                print(f"Invalid move: {leftmost_card} cannot be placed on {top_card}!")
                return False

        self.tableau[target_tableau_idx].extend(cards_to_move)

        for _ in range(no_cards):
            self.tableau[target_tableau_idx].append(self.tableau[source_tableau_idx].pop())

        print(f"Moved {len(cards_to_move)} cards from tableau {source_tableau_idx + 1} to tableau {target_tableau_idx + 1}")

        return True

    def is_valid_sequence(self, cards_to_move):
        """Check if the cards form a valid sequence in the tableau"""
        for i in range(1, len(cards_to_move)):
            prev_card = cards_to_move[i - 1]
            curr_card = cards_to_move[i]
            if not (curr_card.value == prev_card.value - 1 and
                    curr_card.color != prev_card.color):
                return False
        return True

    def play_human(self):
        while not self.is_winner():
            self.display()

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

            if parts[0] == "freecell" and len(parts) == 2:
                self.move_to_freecell(int(parts[1]) - 1)
            elif parts[0] == "tableau" and len(parts) == 3:
                self.move_to_tableau(int(parts[1]) - 1, int(parts[2]) - 1)
            elif parts[0] == "move" and len(parts) == 3:
                self.move_tableau_to_tableau(int(parts[1]) - 1, int(parts[2]) - 1)
            elif parts[0] == "foundation" and len(parts) == 2:
                self.move_to_foundation(int(parts[1]) - 1)
            elif parts[0] == "freecell-foundation" and len(parts) == 2:
                self.move_freecell_to_foundation(int(parts[1]) - 1)
            elif parts[0] == "supermove" and len(parts) == 4:
                self.move_supermove(int(parts[1]) - 1, int(parts[2]) - 1, int(parts[3]))
            elif parts[0] == 'undo':
                self.undo()
            elif parts[0] == "quit":
                break
            else:
                print("Invalid command!")
        print("Game Over!")
