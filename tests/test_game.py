"""Tests de core/game.py — inicialización, eventos y dibujado (sin ventana real)."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

import settings
from core.game import Game


@pytest.fixture
def game(tmp_path, monkeypatch):
    # Sin sprites: estos tests verifican la lógica y el dibujado de respaldo
    vacia = tmp_path / "sin_assets"
    vacia.mkdir()
    monkeypatch.setattr(settings, "TILES_SPRITES_DIR", vacia)
    monkeypatch.setattr(settings, "ROBOT_SPRITES_DIR", vacia)
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
    # Avanzar más allá de la pantalla de introducción
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    game.handle_events()
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


# ── Máquina de estados (#50) ─────────────────────────────────────────────────

def test_arranca_en_intro_y_espacio_pasa_a_planning(game):
    """El nivel arranca en INTRO; ESPACIO lleva a PLANNING (antes IDLE)."""
    from core.game import STATE_INTRO, STATE_PLANNING
    assert game.state == STATE_INTRO
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    game.handle_events()
    assert game.state == STATE_PLANNING


def test_desde_planning_espacio_inicia_la_ejecucion(game):
    """En PLANNING, ESPACIO arranca el intérprete y pasa a RUNNING."""
    from core.game import STATE_PLANNING, STATE_RUNNING
    game.state = STATE_PLANNING
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    game.handle_events()
    assert game.state == STATE_RUNNING
    assert game.interpreter.running is True


def test_en_planning_las_flechas_no_rompen_ni_inician(game):
    """PLANNING acepta input de flechas sin cambiar de estado ni fallar."""
    from core.game import STATE_PLANNING
    game.state = STATE_PLANNING
    for tecla in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=tecla))
        game.handle_events()
    assert game.state == STATE_PLANNING
    assert game.running is True


def test_en_running_las_flechas_se_ignoran(game):
    """Durante RUNNING no se acepta input de ruta: las flechas no hacen nada."""
    from core.game import STATE_RUNNING
    game.state = STATE_RUNNING
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
    game.handle_events()
    assert game.state == STATE_RUNNING


def test_action_prompt_se_resuelve_con_la_tecla_e(game):
    """En ACTION_PROMPT la tecla E resuelve la ventana y vuelve a RUNNING."""
    from core.game import STATE_ACTION_PROMPT, STATE_RUNNING
    game.state = STATE_ACTION_PROMPT
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
    game.handle_events()
    assert game.state == STATE_RUNNING


def test_en_action_prompt_el_interprete_no_avanza(game):
    """Mientras se espera la tecla E, la ejecución queda pausada."""
    from core.game import STATE_ACTION_PROMPT
    game.interpreter.start()
    game.state = STATE_ACTION_PROMPT
    indice_antes = game.interpreter._index
    for _ in range(10):
        game.update()
    assert game.interpreter._index == indice_antes
    assert game.state == STATE_ACTION_PROMPT


def test_reiniciar_vuelve_al_flujo_de_planning(game):
    """R recarga el nivel y queda listo para volver a PLANNING tras la intro."""
    from core.game import STATE_INTRO, STATE_PLANNING
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
    game.handle_events()
    assert game.state == STATE_INTRO
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    game.handle_events()
    assert game.state == STATE_PLANNING


def _ejecutar_hasta_terminar(game, max_frames=2000):
    """Presiona ESPACIO para pasar INTRO e IDLE, y simula frames hasta terminar."""
    from core.game import STATE_INTRO, STATE_RUNNING
    # Salir del estado INTRO si estamos allí
    if game.state == STATE_INTRO:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        game.handle_events()
    # Iniciar el nivel
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    game.handle_events()
    for _ in range(max_frames):
        game.update()
        if game.state != STATE_RUNNING:
            break
    return game.state


def test_la_secuencia_hardcodeada_gana_el_nivel_real(game):
    """Integración con el level_1.json real: debe plantar todo y llegar a la meta."""
    from core.game import STATE_VICTORY
    estado = _ejecutar_hasta_terminar(game)
    assert estado == STATE_VICTORY
    assert game.level.get_cell(game.robot.col, game.robot.row) == "GOAL"


def test_los_objetivos_se_cumplen_de_verdad(game):
    """Tras ganar, las celdas de los objetivos deben haber cambiado a TREE/FLOOR."""
    _ejecutar_hasta_terminar(game)
    for obj in game.level.objectives:
        celda = game.level.get_cell(obj["col"], obj["row"])
        if obj["type"] == "PLANT_TREE":
            assert celda == "TREE"
        elif obj["type"] == "COLLECT_TRASH":
            assert celda == "FLOOR"


def test_no_se_gana_ignorando_los_objetivos(game):
    """Ir directo a la meta sin plantar debe ser derrota, no victoria."""
    from core.game import STATE_FAILURE
    from core.interpreter import Interpreter
    game.interpreter = Interpreter(["MOVE", "MOVE", "MOVE", "MOVE"])  # directo al GOAL
    estado = _ejecutar_hasta_terminar(game)
    assert estado == STATE_FAILURE


def test_al_ganar_el_robot_termino_su_animacion(game):
    """La victoria se evalúa con el robot quieto y centrado en su celda."""
    _ejecutar_hasta_terminar(game)
    assert game.robot.moving is False
    assert game.robot.pixel_x == game.robot.target_x
    assert game.robot.pixel_y == game.robot.target_y
