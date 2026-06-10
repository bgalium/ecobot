"""Tests de core/game.py — inicialización, eventos y dibujado (sin ventana real)."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

import settings
from core.game import Game


@pytest.fixture
def game():
    pygame.init()
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    yield Game(screen)
    pygame.quit()


def test_carga_el_nivel_y_crea_el_robot_en_su_inicio(game):
    assert game.level is not None
    assert game.robot.col == game.level.robot_start_col
    assert game.robot.row == game.level.robot_start_row
    assert game.robot.direction == game.level.robot_start_direction
    assert game.running is True


def test_esc_detiene_el_juego(game):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    game.handle_events()
    assert game.running is False


def test_cerrar_la_ventana_detiene_el_juego(game):
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    game.handle_events()
    assert game.running is False


def test_draw_pinta_el_nivel_y_el_robot(game):
    game.draw()
    half = settings.TILE_SIZE // 2
    ox, oy = game.grid_origin
    robot_center = (
        ox + game.robot.col * settings.TILE_SIZE + half,
        oy + game.robot.row * settings.TILE_SIZE + half,
    )
    assert game.screen.get_at(robot_center)[:3] == settings.COLOR_ROBOT


def test_run_termina_si_hay_evento_quit(game):
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    game.run()  # si no consume el QUIT, esto no retorna nunca
    assert game.running is False
