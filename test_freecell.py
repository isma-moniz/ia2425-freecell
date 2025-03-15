from main import FreeCell, Card

def test_supermove_1():
    game = FreeCell()
    
    game.tableau[0] = [Card('K', 'Hearts'), Card('Q', 'Spades'), Card('J', 'Hearts'), Card('10', 'Clubs')]
    game.tableau[1] = [Card('9', 'Clubs'), Card('8', 'Clubs'), Card('7', 'Clubs')]
    game.tableau[2] = [Card('6', 'Diamonds'), Card('5', 'Diamonds')]
    game.tableau[3] = [Card('4', 'Spades'), Card('3', 'Spades')]
    game.tableau[4] = []
    game.tableau[5] = [Card('A', 'Clubs')]
    game.tableau[6] = [Card('K', 'Diamonds')]
    game.tableau[7] = [Card('Q', 'Spades')]

    game.free_cells[0] = Card('2', 'Hearts')
    game.free_cells[1] = Card('A', 'Clubs')
    game.free_cells[2] = None
    game.free_cells[3] = None

    print("\nInitial Game State:")
    game.display()

    print("\nAttempting a valid supermove from tableau 1 to tableau 5:")
    game.move_supermove(0, 4, 2)
    
    print("\nGame State After Valid Supermove:")
    game.display()

def test_supermove_2():
    game = FreeCell()
    
    game.tableau[0] = [Card('K', 'Hearts'), Card('Q', 'Spades'), Card('J', 'Hearts'), Card('10', 'Clubs')]
    game.tableau[1] = [Card('9', 'Clubs'), Card('8', 'Clubs'), Card('7', 'Clubs')]
    game.tableau[2] = [Card('6', 'Diamonds'), Card('5', 'Diamonds')]
    game.tableau[3] = [Card('4', 'Spades'), Card('3', 'Spades')]
    game.tableau[4] = [Card('Q', 'Clubs')]
    game.tableau[5] = [Card('A', 'Clubs')]
    game.tableau[6] = [Card('K', 'Diamonds')]
    game.tableau[7] = [Card('Q', 'Spades')]

    game.free_cells[0] = Card('2', 'Hearts')
    game.free_cells[1] = Card('A', 'Clubs')
    game.free_cells[2] = None
    game.free_cells[3] = None

    print("\nInitial Game State:")
    game.display()

    print("\nAttempting a valid supermove from tableau 1 to tableau 5:")
    game.move_supermove(0, 4, 2)
    
    print("\nGame State After Valid Supermove:")
    game.display()


if __name__ == "__main__":
    print("Choose one of the following tests:\n"
          "1 - supermove 1\n"
          "2 - supermove 2")
    option = input("")
    if option == "1":
        test_supermove_1()
    elif option == "2":
        test_supermove_2()
