"""Tests de core/robot.py — estado inicial y posición en píxeles."""
import settings
from core.robot import Robot


def test_guarda_posicion_y_direccion_iniciales():
    robot = Robot(col=2, row=3, direction="RIGHT")
    assert robot.col == 2
    assert robot.row == 3
    assert robot.direction == "RIGHT"


def test_posicion_en_pixeles_derivada_de_la_grilla():
    robot = Robot(col=2, row=3, direction="UP")
    assert robot.pixel_x == 2 * settings.TILE_SIZE
    assert robot.pixel_y == 3 * settings.TILE_SIZE
