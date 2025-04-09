# IA2425-FreeCell

## How to Play FreeCell

FreeCell is a solitaire card game played with a standard 52-card deck.  
The objective is to build four foundation piles (one for each suit) in ascending order, starting with the Ace and ending with the King.

---

## Game Layout

### Tableau
The main playing area consists of several tableau piles where cards are arranged in columns.  
All cards in the tableau are face-up, and you can rearrange them following specific rules.

### Free Cells
There are four free cells available. These cells serve as temporary storage for individual cards, helping you free up cards in the tableau for further moves.

### Foundations
There are four foundation piles (one per suit). The goal is to move all cards here in sequential order, from Ace up to King.

---

## Basic Rules

### Moving Cards

#### Within the Tableau:
- You can move a single card or a properly ordered sequence of cards between tableau piles.
- Moves are allowed only if the sequence follows **descending order** and **alternating colors**.  
  (e.g., a red 8 can only be placed on a black 9).

#### To Free Cells:
- Move one card at a time from a tableau pile to a free cell if the cell is empty.

#### To Foundations:
- Move a card to its corresponding foundation if it is the next card in sequence for that suit.  
  (e.g., an Ace can be moved to an empty foundation, and a 2 can be moved only if the Ace of the same suit is already in place).

---

### Sequence Building
- In the tableau, cards must be arranged in descending order (King to Ace) with alternating colors.
- This rule applies to moves that involve moving multiple cards at once.

---

### Empty Free Cells and Cascades
- Utilize empty free cells and tableau columns to temporarily hold cards while rearranging.
- This strategy is key for uncovering hidden cards and progressing the game.

---

## Winning the Game
The game is won when all cards have been successfully moved to the foundations in the correct order for each suit.

## Losing the Game
The game is lost when there are no possible moves to be made.

---

## How to Play

### Launching the Application:
1. Move to the folder holding the application.
2. Launch it by typing:
   ```bash
   python3 main.py
