"""Tests de la animación de EcoBot: frames por dirección, ciclo y fallback."""
import pygame
import pytest

import settings
from core.robot import Robot
from utils.assets import load_frames

ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)


def _save_png(path, color, size=(64, 64)):
    surf = pygame.Surface(size)
    surf.fill(color)
    pygame.image.save(surf, str(path))


def _crear_anim(base, nombre, colores):
    """Crea una carpeta de animación con un frame sólido por color."""
    carpeta = base / nombre
    carpeta.mkdir(parents=True)
    for i, color in enumerate(colores):
        _save_png(carpeta / f"{i:02d}.png", color)


def centro():
    half = settings.TILE_SIZE // 2
    return (half, half)


# ── load_frames ──────────────────────────────────────────────────────────────

def test_carpeta_inexistente_retorna_lista_vacia(tmp_path):
    assert load_frames(tmp_path / "no_existe") == []

def test_carga_los_frames_ordenados_por_nombre(tmp_path):
    _crear_anim(tmp_path, "anim", [ROJO, VERDE, AZUL])
    frames = load_frames(tmp_path / "anim", size=(64, 64))
    assert len(frames) == 3
    assert [f.get_at((1, 1))[:3] for f in frames] == [ROJO, VERDE, AZUL]
    assert all(f.get_size() == (64, 64) for f in frames)


# ── Robot animado ────────────────────────────────────────────────────────────

@pytest.fixture
def anim_dir(tmp_path, monkeypatch):
    """Animaciones falsas: idle_right rojo/verde, walk_right azul."""
    _crear_anim(tmp_path, "idle_right", [ROJO, VERDE])
    _crear_anim(tmp_path, "walk_right", [AZUL])
    monkeypatch.setattr(settings, "ROBOT_SPRITES_DIR", tmp_path)
    return tmp_path


def test_dibuja_el_frame_de_su_direccion(anim_dir):
    surface = pygame.Surface((128, 128))
    Robot(col=0, row=0, direction="RIGHT").draw(surface, (0, 0))
    assert surface.get_at(centro())[:3] == ROJO  # primer frame de idle_right


def test_update_avanza_el_ciclo_de_frames(anim_dir):
    surface = pygame.Surface((128, 128))
    robot = Robot(col=0, row=0, direction="RIGHT")
    for _ in range(settings.ANIMATION_FRAME_TICKS):
        robot.update()
    robot.draw(surface, (0, 0))
    assert surface.get_at(centro())[:3] == VERDE  # segundo frame

    for _ in range(settings.ANIMATION_FRAME_TICKS):
        robot.update()
    surface.fill((0, 0, 0))
    robot.draw(surface, (0, 0))
    assert surface.get_at(centro())[:3] == ROJO  # el ciclo da la vuelta


def test_al_moverse_usa_la_animacion_walk(anim_dir):
    surface = pygame.Surface((128, 128))
    robot = Robot(col=0, row=0, direction="RIGHT")
    robot.moving = True
    robot.draw(surface, (0, 0))
    assert surface.get_at(centro())[:3] == AZUL


def test_sin_frames_de_esa_direccion_cae_al_sprite_estatico(tmp_path, monkeypatch):
    # Solo existe idle.png estático: dirección UP no tiene carpeta de animación
    _save_png(tmp_path / "idle.png", VERDE)
    monkeypatch.setattr(settings, "ROBOT_SPRITES_DIR", tmp_path)
    surface = pygame.Surface((128, 128))
    Robot(col=0, row=0, direction="UP").draw(surface, (0, 0))
    assert surface.get_at(centro())[:3] == VERDE
