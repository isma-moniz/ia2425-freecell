import heapq
import copy
import random
from colorama import Fore, Style
import heapq
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

class BoardState:
    def __init__(self, tableau, free_cells, foundations):

        self.move_count = 0
        self.tableau = tableau
        self.free_cells = free_cells
        self.foundations = foundations
        self.deck = [Card(rank, suit) for suit in TYPES for rank in RANKS]
        self.deck_size = len(self.deck)
        random.shuffle(self.deck)

        self.starting_point = False

        self.history = []

    def set_starting_point(self):
        self.starting_point = True

    def is_starting_point(self):
        return self.starting_point

    def set_move_count(self, move_count):
        self.move_count = move_count

    def deal_cards(self):

        for i in range(self.deck_size):
            pos = i % TABLEAU_COUNT
            self.tableau[pos].append(self.deck.pop())

    def get_foundation_score(self):
        """Heuristic score based on how many cards are in the foundations."""
        score = 0
        for suit, foundation in self.foundations.items():
            score += len(foundation) * FOUNDATION_MULTIPLIER  # More cards in foundation is better
        return score

    def get_free_cell_score(self):
        """Heuristic score based on the number of empty free cells."""
        return self.free_cells.count(None) * FREECELL_MULTIPLIER  # More empty free cells is better

    def get_empty_tableau_score(self):
        """Heuristic score based on the number of empty tableau piles."""
        return sum(1 for pile in self.tableau if not pile)  # More empty tableau piles is better

    def get_tableau_order_score(self):
        """Heuristic score based on how well tableau piles are organized."""
        score = 0
        for pile in self.tableau:
            if pile:
                # Check if the tableau is organized in descending order, alternating colors
                valid_sequence = True
                for i in range(1, len(pile)):
                    prev_card = pile[i - 1]
                    curr_card = pile[i]
                    if not (curr_card.value == prev_card.value - 1 and curr_card.color != prev_card.color):
                        valid_sequence = False
                        break
                if valid_sequence:
                    score += len(pile)  # More organized tableau piles are better
        return score * ORDER_MULTIPLIER


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

    def display_card(self, card, last):

        text = str(card)

        if len(text) < CARD_STRING_SIZE:
            pos = (CARD_STRING_SIZE - len(text)) // 2

            text = " " * pos + text

            while len(text) < CARD_STRING_SIZE:
                text += " "


        return text + "|" if not last else text

    def calculate_heuristic(self):
        """Combine all the individual scores into one final heuristic score."""
        foundation_score = self.get_foundation_score()
        free_cell_score = self.get_free_cell_score()
        empty_tableau_score = self.get_empty_tableau_score()
        tableau_order_score = self.get_tableau_order_score()
        win = self.is_winner()

        """
        print("Foundation Score: ", foundation_score)
        #print("FreeCell Score: ", free_cell_score)
        print("Empty_Tableau: ", empty_tableau_score)
        print("Tableau Order: ", tableau_order_score)
        print("Move Count: ", self.move_count)
        print("Are you winning son? ", "Yes dad" if win else "no :(")
        """


        if win: return VICTORY_SCORE

        total_score = foundation_score + free_cell_score + empty_tableau_score + tableau_order_score - self.move_count
        return total_score

    def move_to_freecell(self, tableau_idx):

        if self.tableau[tableau_idx]:
            card = self.tableau[tableau_idx].pop()
            for i in range(4):
                if not self.free_cells[i]:
                    self.free_cells[i] = card
                    #print(f"Moved {card} to free cell {i + 1}")
                    self.move_count += 1
                    return True
        #print("Invalid move!")
        return False

    def move_to_tableau(self, freecell_idx, tableau_idx):
        card = self.free_cells[freecell_idx]
        if card and self.is_valid_tableau_move(tableau_idx, card):
            self.tableau[tableau_idx].append(card)
            self.free_cells[freecell_idx] = None
            #print(f"Moved {card} to tableau {tableau_idx + 1}")
            self.move_count += 1
            return True
        #print("Invalid move!")
        return False

    def move_tableau_to_tableau(self, from_idx, to_idx):
        if self.tableau[from_idx]:
            card = self.tableau[from_idx][-1]
            if self.is_valid_tableau_move(to_idx, card):
                self.tableau[to_idx].append(self.tableau[from_idx].pop())
                #print(f"Moved {card} from tableau {from_idx + 1} to {to_idx + 1}")
                self.move_count += 1
                return True
        #print("Invalid move!")
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
                self.foundations[card.suit].append(card)
                self.tableau[tableau_idx].pop()
                #print(f"Moved {card} to foundation {card.suit}")
                self.move_count += 1
                return True
        #print("Invalid move!")
        return False

    def move_freecell_to_foundation(self, freecell_idx):
        card = self.free_cells[freecell_idx]
        if card and self.is_valid_foundation_move(card):
            self.foundations[card.suit].append(card)
            self.free_cells[freecell_idx] = None
            #print(f"Moved {card} to foundation {card.suit}")
            self.move_count += 1
            return True
        #print("Invalid move!")
        return False

    def is_valid_foundation_move(self, card):
        if not self.foundations[card.suit]:
            return card.rank == 'A'
        top_card = self.foundations[card.suit][-1]
        return card.value == top_card.value + 1

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
        self.move_count += 1

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

    def clone(self):
        return BoardState(self.tableau, self.free_cells, self.foundations)

    def is_winner(self):
        """Check if the game is won (all foundations have 13 cards)."""
        return all(len(foundation) == 13 for foundation in self.foundations.values())


