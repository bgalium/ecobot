"""Tests de core/level.py — carga del JSON de nivel y transitabilidad."""
import json

import pytest

from core.level import Level


@pytest.fixture
def level_file(tmp_path):
    """JSON de nivel con la estructura definida en el issue #10."""
    data = {
        "name": "Nivel de prueba",
        "environmental_fact": "Dato ambiental de prueba.",
        "max_slots": 10,
        "available_instructions": ["MOVE", "TURN_LEFT", "TURN_RIGHT", "ACTION"],
        "robot_start": {"col": 0, "row": 2, "direction": "RIGHT"},
        "grid": [
            ["FLOOR", "TRASH", "FLOOR"],
            ["FLOOR", "WALL", "DEAD_TREE"],
            ["FLOOR", "FLOOR", "GOAL"],
        ],
        "objectives": [
            {"type": "COLLECT_TRASH", "col": 1, "row": 0},
            {"type": "PLANT_TREE", "col": 2, "row": 1},
        ],
    }
    path = tmp_path / "level_test.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_load_lee_campos_basicos(level_file):
    level = Level(level_file)
    assert level.name == "Nivel de prueba"
    assert level.environmental_fact == "Dato ambiental de prueba."
    assert level.max_slots == 10
    assert level.available_instructions == ["MOVE", "TURN_LEFT", "TURN_RIGHT", "ACTION"]


def test_load_lee_posicion_inicial_del_robot(level_file):
    level = Level(level_file)
    assert level.robot_start_col == 0
    assert level.robot_start_row == 2
    assert level.robot_start_direction == "RIGHT"


def test_load_calcula_dimensiones_de_la_grilla(level_file):
    level = Level(level_file)
    assert level.cols == 3
    assert level.rows == 2 + 1  # 3 filas


def test_load_guarda_los_objetivos(level_file):
    level = Level(level_file)
    assert len(level.objectives) == 2
    assert level.objectives[0]["type"] == "COLLECT_TRASH"


def test_floor_y_goal_son_transitables(level_file):
    level = Level(level_file)
    assert level.is_walkable(0, 0) is True   # FLOOR
    assert level.is_walkable(2, 2) is True   # GOAL


def test_wall_dead_tree_y_trash_no_son_transitables(level_file):
    level = Level(level_file)
    assert level.is_walkable(1, 1) is False  # WALL
    assert level.is_walkable(2, 1) is False  # DEAD_TREE
    assert level.is_walkable(1, 0) is False  # TRASH


def test_fuera_de_la_grilla_no_es_transitable(level_file):
    level = Level(level_file)
    assert level.is_walkable(-1, 0) is False
    assert level.is_walkable(0, -1) is False
    assert level.is_walkable(3, 0) is False
    assert level.is_walkable(0, 3) is False
