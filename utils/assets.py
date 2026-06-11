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


def load_frames(dir_path: str | Path, size: tuple[int, int] | None = None) -> list[pygame.Surface]:
    """Carga los frames de una animación: los PNG de la carpeta, en orden de nombre.

    Retorna lista vacía si la carpeta no existe o no tiene frames legibles,
    para que quien llama caiga a su dibujo de respaldo.
    """
    dir_path = Path(dir_path)
    if not dir_path.is_dir():
        return []
    frames = []
    for path in sorted(dir_path.glob("*.png")):
        img = load_image(path, size)
        if img is not None:
            frames.append(img)
    return frames
