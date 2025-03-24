import heapq
import copy
import heapq
from constants import *

class MaxPriorityQueue:
    def __init__(self):
        self.heap = []

    def push(self, item):
        # Negate the value to simulate a max-heap
        heapq.heappush(self.heap, -item)

    def pop(self):
        # Negate the value to get back the original value
        return -heapq.heappop(self.heap)

    def peek(self):
        # Peek the highest priority item (without removing it)
        return -self.heap[0] if self.heap else None

    def is_empty(self):
        return len(self.heap) == 0

class BoardState:
    def __init__(self, tableau, free_cells, foundations):
        self.tableau = tableau
        self.free_cells = free_cells
        self.foundations = foundations
        self.move_count = 0

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
        return score

    def calculate_heuristic(self):
        """Combine all the individual scores into one final heuristic score."""
        foundation_score = self.get_foundation_score()
        #free_cell_score = self.get_free_cell_score() #I dont think this is necessary.
        empty_tableau_score = self.get_empty_tableau_score()
        tableau_order_score = self.get_tableau_order_score()
        win = self.is_winner()

        print("Foundation Score: ", foundation_score)
        #print("FreeCell Score: ", free_cell_score)
        print("Empty_Tableau: ", empty_tableau_score)
        print("Tableau Order: ", tableau_order_score)
        print("Are you winning son? ", "Yes dad" if win else "no :(")


        if win: return VICTORY_SCORE

        total_score = foundation_score + empty_tableau_score + tableau_order_score
        return total_score

    def is_winner(self):
        """Check if the game is won (all foundations have 13 cards)."""
        return all(len(foundation) == 13 for foundation in self.foundations.values())


class FreecellBot():
    def __init__(self, board):
        self.queue = MaxPriorityQueue()

    def get_possible_moves(self, freecell):

        board = freecell.get_board()

        for i in range(TABLEAU_COUNT):

            result = freecell.move_to_freecell(i)
            if(result != None): self.queue.push(result)



    def play(self, freecell):

        self.get_possible_moves(freecell)
