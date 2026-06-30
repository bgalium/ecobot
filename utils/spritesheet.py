"""Carga y recorte de spritesheets con soporte para grillas con padding."""

from pathlib import Path

import pygame


class SpriteSheet:
    """Administra una hoja de sprites y extrae submódulos (tiles) por grilla o por rect."""

    def __init__(self, path: str | Path) -> None:
        self.image = pygame.image.load(str(path)).convert_alpha()
        self.width, self.height = self.image.get_size()

    def get_tile(self, col: int, row: int, tile_w: int = 16, tile_h: int = 16,
                 padding: int = 0) -> pygame.Surface:
        """Extrae un tile de la grilla.

        Con padding=0 la celda empieza en (col*tile_w, row*tile_h).
        Con padding=1 (formato estándar con 1px de gap) la celda empieza en
        col*(tile_w+padding), row*(tile_h+padding) y el área extraída mide
        (tile_w, tile_h) — el padding no se incluye en el resultado.
        """
        x = col * (tile_w + padding)
        y = row * (tile_h + padding)
        return self.image.subsurface((x, y, tile_w, tile_h))

    def get_sprite(self, x: int, y: int, w: int, h: int) -> pygame.Surface:
        """Extrae un rectángulo arbitrario de la hoja (útil para decoraciones)."""
        return self.image.subsurface((x, y, w, h))

    def get_sprite_scaled(self, x: int, y: int, w: int, h: int,
                          scale: tuple[int, int]) -> pygame.Surface:
        """Extrae y redimensiona un sprite."""
        sprite = self.get_sprite(x, y, w, h)
        return pygame.transform.scale(sprite, scale)
