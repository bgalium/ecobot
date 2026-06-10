"""Punto de entrada de EcoBot: crea la ventana y lanza el juego."""
import pygame

import settings
from core.game import Game


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    pygame.display.set_caption(settings.WINDOW_TITLE)

    Game(screen).run()

    pygame.quit()


if __name__ == "__main__":
    main()
