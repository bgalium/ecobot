"""Tests del issue #11: tiles y robot se dibujan con imagen si existe, color si no."""
import json

import pygame
import pytest

import settings
from core.level import Level
from core.robot import Robot

ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)


def _save_png(path, color, size=(64, 64)):
    surf = pygame.Surface(size)
    surf.fill(color)
    pygame.image.save(surf, str(path))


@pytest.fixture
def level_path(tmp_path):
    data = {
        "name": "n", "environmental_fact": "f", "max_slots": 1,
        "available_instructions": [], "objectives": [],
        "robot_start": {"col": 0, "row": 0, "direction": "RIGHT"},
        "grid": [["FLOOR"]],
    }
    path = tmp_path / "lvl.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def centro(origin=(0, 0), col=0, row=0):
    half = settings.TILE_SIZE // 2
    return (origin[0] + col * settings.TILE_SIZE + half,
            origin[1] + row * settings.TILE_SIZE + half)


# ── Level ────────────────────────────────────────────────────────────────────

def test_level_usa_imagen_de_tile_si_existe(tmp_path, level_path, monkeypatch):
    _save_png(tmp_path / "floor.png", ROJO)
    monkeypatch.setattr(settings, "TILES_SPRITES_DIR", tmp_path)
    surface = pygame.Surface((128, 128))
    Level(level_path).draw(surface, (0, 0))
    assert surface.get_at(centro())[:3] == ROJO


def test_level_cae_al_color_si_no_hay_imagen(tmp_path, level_path, monkeypatch):
    monkeypatch.setattr(settings, "TILES_SPRITES_DIR", tmp_path)  # carpeta vacía
    surface = pygame.Surface((128, 128))
    Level(level_path).draw(surface, (0, 0))
    assert surface.get_at(centro())[:3] == settings.TILE_COLORS["FLOOR"]


# ── Robot ────────────────────────────────────────────────────────────────────

def test_robot_usa_sprite_idle_si_existe(tmp_path, monkeypatch):
    _save_png(tmp_path / "idle.png", VERDE)
    monkeypatch.setattr(settings, "ROBOT_SPRITES_DIR", tmp_path)
    surface = pygame.Surface((128, 128))
    Robot(col=0, row=0, direction="RIGHT").draw(surface, (0, 0))
    assert surface.get_at(centro())[:3] == VERDE


def test_robot_usa_sprite_walk_cuando_se_mueve(tmp_path, monkeypatch):
    _save_png(tmp_path / "idle.png", VERDE)
    _save_png(tmp_path / "walk.png", AZUL)
    monkeypatch.setattr(settings, "ROBOT_SPRITES_DIR", tmp_path)
    surface = pygame.Surface((128, 128))
    robot = Robot(col=0, row=0, direction="RIGHT")
    robot.moving = True
    robot.draw(surface, (0, 0))
    assert surface.get_at(centro())[:3] == AZUL


def test_robot_cae_al_rectangulo_si_no_hay_sprite(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "ROBOT_SPRITES_DIR", tmp_path)  # carpeta vacía
    surface = pygame.Surface((128, 128))
    Robot(col=0, row=0, direction="RIGHT").draw(surface, (0, 0))
    assert surface.get_at(centro())[:3] == settings.COLOR_ROBOT
