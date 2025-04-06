import heapq
import copy
import time
import math
import random
from copy import deepcopy
from types import NoneType, SimpleNamespace

from colorama import Fore, Style
import heapq
from constants import *

from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
THREAD_POOL_EXECUTOR = ThreadPoolExecutor(max_workers=8)
prev_scores = []
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
    
    def __deepcopy__(self, memo):
        return self

class BoardState:
    def __init__(self, tableau, free_cells, foundations, initialize_deck=True):
        self.move_count = 0
        self.tableau = tableau
        self.free_cells = free_cells
        self.foundations = foundations
        self.starting_point = False
        self.history = []
        self.current_weights = SimpleNamespace(**DEFAULT_WEIGHTS)

        if initialize_deck:  # Only initialize deck for new games, not clones
            self.deck = [Card(rank, suit) for suit in TYPES for rank in RANKS]
            self.deck_size = len(self.deck)
            random.shuffle(self.deck)
        else:  # For cloned states
            self.deck = None
            self.deck_size = 0

        self.update_weights()
    
    def get_game_phase(board):
        foundation_progress = sum(len(foundation) for foundation in board.foundations.values()) / 52

        if foundation_progress < 0.2:
            return "early"
        elif foundation_progress < 0.7:
            return "mid"
        else:
            return "late"
        
    def update_weights(self):
        phase = self.get_game_phase()
        # Merge default weights with phase-specific overrides
        weights = {**DEFAULT_WEIGHTS, **WEIGHT_PROFILES.get(phase, {})}
        self.current_weights = SimpleNamespace(**weights)

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
        """Distribute cards to tableau piles only if deck exists"""
        if not hasattr(self, 'deck') or self.deck is None:
            return

        d = deepcopy(self.deck)

        for i in range(len(d)):
            pos = i % TABLEAU_COUNT
            self.tableau[pos].append(d.pop())

    def get_foundation_score(self):
        """Heuristic score based on how many cards are in the foundations."""
        score = 0
        for suit, foundation in self.foundations.items():
            score += len(foundation) * self.current_weights.FOUNDATION_MULTIPLIER
        return score

    def get_free_cell_score(self):
        """Heuristic score based on the number of empty free cells."""
        return self.free_cells.count(None) * self.current_weights.FREECELL_MULTIPLIER

    #TODO: maybe give some score, even if only part of the pile is organized
    def get_tableau_order_score(self):
        """Heuristic score based on how well tableau piles are organized."""
        score = 0
        for pile in self.tableau:
            if pile:
                valid_sequence = True
                for i in range(1, len(pile)):
                    prev_card = pile[i - 1]
                    curr_card = pile[i]
                    if not (curr_card.value == prev_card.value - 1 and curr_card.color != prev_card.color):
                        valid_sequence = False
                        break
                if valid_sequence:
                    score += len(pile) * self.current_weights.ORDER_MULTIPLIER
        return score


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

                if card.value >= 13: continue
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
                        score += self.current_weights.CARD_EXCAVATION_MULTIPLIER * 2
                    else:
                        score += self.current_weights.CARD_EXCAVATION_MULTIPLIER/pos
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

                if card.value >= 13: continue
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
        score = 0
        for pile in self.tableau:
            if len(pile) == 0:
                score += self.current_weights.TABLEAU_EMPTY_SCORE * 2
            else:
                score += self.current_weights.TABLEAU_EMPTY_SCORE / len(pile)
        return score
    
    def get_lookahead_bonus(self, max_depth=2):
        """
        Computes the bonus score from lookahead with improved efficiency and adaptability.
        Dynamically adjusts depth based on game state complexity and adjusts the bonus
        to prevent overly greedy short-term moves.
        Terminates search early if a winning state is found.

        Parameters:
        - max_depth: Maximum search depth (will be adjusted based on game state)

        Returns:
        - A weighted bonus score if a better future state is found, or VICTORY_SCORE if a winning state is found
        """
        # Calculate base score without lookahead to avoid recursion
        current_score = self.calculate_heuristic(False)

        # Return immediately if this is already a winning state
        if self.is_winner() or current_score >= VICTORY_SCORE:
            return VICTORY_SCORE

        # Adjust search depth based on game phase and available empty cells
        phase = self.get_game_phase()
        empty_cells, empty_cascades = self.get_empty_cells_and_cascades()

        # Deeper search when we have more space to work with
        adjusted_depth = max_depth
        if empty_cells >= 2 or empty_cascades >= 1:
            adjusted_depth += 1

        # Deeper in late game when decisions are more critical
        if phase == "late":
            adjusted_depth += 1

        # Limit depth if board is too complex to avoid timeout
        card_count = sum(len(pile) for pile in self.tableau)
        if card_count > 40:  # Still many cards on the tableau
            adjusted_depth = min(adjusted_depth, 1)

        # Use the improved lookahead function
        if hasattr(self, 'improved_look_ahead_score_boost'):
            best_future_score = self.improved_look_ahead_score_boost(adjusted_depth, 0)
        else:
            # Fallback to original if improved version not available
            best_future_score = self.look_ahead_score_boost(adjusted_depth, 0)

        # If a winning state was found, return victory score immediately
        if best_future_score >= VICTORY_SCORE:
            return VICTORY_SCORE

        # Calculate raw bonus
        raw_bonus = best_future_score - current_score

        # Apply diminishing returns to prevent greediness
        if raw_bonus > 0:
            # Scale bonus based on game phase
            if phase == "early":
                # Early game: moderate lookahead influence
                bonus = raw_bonus * 0.6
            elif phase == "mid":
                # Mid game: higher lookahead influence
                bonus = raw_bonus * 0.8
            else:
                # Late game: strong lookahead influence
                bonus = raw_bonus * 0.9

            # Apply logarithmic scaling to very large bonuses
            if bonus > 50:
                bonus = 50 + math.log(bonus - 50 + 1, 2) * 10

            return bonus
        else:
            # Small negative bonus for states that lead to worse positions
            # This helps avoid moves that look good now but lead to problems
            return max(-10, raw_bonus * 0.3)
        
    def is_new_state(self, visited):
        return not any(self == v for v in visited)

    def get_sequential_chains_score(self):
        """Reward long sequential chains that are correctly ordered and can be moved together."""
        score = 0
        for pile in self.tableau:
            if len(pile) <= 1:
                continue

            # Find continuous chains
            current_chain = 1
            longest_chain = 1
            for i in range(1, len(pile)):
                prev_card = pile[i - 1]
                curr_card = pile[i]

                if curr_card.value == prev_card.value - 1 and curr_card.color != prev_card.color:
                    current_chain += 1
                    longest_chain = max(longest_chain, current_chain)
                else:
                    current_chain = 1

            # Reward exponentially for longer chains
            chain_score = longest_chain ** 1.5 * self.current_weights.CHAIN_MULTIPLIER

            # Extra bonus if the top card of a chain can go to foundation
            if longest_chain > 1 and pile:
                top_card = pile[-1]
                if self.can_go_to_foundation(top_card):
                    chain_score *= 1.3

            score += chain_score
        return score
    
    def get_blocked_cards_penalty(self):
        """Penalize situations where lower cards are blocked by higher cards of same color."""
        penalty = 0

        # Track which cards we need for immediate foundation building
        needed_cards = {}
        for suit in TYPES:
            if not self.foundations[suit]:
                needed_value = 1  # Ace
            else:
                top_card = self.foundations[suit][-1]
                needed_value = top_card.value + 1

            if needed_value <= 13:  # Only if not complete
                needed_cards[suit] = needed_value

        # Check for blocked cards
        for pile in self.tableau:
            for i, card in enumerate(pile):
                # Check if this is a needed card
                if card.suit in needed_cards and card.value == needed_cards[card.suit]:
                    # Count how many cards are above it
                    cards_above = len(pile) - i - 1

                    # Higher penalty if blocked by many cards
                    if cards_above > 0:
                        penalty += cards_above * self.current_weights.BLOCKED_CARD_PENALTY

                        # Extra penalty if blocked by cards of same color (which can't help uncover it)
                        for j in range(i + 1, len(pile)):
                            if pile[j].color == card.color:
                                penalty += self.current_weights.SAME_COLOR_BLOCK_PENALTY

        return penalty

    def get_balanced_foundation_score(self):
        """Reward more evenly built foundations rather than building one too far ahead."""
        foundation_heights = [len(self.foundations[suit]) for suit in TYPES]
        avg_height = sum(foundation_heights) / len(foundation_heights)

        # Calculate standard deviation to measure imbalance
        variance = sum((h - avg_height) ** 2 for h in foundation_heights) / len(foundation_heights)
        std_dev = variance ** 0.5

        # Small std_dev means more balanced foundations
        balance_score = (5 - std_dev) * self.current_weights.BALANCE_MULTIPLIER

        # Ensure it's not negative
        return max(0, balance_score)

    def can_go_to_foundation(self, card):
        """Check if a card can be moved to the foundation immediately."""
        if card.rank == 'A' and not self.foundations[card.suit]:
            return True

        if self.foundations[card.suit]:
            top_card = self.foundations[card.suit][-1]
            return card.value == top_card.value + 1

        return False

    def get_potential_moves_score(self):
        """Evaluate the number of potential moves available."""
        potential_moves = 0

        # Check for movable cards between tableau piles
        for i in range(TABLEAU_COUNT):
            if not self.tableau[i]:
                continue

            bottom_card = self.tableau[i][-1]

            # Check if it can move to an empty tableau
            if any(len(pile) == 0 for pile in self.tableau):
                potential_moves += 1

            # Check if it can move to another tableau pile
            for j in range(TABLEAU_COUNT):
                if i == j or not self.tableau[j]:
                    continue

                target_card = self.tableau[j][-1]
                if bottom_card.value == target_card.value - 1 and bottom_card.color != target_card.color:
                    potential_moves += 1

        # Value of having potential moves
        return potential_moves * self.current_weights.POTENTIAL_MOVE_MULTIPLIER

    def improved_look_ahead_score_boost(self, max_depth=3, current_depth=0, visited=None, alpha=-float('inf'),
                                        beta=float('inf')):
        """Enhanced look-ahead with alpha-beta pruning for better performance.
        Now terminates early if a winning state is found."""
        if visited is None:
            visited = set()

        # Create a hashable representation of the current state

        visited.add(self)

        # Check for victory condition immediately
        if self.is_winner():
            return VICTORY_SCORE

        base_score = self.calculate_heuristic(False)

        # Also terminate if score is already at victory level
        if base_score >= VICTORY_SCORE:
            return VICTORY_SCORE

        # Stop recursion at max depth
        if current_depth >= max_depth:
            return base_score

        best_score = base_score
        next_states = []

        # Generate all possible moves (same as original)
        for i in range(TABLEAU_COUNT):
            new_state = self.clone()
            if new_state.move_to_freecell(i) and new_state not in visited:
                next_states.append(new_state)

            new_state = self.clone()
            if new_state.move_to_foundation(i):
                next_states.append(new_state)
                # Early termination - if moving to foundation creates a winning state
                if new_state.is_winner():
                    return VICTORY_SCORE

            for j in range(FREECELL_COUNT):
                new_state = self.clone()
                if new_state.move_to_tableau(j, i) and new_state not in visited:
                    next_states.append(new_state)

            for j in range(TABLEAU_COUNT):
                if i == j: continue

                new_state = self.clone()
                if new_state.move_tableau_to_tableau(i, j) and new_state not in visited:
                    next_states.append(new_state)

        for j in range(FREECELL_COUNT):
            new_state = self.clone()
            if new_state.move_freecell_to_foundation(j) and new_state not in visited:
                next_states.append(new_state)
                # Early termination - if moving to foundation creates a winning state
                if new_state.is_winner():
                    return VICTORY_SCORE

        # Instead of evaluating all states, sort and only look at the most promising ones
        next_states.sort(key=lambda s: s.calculate_heuristic(False), reverse=True)

        # Only consider the top N states to improve search efficiency
        top_n = len(next_states) #min(8, len(next_states))

        for next_state in next_states[:top_n]:
            # Alpha-beta pruning
            score = next_state.improved_look_ahead_score_boost(max_depth, current_depth + 1, visited, alpha, beta)

            # Early termination if a winning state was found in the branch
            if score >= VICTORY_SCORE:
                return VICTORY_SCORE

            best_score = max(best_score, score)

            alpha = max(alpha, best_score)
            if beta <= alpha:
                break  # Beta cutoff

        return best_score

    # Now modify the calculate_heuristic method to include these new evaluations
    def calculate_heuristic(self, apply_bonus=True):
        # Original scores
        foundation_score = self.get_foundation_score()
        free_cell_score = self.get_free_cell_score()
        empty_tableau_score = self.get_tableau_empty_score()
        tableau_order_score = self.get_tableau_order_score()
        card_excavation_score = self.card_excavation_score()

        phase = self.get_game_phase()
        weights = self.current_weights

        # New scores
        sequential_chains_score = self.get_sequential_chains_score()
        blocked_cards_penalty = self.get_blocked_cards_penalty()
        balanced_foundation_score = self.get_balanced_foundation_score()
        potential_moves_score = self.get_potential_moves_score()

        move_penalty = self.move_count * weights.MOVE_COUNT_SCORE

        if self.is_winner():
            return VICTORY_SCORE

        base_score = (
                foundation_score +
                free_cell_score +
                empty_tableau_score +
                tableau_order_score +
                card_excavation_score +
                sequential_chains_score +
                balanced_foundation_score +
                potential_moves_score -
                blocked_cards_penalty -
                move_penalty
        )

        if apply_bonus:
            if (len(prev_scores) == 10):
                stagnation = (max(prev_scores) - min(prev_scores)) < STAGNATION_THRESHOLD
                if stagnation:
                    print("stagnated")
                    print(prev_scores)
            else: 
                stagnation = False
            if stagnation:
                print("Calling dfs!")
                for depth in range(2,6):
                    bonus = self.improved_look_ahead_score_boost(depth)
                    if bonus > STAGNATION_THRESHOLD * 2:
                        break
                total_score = base_score + bonus
            else:
                total_score = base_score
            prev_scores.append(total_score)
            if len(prev_scores) > 10:
                prev_scores.pop(0)
        else:
            total_score = base_score
        
        # Append the actual score used for this state
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
        """Create a simulation-safe copy without deck operations"""
        new_state = BoardState(
            [list(pile) for pile in self.tableau],
            list(self.free_cells),
            {suit: list(pile) for suit, pile in self.foundations.items()},
            initialize_deck=False  # Don't create deck for clones
        )
        new_state.move_count = self.move_count
        new_state.current_weights = SimpleNamespace(**self.current_weights.__dict__)
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
        self.score = board.calculate_heuristic(True)
        self.board = board
        self.previous = previous

    def get_board(self):
        return self.board

    def get_score(self):
        return self.score

    def get_previous(self):
        return self.previous

    def is_starting_point(self):
        return self.board.is_starting_point()

    def __lt__(self, other):
        return self.score < other.score


