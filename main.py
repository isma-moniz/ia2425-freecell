# main.py
from freecell_gui import FreeCellGUI
from freecell_game import FreeCell


if __name__ == "__main__":
    mode = input("Select mode (human/bot/gui): ").strip().lower()

    game = FreeCell()

    if mode == "human":
        game.play_human()
    elif mode == "bot":
        game.play_bot()
    
    elif mode == "gui":
        game_gui = FreeCellGUI()
        game_gui.run()
    else:
        print("Invalid mode selected!")