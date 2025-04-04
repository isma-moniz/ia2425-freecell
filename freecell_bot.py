import heapq
import copy
import random
from copy import deepcopy

from colorama import Fore, Style
import heapq
from constants import *

from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Cards
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = CARD_VALUES[rank]
        self.color = Fore.RED if suit in ['Hearts', 'Diamonds'] else Fore.BLACK

    def __repr__(self):
        return f'{self.color}{self.rank} of {self.suit}{Style.RESET_ALL}'

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.rank == other.rank and self.suit == other.suit
        return False

    def __hash__(self):
        return hash((self.rank, self.suit))

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

    def __eq__(self, other):

        # print("EQ STARTED")

        if not isinstance(other, BoardState):
            return False

        # Compare corresponding cards in tableau
        for i in self.tableau:
            if i not in other.tableau: return False

        # Check free cells equality
        for i in self.free_cells:
            if i not in other.free_cells: return False

        # Check foundations equality: Compare both length and the actual cards in the foundation
        for suit in TYPES:

            # print("foundations", self.foundations[suit], other.foundations[suit])

            if len(self.foundations[suit]) != len(other.foundations[suit]):
                return False

            if self.foundations[suit] != other.foundations[suit]:  # Compare the actual cards in the foundation piles
                return False

        # print("returning true")
        return True


    def __hash__(self):
        tableau_hash = hash(tuple(tuple(pile) for pile in self.tableau))
        free_cells_hash = hash(tuple(self.free_cells))
        foundations_hash = hash(tuple((k, tuple(v)) for k, v in self.foundations.items()))

        return hash((tableau_hash, free_cells_hash, foundations_hash))

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

    def card_excavation_score(self):

        score = 0

        for extra,suit in enumerate(TYPES):

            if not self.foundations[suit]:
                next_card_val = 1
            else:
                card = self.foundations[suit][-1]

                if card.value >= 13: continue;
                next_card_val = card.value + 1


            check = False
            for i in range(TABLEAU_COUNT):
                for index,card in enumerate(self.tableau[i]):

                    if card.value != next_card_val: continue
                    if card.suit != suit: continue
                    check = True

                    pos = (len(self.tableau[i]) - index)

                    score += extra * 2 #The algorithm favours some suits over anothers
                    #This is meant to break stalemates so if there are 2 different cards on the same depth, one will be prefered by the algorithm over another

                    if pos == 0:
                        score += CARD_EXCAVATION_MULTIPLIER * 2
                    else:
                        score += CARD_EXCAVATION_MULTIPLIER/pos
                    break

                if check: break


        return score


    def closest_card_score(self):


        dist = 100000

        for suit in TYPES:

            if not self.foundations[suit]:
                next_card_val = 1
            else:
                card = self.foundations[suit][-1]

                if card.value >= 13: continue;
                next_card_val = card.value + 1

            check = False
            for i in range(TABLEAU_COUNT):
                for index, card in enumerate(self.tableau[i]):

                    if card.value != next_card_val: continue
                    if card.suit != suit: continue

                    from_top = len(self.tableau[i]) - index

                    if dist > from_top:
                        dist = from_top
                        if dist == 0 : return 100

                    break

                if check: break

        return 80 / dist

    def get_tableau_empty_score(self):

        score = 0;

        for pile in self.tableau:

            if len(pile) == 0:
                score += TABLEAU_EMPTY_SCORE * 2;
                continue

            score += TABLEAU_EMPTY_SCORE / len(pile)

        return score

    def calculate_heuristic(self):
        """Combine all the individual scores into one final heuristic score."""

        foundation_score = self.get_foundation_score()
        free_cell_score = self.get_free_cell_score()
        empty_tableau_score = self.get_tableau_empty_score()
        tableau_order_score = self.get_tableau_order_score()
        card_excavation_score = self.card_excavation_score()

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

        total_score = foundation_score + free_cell_score + empty_tableau_score + tableau_order_score + card_excavation_score - self.move_count * MOVE_COUNT_SCORE
        return total_score

    def move_to_freecell(self, tableau_idx):
        if self.tableau[tableau_idx]:
            for i in range(4):
                if not self.free_cells[i]:
                    card = self.tableau[tableau_idx].pop()
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

                #print(f"Moved {card} from tableau {from_idx + 1} to {to_idx + 1} ({previous_card})")
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
            #print(f"Cannot move {len(cards_to_move)} cards. More empty cells or cascades needed.")
            return False

        if not self.is_valid_sequence(cards_to_move):
            #print("The selected cards do not form a valid sequence!")
            return False

        if self.tableau[target_tableau_idx]:
            top_card = self.tableau[target_tableau_idx][-1]
            leftmost_card = cards_to_move[0]
            if not (leftmost_card.value == top_card.value - 1 and leftmost_card.color != top_card.color):
                #print(f"Invalid move: {leftmost_card} cannot be placed on {top_card}!")
                return False

        self.tableau[target_tableau_idx].extend(cards_to_move)

        for _ in range(no_cards):
            self.tableau[target_tableau_idx].append(self.tableau[source_tableau_idx].pop())

        #print(f"Moved {len(cards_to_move)} cards from tableau {source_tableau_idx + 1} to tableau {target_tableau_idx + 1}")
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

        new_state = BoardState(deepcopy(self.tableau), deepcopy(self.free_cells), deepcopy(self.foundations))
        new_state.move_count = self.move_count

        return new_state

    def is_winner(self):
        """Check if the game is won (all foundations have 13 cards)."""
        return all(len(foundation) == 13 for foundation in self.foundations.values())


class MaxPriorityQueue:
    def __init__(self):
        self.heap = []

    def push(self, state):
        heapq.heappush(self.heap, (-state.get_score(), state))

    def pop(self):
        return heapq.heappop(self.heap)[1]

    def peek(self):
        return self.heap[0] if self.heap else None

    def is_empty(self):
        return len(self.heap) == 0

    def size(self):
        return len(self.heap)


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

        self.previous = set()
        self.start_board = None

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

            #Move from one tableau to another
            for o in range(TABLEAU_COUNT):
                if i == o: continue

                board = state.clone()
                if board.move_tableau_to_tableau(i, o): self.queue_move(board, state)

                #SuperMove
                """
                for cardsCount in range(len(state.tableau[i])):
                    board = state.clone()
                    if board.move_supermove(i, o, cardsCount): self.queue_move(board, state)
                """

        #Move from the freecell to the foundation
        for i in range(FREECELL_COUNT):
            board = state.clone()
            if board.move_freecell_to_foundation(i): self.queue_move(board, state)

    def queue_move(self, board, state):

        for b in self.previous:
            if b == board:
                """
                board.display()
                b.display()
                self.start_board.display()

                print(len(self.previous))
                print(board, b)
                """

                return

        """
        print("added")

        board.display()
        """

        self.previous.add(board)
        self.queue.push(BotMove(board, state))

    def get_plays(self, freecell):

        self.plays.clear()
        self.previous.clear()

        self.start_board = freecell.get_board()
        self.start_board.set_starting_point()
        self.previous.add(self.start_board)

        self.get_possible_moves(self.start_board)

        while self.queue.size() > 0:


            highest_move = self.queue.pop()
            state = highest_move.get_board()

            # print("\n-----------------------------")
            #print("Queue Size: ", self.queue.size())
            #print("Heuristic Value: ", state.calculate_heuristic())
           # print("Previous Size: ", len(self.previous))


            if state.is_winner():
                self.plays.append(highest_move)
                print("Winner!!!")
                #state.display()
                break

            state.display()

            self.get_possible_moves(state)





    def play(self):

        print(len(self.plays))
