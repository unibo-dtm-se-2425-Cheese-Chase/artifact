import CheeseChase

if __name__ == "__main__":
    game = CheeseChase.GameController()
    game.startGame()
    while True:
        game.update()



