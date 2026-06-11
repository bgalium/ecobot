"""Tests de dibujado: Level.draw y Robot.draw pintan los colores esperados."""
import json

import pygame
import pytest

import settings
from core.level import Level
from core.robot import Robot


@pytest.fixture(autouse=True)
def sin_sprites(tmp_path, monkeypatch):
    """Estos tests verifican el dibujado de RESPALDO (colores): sin PNGs."""
    vacia = tmp_path / "sin_assets"
    vacia.mkdir()
    monkeypatch.setattr(settings, "TILES_SPRITES_DIR", vacia)
    monkeypatch.setattr(settings, "ROBOT_SPRITES_DIR", vacia)


@pytest.fixture
def level(tmp_path):
    data = {
        "name": "Nivel de prueba",
        "environmental_fact": "Dato.",
        "max_slots": 10,
        "available_instructions": ["MOVE"],
        "robot_start": {"col": 0, "row": 0, "direction": "RIGHT"},
        "grid": [
            ["FLOOR", "WALL"],
            ["TRASH", "GOAL"],
        ],
        "objectives": [],
    }
    path = tmp_path / "level_test.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return Level(path)


def cell_center(origin, col, row):
    half = settings.TILE_SIZE // 2
    return (origin[0] + col * settings.TILE_SIZE + half,
            origin[1] + row * settings.TILE_SIZE + half)


def test_level_draw_pinta_cada_tipo_de_celda_con_su_color(level):
    surface = pygame.Surface((400, 400))
    origin = (32, 16)
    level.draw(surface, origin)
    assert surface.get_at(cell_center(origin, 0, 0))[:3] == settings.TILE_COLORS["FLOOR"]
    assert surface.get_at(cell_center(origin, 1, 0))[:3] == settings.TILE_COLORS["WALL"]
    assert surface.get_at(cell_center(origin, 0, 1))[:3] == settings.TILE_COLORS["TRASH"]
    assert surface.get_at(cell_center(origin, 1, 1))[:3] == settings.TILE_COLORS["GOAL"]


def test_robot_draw_pinta_el_robot_en_su_celda():
    surface = pygame.Surface((400, 400))
    origin = (32, 16)
    robot = Robot(col=1, row=1, direction="RIGHT")
    robot.draw(surface, origin)
    assert surface.get_at(cell_center(origin, 1, 1))[:3] == settings.COLOR_ROBOT
    # Fuera de su celda no pinta nada
    assert surface.get_at(cell_center(origin, 0, 0))[:3] == (0, 0, 0)
