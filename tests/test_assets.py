"""Tests de utils/assets.py — carga de imágenes con fallback a None."""
import pygame

from utils.assets import load_image


def _save_png(path, size=(16, 16), color=(255, 0, 0)):
    surf = pygame.Surface(size)
    surf.fill(color)
    pygame.image.save(surf, str(path))


def test_archivo_inexistente_retorna_none(tmp_path):
    assert load_image(tmp_path / "no_existe.png") is None


def test_archivo_existente_retorna_surface(tmp_path):
    _save_png(tmp_path / "tile.png")
    img = load_image(tmp_path / "tile.png")
    assert isinstance(img, pygame.Surface)
    assert img.get_size() == (16, 16)


def test_size_reescala_la_imagen(tmp_path):
    _save_png(tmp_path / "tile.png", size=(16, 16))
    img = load_image(tmp_path / "tile.png", size=(64, 64))
    assert img.get_size() == (64, 64)


def test_archivo_corrupto_retorna_none(tmp_path):
    (tmp_path / "roto.png").write_bytes(b"esto no es un png")
    assert load_image(tmp_path / "roto.png") is None
