# gui.py
import threading
import queue
import time
import pygame
import sys
from constants import TYPES, RANKS
from pygame.locals import *
from freecell_game import FreeCell
from freecell_bot import FreecellBot

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CARD_WIDTH = 71
CARD_HEIGHT = 96
MARGIN = 20
TABLEAU_SPACING = 80
FREECELL_SPACING = 80
FOUNDATION_SPACING = 80
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 60

# Colors
CASINO_GREEN = (21, 109, 69)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BORDEAUX = (109, 21, 61)
BLUE = (25, 21, 109)
LIGHT_BLUE = (100, 100, 255)
GRAY = (200, 200, 200)
DARK_GREEN = (0, 100, 0)
DARK_GOLD = (105, 109, 21)
VICTORY_COLOR_GOLD = (255, 215, 0)

class FreeCellGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('FreeCell Solitaire')
        self.clock = pygame.time.Clock()
        self.large_font = pygame.font.SysFont('Copperplate Gothic', 48)
        self.medium_font = pygame.font.SysFont('Copperplate Gothic', 36)
        self.small_font = pygame.font.SysFont('Copperplate Gothic', 24)
        self.tiny_font = pygame.font.SysFont('Copperplate Gothic', 12)
        
        # Game state
        self.game = None
        self.bot = None
        self.current_mode = None
        self.show_main_menu = True
        self.show_game = False
        self.bot_thread = None
        self.bot_moves = queue.Queue()
        self.show_victory = False
        
        # Card dragging
        self.dragging = False
        self.dragged_card = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.origin_pile = None
        self.origin_pile_type = None
        #TODO: why no target pile?

        # Load card images
        self.card_images = self.load_card_spritesheet()

        # Human timer
        self.human_start_time = 0
        self.human_mode_timer = 0
        self.timer_font = pygame.font.SysFont('Arial', 20)

    def load_card_spritesheet(self):
        sheet = pygame.image.load("sprites/cards.png").convert()
        cards = {}

        for row, rank in enumerate(RANKS):
            for col, suit in enumerate(TYPES):
                x = col * (CARD_WIDTH + 4) # 4 is the offset in between cards
                y = row * (CARD_HEIGHT + 4)

                rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
                image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
                image.blit(sheet, (0,0), rect)

                cards[(rank, suit)] = image
        return cards

    def draw_main_menu(self):
        """Draw the main menu with mode selection"""
        self.screen.fill(CASINO_GREEN)
        
        # Title
        title = self.large_font.render("FreeCell Solitaire", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.screen.blit(title, title_rect)
        
        # Human mode button
        human_rect = pygame.Rect(SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 
                               SCREEN_HEIGHT//2 - BUTTON_HEIGHT, 
                               BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, BORDEAUX, human_rect, border_radius=10)
        human_text = self.medium_font.render("Human", True, BLACK)
        human_text_rect = human_text.get_rect(center=human_rect.center)
        self.screen.blit(human_text, human_text_rect)
        
        # Bot mode button
        bot_rect = pygame.Rect(SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 
                             SCREEN_HEIGHT//2 + BUTTON_HEIGHT, 
                             BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, BLUE, bot_rect, border_radius=10)
        bot_text = self.medium_font.render("Bot", True, BLACK)
        bot_text_rect = bot_text.get_rect(center=bot_rect.center)
        self.screen.blit(bot_text, bot_text_rect)
        
        pygame.display.flip()
        return human_rect, bot_rect

    def init_game(self, mode):
        """Initialize the game based on selected mode"""
        self.game = FreeCell()
        self.current_mode = mode
        self.show_main_menu = False
        self.show_game = True
        self.show_victory = False

        # Start timer for human mode
        if mode == "human":
            self.human_start_time = time.time()

        elif mode == "bot":
            self.bot_moves = queue.Queue()
            self.bot_thread = threading.Thread(target=self.run_bot_thread)
            self.bot_thread.start()

    def run_bot_thread(self):
        self.bot = FreecellBot()
        for state in self.bot.get_plays(self.game):
            self.bot_moves.put(state)
            #pygame.time.wait(50)

    def draw_game(self):
        """Draw the actual game interface"""
        self.screen.fill(CASINO_GREEN)

        # Draw timer in human mode
        if self.current_mode == "human" and not self.game.board_state.is_winner():
            self.human_mode_timer = time.time() - self.human_start_time
            timer_text = self.timer_font.render(
                f"Time: {self.human_mode_timer:.2f}", 
                True, 
                WHITE
            )
            self.screen.blit(timer_text, (SCREEN_WIDTH - 150, 10))
        
        # Draw mode indicator
        mode_text = self.tiny_font.render(f"Mode: {self.current_mode}", True, WHITE)
        self.screen.blit(mode_text, (10, 10))
        
        # Draw menu button
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, 10, 100, 40)
        pygame.draw.rect(self.screen, BLUE, menu_rect, border_radius=5)
        menu_text = self.small_font.render("Menu", True, WHITE)
        menu_text_rect = menu_text.get_rect(center=menu_rect.center)
        self.screen.blit(menu_text, menu_text_rect)
        
        # ===== DRAW FREE CELLS WITH LABELS =====
        freecell_label = self.small_font.render("Free Cells", True, WHITE)
        self.screen.blit(freecell_label, (MARGIN, MARGIN + 30))
        
        for i in range(4):
            x = MARGIN + FREECELL_SPACING * i
            y = MARGIN + 60
            
            # Draw cell background
            pygame.draw.rect(self.screen, BORDEAUX, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=5)
            pygame.draw.rect(self.screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=5)
            
            # Draw cell number
            cell_num = self.small_font.render(str(i+1), True, WHITE)
            self.screen.blit(cell_num, (x + 5, y + 5))
            
            # Draw card if present
            if self.game.board_state.free_cells[i]:
                card = self.game.board_state.free_cells[i]
                self.screen.blit(self.card_images[(card.rank, card.suit)], (x, y))
        
        # ===== DRAW FOUNDATIONS WITH LABELS =====
        foundation_label = self.small_font.render("Foundations", True, WHITE)
        self.screen.blit(foundation_label, (SCREEN_WIDTH - 188, MARGIN + 30))
        
        for i, suit in enumerate(['Hearts', 'Diamonds', 'Clubs', 'Spades']):
            x = SCREEN_WIDTH - FOUNDATION_SPACING * (4 - i) - 12
            y = MARGIN + 60
            
            # Draw foundation background
            pygame.draw.rect(self.screen, DARK_GOLD, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=5)
            pygame.draw.rect(self.screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=5)
            
            # Draw suit symbol
            suit_color = RED if suit in ['Hearts', 'Diamonds'] else BLACK
            suit_text = self.small_font.render(suit[0], True, suit_color)
            self.screen.blit(suit_text, (x + CARD_WIDTH//2 - 5, y + CARD_HEIGHT//2 - 10))
            
            # Draw card if present
            if self.game.board_state.foundations[suit]:
                card = self.game.board_state.foundations[suit][-1]
                self.screen.blit(self.card_images[(card.rank, card.suit)], (x, y))
        
        # ===== DRAW TABLEAU WITH LABELS =====
        tableau_label = self.small_font.render("Tableau", True, WHITE)
        self.screen.blit(tableau_label, (MARGIN, MARGIN + CARD_HEIGHT + 80))
        
        for i in range(8):
            x = MARGIN + TABLEAU_SPACING * i
            y = MARGIN + CARD_HEIGHT + 100
            
            # Draw pile number
            pile_num = self.small_font.render(str(i+1), True, WHITE)
            self.screen.blit(pile_num, (x + CARD_WIDTH//2 - 5, y + 10))
            
            # Draw cards in pile
            if not self.game.board_state.tableau[i]:
                # Draw empty pile indicator
                pygame.draw.rect(self.screen, DARK_GREEN, (x, y + 35, CARD_WIDTH, CARD_HEIGHT), border_radius=5)
                pygame.draw.rect(self.screen, BLACK, (x, y + 35, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=5)
            else:
                for j, card in enumerate(self.game.board_state.tableau[i]):
                    card_y = y + 35 + j * 25
                    self.screen.blit(self.card_images[(card.rank, card.suit)], (x, card_y))
        
        # Draw dragged card if any
        if self.dragging and self.dragged_card:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.screen.blit(self.card_images[(self.dragged_card.rank, self.dragged_card.suit)], 
                        (mouse_x - self.drag_offset_x, mouse_y - self.drag_offset_y))
        
        pygame.display.flip()
        return menu_rect
    
    def draw_victory_screen(self):
        """Simplified victory screen showing seconds"""
        self.screen.fill(CASINO_GREEN)
        
        # Get time in seconds (bot) or fallback to human timer
        elapsed = (self.bot.execution_time if hasattr(self, 'bot') and self.bot.execution_time 
                else time.time() - self.human_start_time)
        time_text = f"Time: {elapsed:.2f} seconds"
        
        # Create text elements
        elements = [
            (self.large_font.render("You Won!", True, VICTORY_COLOR_GOLD)),
            (self.medium_font.render(time_text, True, WHITE)),
            (self.medium_font.render(f"Moves: {self.game.board_state.move_count}", True, WHITE))
        ]
        
        # Draw all elements centered
        y_pos = SCREEN_HEIGHT // 3
        for element in elements:
            rect = element.get_rect(center=(SCREEN_WIDTH//2, y_pos))
            self.screen.blit(element, rect)
            y_pos += 60
        
        # Draw menu button
        btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, y_pos, 200, 50)
        pygame.draw.rect(self.screen, BLUE, btn_rect, border_radius=5)
        btn_text = self.medium_font.render("Menu", True, WHITE)
        self.screen.blit(btn_text, btn_text.get_rect(center=btn_rect.center))
        
        pygame.display.flip()
        return btn_rect

    def get_card_at_pos(self, pos):
        """Returns the top card at given position if it's movable"""
        x, y = pos
        
        # Check free cells (always movable if present)
        for i in range(4):
            cell_x = MARGIN + FREECELL_SPACING * i
            cell_y = MARGIN + 60
            if (cell_x <= x <= cell_x + CARD_WIDTH and 
                cell_y <= y <= cell_y + CARD_HEIGHT and
                self.game.board_state.free_cells[i]):
                return self.game.board_state.free_cells[i], 'freecell', i
        
        # Check tableau piles (only top card is movable) #TODO: for now ;)
        for i in range(8):
            pile_x = MARGIN + TABLEAU_SPACING * i
            pile_y = MARGIN + CARD_HEIGHT + 100
            
            if (pile_x <= x <= pile_x + CARD_WIDTH and 
                self.game.board_state.tableau[i]):
                top_card_y = pile_y + (len(self.game.board_state.tableau[i]) - 1) * 25
                if top_card_y <= y <= top_card_y + CARD_HEIGHT:
                    return self.game.board_state.tableau[i][-1], 'tableau', i
        
        return None, None, None

    def handle_card_drop(self, pos):
        """Handles card drops with proper validation"""
        if not self.dragged_card or self.origin_pile_type is None:
            return
        
        x, y = pos
        new_game_state = False
        
        # First check if we're in the top area (free cells or foundations)
        if MARGIN + 60 <= y <= MARGIN + 60 + CARD_HEIGHT:
            # Check free cells first (left side)
            for i in range(4):
                cell_x = MARGIN + FREECELL_SPACING * i
                if cell_x <= x <= cell_x + CARD_WIDTH:
                    if not self.game.board_state.free_cells[i] and self.origin_pile_type == 'tableau':
                        new_game_state = self.game.move_to_freecell(self.origin_pile)
                        print(f"Dropped card at freecell nr {i + 1}")
                        break
            
            # If not dropped on free cell, check foundations (right side)
            if not new_game_state:
                for i, suit in enumerate(['Hearts', 'Diamonds', 'Clubs', 'Spades']):
                    foundation_x = SCREEN_WIDTH - FOUNDATION_SPACING * (4 - i) - 12
                    if foundation_x <= x <= foundation_x + CARD_WIDTH:
                        if self.is_valid_foundation_move(self.dragged_card, suit):
                            if self.origin_pile_type == 'freecell':
                                new_game_state = self.game.move_freecell_to_foundation(self.origin_pile)
                            elif self.origin_pile_type == 'tableau':
                                new_game_state = self.game.move_to_foundation(self.origin_pile)
                        break
        
        # Check tableau drop (main area)
        elif MARGIN + CARD_HEIGHT + 100 <= y <= SCREEN_HEIGHT:
            for i in range(8):
                pile_x = MARGIN + TABLEAU_SPACING * i
                if pile_x <= x <= pile_x + CARD_WIDTH:
                    if self.origin_pile_type == 'freecell':
                        if self.is_valid_tableau_move(i, self.dragged_card):
                            new_game_state = self.game.move_to_tableau(self.origin_pile, i)
                    elif self.origin_pile_type == 'tableau' and i != self.origin_pile:
                        if self.is_valid_tableau_move(i, self.dragged_card):
                            new_game_state = self.game.move_tableau_to_tableau(self.origin_pile, i)
                    break
        
        if new_game_state:
            self.game.board_state = new_game_state
        else:
            print(f"Failed to drop card at ({x},{y})")
            print(f"Origin: {self.origin_pile_type} {self.origin_pile}")
            print(f"Dragged card: {self.dragged_card}")

    def is_valid_tableau_move(self, pile_idx, card):
        """Check if card can be placed on tableau pile"""
        if not self.game.board_state.tableau[pile_idx]:
            return True  # Empty pile accepts any card
        
        top_card = self.game.board_state.tableau[pile_idx][-1]
        return (card.value == top_card.value - 1 and 
                card.color != top_card.color)

    def is_valid_foundation_move(self, card, suit):
        """Check if card can be placed on foundation"""
        if card.suit != suit:
            return False
        if not self.game.board_state.foundations[suit]:
            return card.rank == 'A'
        top_card = self.game.board_state.foundations[suit][-1]
        return card.value == top_card.value + 1

    def handle_game_events(self):
        """Handles all game events including drag-and-drop"""
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, 10, 100, 40)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            # Mouse click - start dragging
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if menu_rect.collidepoint(event.pos):
                    self.show_main_menu = True
                    self.show_game = False
                    continue
                
                card, pile_type, pile_idx = self.get_card_at_pos(event.pos)
                if card:
                    self.dragging = True
                    self.dragged_card = card
                    self.origin_pile_type = pile_type
                    self.origin_pile = pile_idx
                    
                    # Calculate drag offset for smooth movement
                    mouse_x, mouse_y = event.pos
                    if pile_type == 'tableau':
                        card_x = MARGIN + TABLEAU_SPACING * pile_idx
                        card_y = MARGIN + CARD_HEIGHT + 100 + (len(self.game.board_state.tableau[pile_idx])-1)*25
                    else:  # freecell
                        card_x = MARGIN + FREECELL_SPACING * pile_idx
                        card_y = MARGIN + 60
                    
                    self.drag_offset_x = mouse_x - card_x
                    self.drag_offset_y = mouse_y - card_y
            
            # Mouse release - attempt drop
            elif event.type == MOUSEBUTTONUP and event.button == 1 and self.dragging:
                self.handle_card_drop(event.pos)
                self.dragging = False
                self.dragged_card = None
                self.origin_pile = None
                self.origin_pile_type = None
            
            # Keyboard controls
            elif event.type == KEYDOWN:
                if event.key == K_u:  # Undo
                    self.game.undo()
                    # self.game.board_state = self.game.get_board()
                elif event.key == K_r:  # Reset
                    self.init_game(self.current_mode)

    def run_bot_move(self):
        """Execute a single bot move"""
        if self.current_mode == "bot" and not self.game.board_state.is_winner():
            self.game.play_bot()

    def run(self):
        """Main game loop"""
        while True:
            if self.show_main_menu:
                human_rect, bot_rect = self.draw_main_menu()
                
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        if human_rect.collidepoint(event.pos):
                            self.init_game("human")
                        elif bot_rect.collidepoint(event.pos):
                            self.init_game("bot")
            
            elif self.show_game:
                # Then update game state
                if self.current_mode == "bot":
                    try:
                        new_state = self.bot_moves.get_nowait()
                        self.game.board_state = new_state
                        if self.game.board_state.is_winner():
                            self.show_victory = True
                            self.show_game = False
                    except queue.Empty:
                        pass
                
                # Check for human victory
                elif self.current_mode == "human" and self.game.board_state.is_winner():
                    self.show_victory = True
                    self.show_game = False
                
                # Draw the game
                self.handle_game_events()
                self.draw_game()
            
            elif self.show_victory:
                # Handle victory screen events
                menu_rect = self.draw_victory_screen()
                
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        if menu_rect.collidepoint(event.pos):
                            self.show_main_menu = True
                            self.show_victory = False
            
            self.clock.tick(60)

if __name__ == "__main__":
    gui = FreeCellGUI()
    gui.run()