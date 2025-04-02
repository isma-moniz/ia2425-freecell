# gui.py
import pygame
import sys
from pygame.locals import *
from freecell_game import FreeCell

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
CARD_WIDTH = 80
CARD_HEIGHT = 120
MARGIN = 20
TABLEAU_SPACING = 110
FREECELL_SPACING = 120
FOUNDATION_SPACING = 120
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 60

# Colors
GREEN = (0, 100, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (100, 100, 255)
GRAY = (200, 200, 200)
DARK_GREEN = (0, 80, 0)

class FreeCellGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('FreeCell Solitaire')
        self.clock = pygame.time.Clock()
        self.large_font = pygame.font.SysFont('Arial', 48)
        self.medium_font = pygame.font.SysFont('Arial', 36)
        self.small_font = pygame.font.SysFont('Arial', 24)
        
        # Game state
        self.game = None
        self.board_state = None
        self.current_mode = None
        self.show_main_menu = True
        self.show_game = False
        
        # Card dragging
        self.dragging = False
        self.dragged_card = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.origin_pile = None
        self.origin_pile_type = None
        
        # Load card images
        self.card_images = self.load_card_images()
        self.card_back = self.create_card_back()

    def load_card_images(self):
        """Create card images with rank and suit"""
        card_images = {}
        for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
            for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
                # Create card surface
                card_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(card_surf, WHITE, (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=5)
                pygame.draw.rect(card_surf, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=5)
                
                # Set text color
                text_color = RED if suit in ['Hearts', 'Diamonds'] else BLACK
                
                # Render rank and suit
                rank_text = self.small_font.render(rank, True, text_color)
                suit_text = self.small_font.render(suit[0], True, text_color)
                
                # Position text
                card_surf.blit(rank_text, (5, 5))
                card_surf.blit(suit_text, (5, 25))
                
                card_images[(rank, suit)] = card_surf
        return card_images

    def create_card_back(self):
        """Create a card back image"""
        card_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, BLUE, (0, 0, CARD_WIDTH, CARD_HEIGHT), border_radius=5)
        pygame.draw.rect(card_surf, BLACK, (0, 0, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=5)
        
        # Add pattern to back
        for i in range(0, CARD_WIDTH, 10):
            pygame.draw.line(card_surf, WHITE, (i, 0), (i, CARD_HEIGHT), 1)
        for i in range(0, CARD_HEIGHT, 10):
            pygame.draw.line(card_surf, WHITE, (0, i), (CARD_WIDTH, i), 1)
            
        return card_surf

    def draw_main_menu(self):
        """Draw the main menu with mode selection"""
        self.screen.fill(DARK_GREEN)
        
        # Title
        title = self.large_font.render("FreeCell Solitaire", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.screen.blit(title, title_rect)
        
        # Human mode button
        human_rect = pygame.Rect(SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 
                               SCREEN_HEIGHT//2 - BUTTON_HEIGHT, 
                               BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, LIGHT_BLUE, human_rect, border_radius=10)
        human_text = self.medium_font.render("Human", True, BLACK)
        human_text_rect = human_text.get_rect(center=human_rect.center)
        self.screen.blit(human_text, human_text_rect)
        
        # Bot mode button
        bot_rect = pygame.Rect(SCREEN_WIDTH//2 - BUTTON_WIDTH//2, 
                             SCREEN_HEIGHT//2 + BUTTON_HEIGHT, 
                             BUTTON_WIDTH, BUTTON_HEIGHT)
        pygame.draw.rect(self.screen, LIGHT_BLUE, bot_rect, border_radius=10)
        bot_text = self.medium_font.render("Bot", True, BLACK)
        bot_text_rect = bot_text.get_rect(center=bot_rect.center)
        self.screen.blit(bot_text, bot_text_rect)
        
        pygame.display.flip()
        return human_rect, bot_rect

    def init_game(self, mode):
        """Initialize the game based on selected mode"""
        self.game = FreeCell()
        self.board_state = self.game.get_board()
        self.current_mode = mode
        self.show_main_menu = False
        self.show_game = True

    def draw_game(self):
        """Draw the actual game interface with cards and clear labels"""
        self.screen.fill(GREEN)
        
        # Draw mode indicator
        mode_text = self.small_font.render(f"Mode: {self.current_mode}", True, WHITE)
        self.screen.blit(mode_text, (20, 20))
        
        # Draw menu button
        menu_rect = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 40)
        pygame.draw.rect(self.screen, BLUE, menu_rect, border_radius=5)
        menu_text = self.small_font.render("Menu", True, WHITE)
        menu_text_rect = menu_text.get_rect(center=menu_rect.center)
        self.screen.blit(menu_text, menu_text_rect)
        
        # ===== DRAW FREE CELLS WITH LABELS =====
        freecell_label = self.small_font.render("Free Cells", True, WHITE)
        self.screen.blit(freecell_label, (MARGIN, MARGIN + 30))
        
        for i in range(4):
            x = MARGIN + FREECELL_SPACING * i
            y = MARGIN + 50
            
            # Draw cell background
            pygame.draw.rect(self.screen, DARK_GREEN, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=5)
            pygame.draw.rect(self.screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=5)
            
            # Draw cell number
            cell_num = self.small_font.render(str(i+1), True, WHITE)
            self.screen.blit(cell_num, (x + 5, y + 5))
            
            # Draw card if present
            if self.board_state.free_cells[i]:
                card = self.board_state.free_cells[i]
                self.screen.blit(self.card_images[(card.rank, card.suit)], (x, y))
        
        # ===== DRAW FOUNDATIONS WITH LABELS =====
        foundation_label = self.small_font.render("Foundations", True, WHITE)
        self.screen.blit(foundation_label, (SCREEN_WIDTH - 200, MARGIN + 30))
        
        for i, suit in enumerate(['Hearts', 'Diamonds', 'Clubs', 'Spades']):
            x = SCREEN_WIDTH - FOUNDATION_SPACING * (4 - i) - CARD_WIDTH - MARGIN
            y = MARGIN + 50
            
            # Draw foundation background
            pygame.draw.rect(self.screen, DARK_GREEN, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=5)
            pygame.draw.rect(self.screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=5)
            
            # Draw suit symbol
            suit_color = RED if suit in ['Hearts', 'Diamonds'] else BLACK
            suit_text = self.small_font.render(suit[0], True, suit_color)
            self.screen.blit(suit_text, (x + CARD_WIDTH//2 - 5, y + CARD_HEIGHT//2 - 10))
            
            # Draw card if present
            if self.board_state.foundations[suit]:
                card = self.board_state.foundations[suit][-1]
                self.screen.blit(self.card_images[(card.rank, card.suit)], (x, y))
        
        # ===== DRAW TABLEAU WITH LABELS =====
        tableau_label = self.small_font.render("Tableau", True, WHITE)
        self.screen.blit(tableau_label, (MARGIN, MARGIN + CARD_HEIGHT + 80))
        
        for i in range(8):
            x = MARGIN + TABLEAU_SPACING * i
            y = MARGIN + CARD_HEIGHT + 100
            
            # Draw pile number
            pile_num = self.small_font.render(str(i+1), True, WHITE)
            self.screen.blit(pile_num, (x + CARD_WIDTH//2 - 5, y - 20))
            
            # Draw cards in pile
            if not self.board_state.tableau[i]:
                # Draw empty pile indicator
                pygame.draw.rect(self.screen, DARK_GREEN, (x, y, CARD_WIDTH, CARD_HEIGHT), border_radius=5)
                pygame.draw.rect(self.screen, BLACK, (x, y, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=5)
            else:
                for j, card in enumerate(self.board_state.tableau[i]):
                    card_y = y + j * 25
                    self.screen.blit(self.card_images[(card.rank, card.suit)], (x, card_y))
        
        # Draw dragged card if any
        if self.dragging and self.dragged_card:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.screen.blit(self.card_images[(self.dragged_card.rank, self.dragged_card.suit)], 
                        (mouse_x - self.drag_offset_x, mouse_y - self.drag_offset_y))
        
        pygame.display.flip()
        return menu_rect

    def get_card_at_pos(self, pos):
        """Returns the top card at given position if it's movable"""
        x, y = pos
        
        # Check free cells (always movable if present)
        for i in range(4):
            cell_x = MARGIN + FREECELL_SPACING * i
            cell_y = MARGIN + 50
            if (cell_x <= x <= cell_x + CARD_WIDTH and 
                cell_y <= y <= cell_y + CARD_HEIGHT and
                self.board_state.free_cells[i]):
                return self.board_state.free_cells[i], 'freecell', i
        
        # Check tableau piles (only top card is movable)
        for i in range(8):
            pile_x = MARGIN + TABLEAU_SPACING * i
            pile_y = MARGIN + CARD_HEIGHT + 100
            
            if (pile_x <= x <= pile_x + CARD_WIDTH and 
                self.board_state.tableau[i]):
                top_card_y = pile_y + (len(self.board_state.tableau[i]) - 1) * 25
                if top_card_y <= y <= top_card_y + CARD_HEIGHT:
                    return self.board_state.tableau[i][-1], 'tableau', i
        
        return None, None, None

    def handle_card_drop(self, pos):
        """Handles card drops with proper validation"""
        if not self.dragged_card or self.origin_pile_type is None:
            return
        
        x, y = pos
        success = False
        
        # First check if we're in the top area (free cells or foundations)
        if MARGIN + 50 <= y <= MARGIN + 50 + CARD_HEIGHT:
            # Check free cells first (left side)
            for i in range(4):
                cell_x = MARGIN + FREECELL_SPACING * i
                if cell_x <= x <= cell_x + CARD_WIDTH:
                    if not self.board_state.free_cells[i] and self.origin_pile_type == 'tableau':
                        success = self.game.move_to_freecell(self.origin_pile)
                        break
            
            # If not dropped on free cell, check foundations (right side)
            if not success:
                for i, suit in enumerate(['Hearts', 'Diamonds', 'Clubs', 'Spades']):
                    foundation_x = SCREEN_WIDTH - FOUNDATION_SPACING * (4 - i) - CARD_WIDTH - MARGIN
                    if foundation_x <= x <= foundation_x + CARD_WIDTH:
                        if self.is_valid_foundation_move(self.dragged_card, suit):
                            if self.origin_pile_type == 'freecell':
                                success = self.game.move_freecell_to_foundation(self.origin_pile)
                            elif self.origin_pile_type == 'tableau':
                                success = self.game.move_to_foundation(self.origin_pile)
                        break
        
        # Check tableau drop (main area)
        elif MARGIN + CARD_HEIGHT + 100 <= y <= SCREEN_HEIGHT:
            for i in range(8):
                pile_x = MARGIN + TABLEAU_SPACING * i
                if pile_x <= x <= pile_x + CARD_WIDTH:
                    if self.origin_pile_type == 'freecell':
                        if self.is_valid_tableau_move(i, self.dragged_card):
                            success = self.game.move_to_tableau(self.origin_pile, i)
                    elif self.origin_pile_type == 'tableau' and i != self.origin_pile:
                        if self.is_valid_tableau_move(i, self.dragged_card):
                            success = self.game.move_tableau_to_tableau(self.origin_pile, i)
                    break
        
        if success:
            self.board_state = self.game.get_board()
        else:
            print(f"Failed to drop card at ({x},{y})")
            print(f"Origin: {self.origin_pile_type} {self.origin_pile}")
            print(f"Dragged card: {self.dragged_card}")

    def is_valid_tableau_move(self, pile_idx, card):
        """Check if card can be placed on tableau pile"""
        if not self.board_state.tableau[pile_idx]:
            return True  # Empty pile accepts any card
        
        top_card = self.board_state.tableau[pile_idx][-1]
        return (card.value == top_card.value - 1 and 
                card.color != top_card.color)

    def is_valid_foundation_move(self, card, suit):
        """Check if card can be placed on foundation"""
        if card.suit != suit:
            return False
        if not self.board_state.foundations[suit]:
            return card.rank == 'A'
        top_card = self.board_state.foundations[suit][-1]
        return card.value == top_card.value + 1

    def handle_game_events(self):
        """Handles all game events including drag-and-drop"""
        menu_rect = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 40)
        
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
                        card_y = MARGIN + CARD_HEIGHT + 100 + (len(self.board_state.tableau[pile_idx])-1)*25
                    else:  # freecell
                        card_x = MARGIN + FREECELL_SPACING * pile_idx
                        card_y = MARGIN + 50
                    
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
                    self.board_state = self.game.get_board()
                elif event.key == K_r:  # Reset
                    self.init_game(self.current_mode)

    def run_bot_move(self):
        """Execute a single bot move"""
        if self.current_mode == "bot" and not self.board_state.is_winner():
            self.game.play_bot()
            self.board_state = self.game.get_board()

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
                self.draw_game()
                self.handle_game_events()
                
                # In bot mode, make moves automatically
                if self.current_mode == "bot":
                    self.run_bot_move()
                    pygame.time.delay(500)  # Pause between bot moves
            
            self.clock.tick(60)

if __name__ == "__main__":
    gui = FreeCellGUI()
    gui.run()