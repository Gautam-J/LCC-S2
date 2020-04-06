import pygame
from game import CoronaBreakout

if __name__ == '__main__':
    # initializing an instance of the game.
    game = CoronaBreakout()
    game.show_start_screen()

    while game.running:
        game.new()
        game.show_gameover_screen()

    pygame.quit()
