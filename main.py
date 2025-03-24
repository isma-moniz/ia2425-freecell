from freecell_game import FreeCell


if __name__ == "__main__":
    mode = input("Select mode (human/bot): ").strip().lower()

    game = FreeCell()

    if mode == "human":
        game.play_human()
    elif mode == "bot":
        game.play_bot()
    else:
        print("Invalid mode selected!")
