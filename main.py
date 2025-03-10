import random
import copy
from colorama import Fore, Style

# Get the card types and values
TYPES = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
CARD_VALUES = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}

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
        random.shuffle(self.deck)
        self.tableau = [[] for _ in range(8)]
        self.free_cells = [None] * 4
        self.foundations = {suit: [] for suit in TYPES}
        self.history = []
        self.deal_cards()

    def deal_cards(self):
        for i in range(4):
            for j in range(7):
                if self.deck:
                    self.tableau[i].append(self.deck.pop())
        for i in range(4):
            for j in range(6):
                if self.deck:
                    self.tableau[i+4].append(self.deck.pop())

    def display(self):
        print("\nTableau:")
        for i, pile in enumerate(self.tableau):
            print(f"{i + 1}: {pile}")

        print("\nFree Cells:")
        for i, cell in enumerate(self.free_cells):
            print(f"{i + 1}: {cell if cell else 'Empty'}")

        print("\nFoundations:")
        for suit, foundation in self.foundations.items():
            print(f"{suit}: {foundation}")

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
            return card.rank == 'K'
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

    def play_human(self):
        while not self.is_winner():
            self.display()
            print("\nMove types:")
            print(" - freecell [tableau_index]: Move top card from tableau to freecell")
            print(" - tableau [freecell_index] [tableau_index]: Move card from freecell to tableau")
            print(" - move [from_tableau] [to_tableau]: Move card from one tableau column to another")
            print(" - foundation [tableau_index]: Move top card from tableau to foundation")
            print(" - freecell-foundation [freecell_index]: Move card from freecell to foundation")
            print(" - undo: return to your last move")
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
                self.move_freecell_to_foundation(int(parts[1]) -1)
            elif parts[0] == 'undo':
                self.undo()
            elif parts[0] == "quit":
                break
            else:
                print("Invalid command!")
        print("Game Over!")

if __name__ == "__main__":
    mode = input("Select mode (human/bot): ")
    game = FreeCell()
    game.play_human()