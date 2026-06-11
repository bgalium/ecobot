"""Carga de imágenes con fallback: si el archivo no existe o falla, retorna None."""
from pathlib import Path

import pygame


def load_image(path: str | Path, size: tuple[int, int] | None = None) -> pygame.Surface | None:
    """Carga una imagen desde disco, reescalada a `size` si se indica.

    Retorna None si el archivo no existe o no se puede leer, para que quien
    llama use su dibujo de respaldo (regla del issue #11: el juego nunca debe
    crashear por un asset faltante).
    """
    path = Path(path)
    if not path.is_file():
        return None
    try:
        img = pygame.image.load(str(path))
    except pygame.error:
        return None
    if size is not None and img.get_size() != size:
        img = pygame.transform.scale(img, size)
    return img