class FreecellBot():

    def __init__(self):
        self.start_time = time.time()
        self.execution_time = None
        self.queue = MaxPriorityQueue()
        self.moves = []
        self.plays = []

        self.previous = set()
        self.start_board = None

    def get_possible_moves(self, state, last_move):

        for i in range(TABLEAU_COUNT):

            #All move to freecell moves
            board = state.clone()
            if board.move_to_freecell(i): self.queue_move(board, last_move)

            #All move to tableau moves
            for o in range(FREECELL_COUNT):
                board = state.clone()
                if board.move_to_tableau(o, i): self.queue_move(board, last_move)

            #All move to foundation moves
            board = state.clone()
            if board.move_to_foundation(i): self.queue_move(board, last_move)

            #Move from one tableau to another
            for o in range(TABLEAU_COUNT):
                if i == o: continue

                board = state.clone()
                if board.move_tableau_to_tableau(i, o): self.queue_move(board, last_move)

                #SuperMove
                """
                for cardsCount in range(len(state.tableau[i])):
                    board = state.clone()
                    if board.move_supermove(i, o, cardsCount): self.queue_move(board, state)
                """

        #Move from the freecell to the foundation
        for i in range(FREECELL_COUNT):
            board = state.clone()
            if board.move_freecell_to_foundation(i): self.queue_move(board, last_move)

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

        self.get_possible_moves(self.start_board, None)

        while self.queue.size() > 0:


            highest_move = self.queue.pop()
            state = highest_move.get_board()

            yield state

            # print("\n-----------------------------")
            #print("Queue Size: ", self.queue.size())
            print("Heuristic Value: ", state.calculate_heuristic())
           # print("Previous Size: ", len(self.previous))


            if state.is_winner():
                stop_time = time.time()
                self.execution_time = stop_time - self.start_time
                self.moves.append(highest_move)
                print("Winner!!!")
                print(f"Run time: {self.execution_time:.4f} seconds")
                #state.display()
                break

            #state.display()

            self.get_possible_moves(state, highest_move)

        if len(self.moves) > 0:

            while self.moves[-1] is not None:
                self.plays.append(self.moves[-1].get_board())
                self.moves.append(self.moves[-1].get_previous())

            self.plays.append(self.start_board)
            self.plays.reverse()
