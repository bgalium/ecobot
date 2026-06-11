"""EcoBot: posición y dirección en la grilla, y su dibujado en pantalla."""
import pygame

import settings


class Robot:
    """Estado del robot con animación de desplazamiento suave entre celdas."""

    # Velocidad de animación en píxeles por frame
    ANIM_SPEED: float = settings.TILE_SIZE / (settings.FPS * 0.15)  # ~15 % de un segundo

    def __init__(self, col: int, row: int, direction: str) -> None:
        self.col = col
        self.row = row
        self.direction = direction
        # Posición visual en píxeles (relativa al origen de la grilla)
        self.pixel_x: float = col * settings.TILE_SIZE
        self.pixel_y: float = row * settings.TILE_SIZE
        # Posición destino en píxeles (iguales a la actual cuando está quieto)
        self._target_x: float = self.pixel_x
        self._target_y: float = self.pixel_y

    # API pública para el intérprete

    def move_to(self, col: int, row: int) -> None:
        """Actualiza la celda lógica y define el destino de la animación."""
        self.col = col
        self.row = row
        self._target_x = col * settings.TILE_SIZE
        self._target_y = row * settings.TILE_SIZE

    def is_idle(self) -> bool:
        """True cuando el robot no está en medio de una animación."""
        return (
            abs(self.pixel_x - self._target_x) < 0.5
            and abs(self.pixel_y - self._target_y) < 0.5
        )

    # Bucle de juego
    def update(self) -> None:
        """Interpola la posición visual hacia el destino (animación suave)."""
        if not self.is_idle():
            dx = self._target_x - self.pixel_x
            dy = self._target_y - self.pixel_y
            dist = (dx**2 + dy**2) ** 0.5

            if dist <= self.ANIM_SPEED:
                # Llegar exactamente al destino
                self.pixel_x = self._target_x
                self.pixel_y = self._target_y
            else:
                self.pixel_x += self.ANIM_SPEED * dx / dist
                self.pixel_y += self.ANIM_SPEED * dy / dist

    def draw(self, surface: pygame.Surface, origin: tuple[int, int]) -> None:
        """Dibuja al robot en su posición visual con un margen dentro de la celda."""
        origin_x, origin_y = origin
        margin = settings.TILE_SIZE // 8
        rect = pygame.Rect(
            origin_x + int(self.pixel_x) + margin,
            origin_y + int(self.pixel_y) + margin,
            settings.TILE_SIZE - 2 * margin,
            settings.TILE_SIZE - 2 * margin,
        )
        pygame.draw.rect(surface, settings.COLOR_ROBOT, rect)