class MaxPriorityQueue:
    def __init__(self):
        self.heap = []
    def push(self, state):
        heapq.heappush(self.heap, state)
    def pop(self):
        return heapq.heappop(self.heap)
    def peek(self):
        return self.heap[0] if self.heap else None
    def is_empty(self):
        return len(self.heap) == 0


class BotMove():
    def __init__(self, board, previous):
        self.score = board.calculate_heuristic()
        self.board = board
        self.previous = previous

    def get_board(self):
        return self.board

    def get_score(self):
        return self.score

    def get_previous(self):
        return self.previous

    def __lt__(self, other):
        return self.score < other.score


class FreecellBot():

    def __init__(self):
        self.queue = MaxPriorityQueue()
        self.plays = []

    def get_possible_moves(self, state):

        for i in range(TABLEAU_COUNT):

            #All move to freecell moves
            board = state.clone()
            if board.move_to_freecell(i): self.queue_move(board, state)

            #All move to tableau moves
            for o in range(FREECELL_COUNT):
                board = state.clone()
                if board.move_to_tableau(o, i): self.queue_move(board, state)

            #All move to foundation moves
            board = state.clone()
            if board.move_to_foundation(i): self.queue_move(board, state)

        for i in range(FREECELL_COUNT):
            board = state.clone()
            if board.move_freecell_to_foundation(i): self.queue_move(board, state)

    def queue_move(self, board, state):
        self.queue.push(BotMove(board, state))

    def get_plays(self, freecell):

        self.plays.clear()
        self.get_possible_moves(freecell.get_board())

        freecell.get_board().set_starting_point()

        while True:

            highest_move = self.queue.pop()
            state = highest_move.get_board()

            print("Heuristic Value: ", state.calculate_heuristic())

            if state.is_winner():
                self.plays.append(highest_move)
                break

            self.get_possible_moves(state)

        #Get list of plays
        if len(self.plays) > 0:
            state = self.plays[len(self.plays) - 1]
            while state.is_starting_point() is not True:
                state = state.get_previous()
                self.plays.append(state)

            self.plays.append(state)

        #Reverse it so the first entry is the start and not the end
        self.plays.reverse()

    def play(self):

        print(len(self.plays))
