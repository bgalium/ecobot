"""EcoBot: posición y dirección en la grilla, y su dibujado en pantalla."""
import pygame

import settings


class Robot:
    """Estado del robot. En esta fase se dibuja como rectángulo de color."""

    def __init__(self, col: int, row: int, direction: str) -> None:
        self.col = col
        self.row = row
        self.direction = direction
        # Posición visual en píxeles (relativa al origen de la grilla);
        # el issue #8 la interpola para animar el movimiento.
        self.pixel_x: float = col * settings.TILE_SIZE
        self.pixel_y: float = row * settings.TILE_SIZE

    def draw(self, surface: pygame.Surface, origin: tuple[int, int]) -> None:
        """Dibuja al robot en su posición actual con un margen dentro de la celda."""
        origin_x, origin_y = origin
        margin = settings.TILE_SIZE // 8
        rect = pygame.Rect(
            origin_x + int(self.pixel_x) + margin,
            origin_y + int(self.pixel_y) + margin,
            settings.TILE_SIZE - 2 * margin,
            settings.TILE_SIZE - 2 * margin,
        )
        pygame.draw.rect(surface, settings.COLOR_ROBOT, rect)
