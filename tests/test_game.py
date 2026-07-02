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


def test_en_planning_las_flechas_van_al_constructor_de_ruta(game, monkeypatch):
    """En PLANNING cada flecha llega a _add_route_step sin cambiar de estado."""
    from core.game import STATE_PLANNING
    game.state = STATE_PLANNING
    recibidas: list[int] = []
    monkeypatch.setattr(game, "_add_route_step", lambda key: recibidas.append(key))
    flechas = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
    for tecla in flechas:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=tecla))
        game.handle_events()
    assert recibidas == flechas
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
    """En ACTION_PROMPT la tecla E resuelve la ventana y reanuda la ejecución."""
    from core.game import STATE_ACTION_PROMPT, STATE_RUNNING
    game.interpreter.start()
    game.state = STATE_ACTION_PROMPT
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
    game.handle_events()
    assert game.state == STATE_RUNNING
    assert game.interpreter.running is True  # la ejecución sigue activa


def test_update_entra_a_action_prompt_cuando_se_dispara(game, monkeypatch):
    """Con el trigger activo y el robot quieto, update() abre la ventana."""
    from core.game import STATE_ACTION_PROMPT, STATE_RUNNING
    game.interpreter.start()
    game.state = STATE_RUNNING
    game.robot.moving = False
    monkeypatch.setattr(game, "_should_trigger_action_prompt", lambda: True)
    game.update()
    assert game.state == STATE_ACTION_PROMPT
    game.draw()  # smoke: ejercita la rama de dibujo de ACTION_PROMPT


def _abrir_y_resolver_prompt(game):
    """Lleva al juego a ACTION_PROMPT y lo resuelve con E; deja estado RUNNING."""
    from core.game import STATE_ACTION_PROMPT, STATE_RUNNING
    game.interpreter.start()
    game.state = STATE_RUNNING
    game.robot.moving = False
    game.update()
    assert game.state == STATE_ACTION_PROMPT
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
    game.handle_events()
    assert game.state == STATE_RUNNING


def test_resolver_el_prompt_no_lo_reabre_en_la_misma_pose(game, monkeypatch):
    """Tras resolver con E, update() no reabre el prompt si el robot no cambió de pose."""
    from core.game import STATE_RUNNING
    monkeypatch.setattr(game, "_should_trigger_action_prompt", lambda: True)
    _abrir_y_resolver_prompt(game)
    game.robot.moving = False
    game.update()
    assert game.state == STATE_RUNNING


def test_girar_en_la_misma_celda_reabre_el_prompt(game, monkeypatch):
    """Si el robot gira hacia otro objetivo sin moverse, se abre un nuevo prompt."""
    from core.game import STATE_ACTION_PROMPT
    monkeypatch.setattr(game, "_should_trigger_action_prompt", lambda: True)
    _abrir_y_resolver_prompt(game)
    # Otra dirección en la misma celda = otro objetivo de frente → nuevo prompt.
    game.robot.turn_left()
    game.robot.moving = False
    game.update()
    assert game.state == STATE_ACTION_PROMPT


def test_avanzar_de_celda_reabre_el_prompt(game, monkeypatch):
    """Si el robot avanza a otra celda, el guard de pose permite un nuevo prompt."""
    from core.game import STATE_ACTION_PROMPT
    monkeypatch.setattr(game, "_should_trigger_action_prompt", lambda: True)
    _abrir_y_resolver_prompt(game)
    # Cambiar de celda (no solo de dirección) también re-arma el prompt.
    game.robot.col += 1
    game.robot.moving = False
    game.update()
    assert game.state == STATE_ACTION_PROMPT


def test_en_action_prompt_una_tecla_no_e_no_reanuda(game):
    """En ACTION_PROMPT, teclas distintas de E (ESPACIO, flechas) no reanudan."""
    from core.game import STATE_ACTION_PROMPT
    game.interpreter.start()
    for tecla in (pygame.K_SPACE, pygame.K_UP, pygame.K_LEFT):
        game.state = STATE_ACTION_PROMPT
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=tecla))
        game.handle_events()
        assert game.state == STATE_ACTION_PROMPT


def test_la_tecla_e_se_ignora_fuera_de_action_prompt(game):
    """E solo actúa en ACTION_PROMPT; en otros estados no muta la máquina."""
    from core.game import STATE_PLANNING, STATE_RUNNING
    for estado in (STATE_PLANNING, STATE_RUNNING):
        game.state = estado
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
        game.handle_events()
        assert game.state == estado


def test_en_action_prompt_el_interprete_no_avanza(game):
    """Mientras se espera la tecla E, la ejecución queda pausada."""
    from core.game import STATE_ACTION_PROMPT
    game.interpreter.start()
    game.state = STATE_ACTION_PROMPT
    game.action_frames_remaining = 1000  # ventana amplia: el prompt sigue abierto
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


def test_r_reinicia_el_nivel_durante_running(game):
    """R es global: reinicia (vuelve a INTRO) incluso en plena ejecución."""
    from core.game import STATE_INTRO, STATE_RUNNING
    game.state = STATE_RUNNING
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
    game.handle_events()
    assert game.state == STATE_INTRO


def test_espacio_reinicia_desde_victoria_y_derrota(game):
    """Desde VICTORY/FAILURE, ESPACIO recarga el nivel (vuelve a INTRO)."""
    from core.game import STATE_FAILURE, STATE_INTRO, STATE_VICTORY
    for estado_final in (STATE_VICTORY, STATE_FAILURE):
        game.state = estado_final
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        game.handle_events()
        assert game.state == STATE_INTRO


def _ejecutar_hasta_terminar(game, max_frames=2000):
    """Pasa INTRO/PLANNING, simula frames y resuelve cada QTE con E hasta terminar."""
    from core.game import (STATE_ACTION_PROMPT, STATE_INTRO, STATE_RUNNING,
                           STATE_VICTORY, STATE_FAILURE)
    # Salir del estado INTRO si estamos allí
    if game.state == STATE_INTRO:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
        game.handle_events()
    # Iniciar el nivel
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    game.handle_events()
    for _ in range(max_frames):
        # Plantar/limpiar ocurre vía QTE (#43): responder cada ventana con E.
        if game.state == STATE_ACTION_PROMPT:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
            game.handle_events()
        game.update()
        if game.state in (STATE_VICTORY, STATE_FAILURE):
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


# ── Ventana de acción / QTE (#43) ────────────────────────────────────────────

def _mirar_arbol(game):
    """Coloca al robot en (2,3) mirando UP → de frente el DEAD_TREE objetivo (2,2)."""
    game.robot.col, game.robot.row, game.robot.direction = 2, 3, "UP"
    game.robot.moving = False


def test_trigger_true_mirando_objetivo_activo(game):
    """_should_trigger es True cuando el robot mira una celda-objetivo incompleta."""
    _mirar_arbol(game)
    assert game._should_trigger_action_prompt() is True


def test_trigger_false_mirando_celda_sin_objetivo(game):
    """Mirando piso (no hay objetivo de frente) no se dispara el prompt."""
    game.robot.col, game.robot.row, game.robot.direction = 2, 3, "DOWN"  # frente (2,4) FLOOR
    assert game._should_trigger_action_prompt() is False


def test_trigger_false_si_el_objetivo_ya_esta_cumplido(game):
    """Si el DEAD_TREE ya es TREE, el objetivo está cumplido → no se dispara."""
    game.level.set_cell(2, 2, "TREE")
    _mirar_arbol(game)
    assert game._should_trigger_action_prompt() is False


def test_abrir_el_prompt_inicializa_la_ventana(game, monkeypatch):
    """Al entrar a ACTION_PROMPT, la ventana arranca en action_window * FPS frames."""
    from core.game import STATE_RUNNING
    game.interpreter.start()
    game.state = STATE_RUNNING
    game.robot.moving = False
    monkeypatch.setattr(game, "_should_trigger_action_prompt", lambda: True)
    game.update()
    assert game.action_frames_remaining == int(game.level.action_window * settings.FPS)


def test_la_ventana_se_consume_en_action_prompt(game):
    """Cada frame en ACTION_PROMPT decrementa la ventana."""
    from core.game import STATE_ACTION_PROMPT
    game.state = STATE_ACTION_PROMPT
    game.action_frames_remaining = 10
    game.update()
    assert game.action_frames_remaining == 9


def test_ventana_agotada_reanuda_sin_ejecutar_la_accion(game):
    """Si la ventana llega a 0 sin pulsar E → RUNNING y el objetivo NO se ejecuta."""
    from core.game import STATE_ACTION_PROMPT, STATE_RUNNING
    game.interpreter.start()
    _mirar_arbol(game)
    game.state = STATE_ACTION_PROMPT
    game.action_frames_remaining = 1
    game.update()
    assert game.state == STATE_RUNNING
    assert game.level.get_cell(2, 2) == "DEAD_TREE"  # objetivo perdido, no plantado
    # No reabre el prompt en la misma pose (quedó marcada como resuelta).
    game.robot.moving = False
    game.update()
    assert game.state != STATE_ACTION_PROMPT


def test_pulsar_e_ejecuta_la_accion_y_cambia_el_tile(game):
    """En ACTION_PROMPT, E ejecuta robot.action(): DEAD_TREE → TREE y vuelve a RUNNING."""
    from core.game import STATE_ACTION_PROMPT, STATE_RUNNING
    game.interpreter.start()
    _mirar_arbol(game)
    game.state = STATE_ACTION_PROMPT
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
    game.handle_events()
    assert game.state == STATE_RUNNING
    assert game.level.get_cell(2, 2) == "TREE"


def test_objetivo_de_tipo_desconocido_no_se_considera_cumplido(game):
    """Un tipo de objetivo no implementado NO debe darse por cumplido en silencio."""
    assert game._objective_done({"type": "CLEAN_SPILL", "col": 0, "row": 0}) is False


def test_trigger_y_resolucion_para_objetivo_collect_trash(game):
    """El QTE también cubre COLLECT_TRASH: mirar TRASH abre el prompt y E → FLOOR."""
    from core.game import STATE_ACTION_PROMPT, STATE_RUNNING
    game.level.set_cell(2, 3, "TRASH")
    game.level.objectives = [{"type": "COLLECT_TRASH", "col": 2, "row": 3}]
    game.robot.col, game.robot.row, game.robot.direction = 1, 3, "RIGHT"  # frente (2,3)
    game.robot.moving = False
    assert game._should_trigger_action_prompt() is True
    game.interpreter.start()
    game.state = STATE_ACTION_PROMPT
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
    game.handle_events()
    assert game.state == STATE_RUNNING
    assert game.level.get_cell(2, 3) == "FLOOR"


def _correr_nivel(game, pulsar_e, max_iter=6000):
    """Ejecuta el bucle update() hasta VICTORY/FAILURE.

    pulsar_e=True → responde cada ACTION_PROMPT con la tecla E.
    """
    from core.game import STATE_ACTION_PROMPT, STATE_VICTORY, STATE_FAILURE
    game.interpreter.start()
    game.state = "RUNNING"
    for _ in range(max_iter):
        if game.state == STATE_ACTION_PROMPT and pulsar_e:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e))
            game.handle_events()
        game.update()
        if game.state in (STATE_VICTORY, STATE_FAILURE):
            return game.state
    return game.state


def test_nivel_completo_con_qte_es_victoria(game):
    """Plantando ambos árboles vía QTE (E) y llegando al GOAL → VICTORY."""
    from core.game import STATE_VICTORY
    assert _correr_nivel(game, pulsar_e=True) == STATE_VICTORY
    assert game.level.get_cell(2, 2) == "TREE"
    assert game.level.get_cell(4, 2) == "TREE"


def test_nivel_sin_pulsar_e_pierde_los_objetivos(game):
    """Sin pulsar E las ventanas se agotan; sin árboles plantados → FAILURE."""
    from core.game import STATE_FAILURE
    game._timer_enabled = False  # aislar: la derrota debe ser por objetivos, no por tiempo
    assert _correr_nivel(game, pulsar_e=False) == STATE_FAILURE
    assert game.failure_reason == "OBJECTIVES_INCOMPLETE"


# ── Temporizador por nivel (#42) ─────────────────────────────────────────────

def test_timer_se_inicializa_desde_el_time_limit_del_nivel(game):
    """Al cargar, el tiempo restante arranca en level.time_limit segundos."""
    assert game.level.time_limit > 0  # level_1.json define time_limit
    assert game.time_remaining_seconds == game.level.time_limit


def test_timer_decrementa_solo_en_running(game):
    """El contador baja en RUNNING, pero no en PLANNING ni ACTION_PROMPT."""
    from core.game import STATE_ACTION_PROMPT, STATE_PLANNING, STATE_RUNNING
    antes = game.time_remaining_frames
    game.state = STATE_PLANNING
    for _ in range(10):
        game.update()
    assert game.time_remaining_frames == antes  # PLANNING no consume tiempo
    game.state = STATE_ACTION_PROMPT
    game.action_frames_remaining = 1000  # ventana amplia: el prompt sigue abierto
    for _ in range(10):
        game.update()
    assert game.time_remaining_frames == antes  # ACTION_PROMPT tampoco
    game.interpreter.start()
    game.state = STATE_RUNNING
    game.update()
    assert game.time_remaining_frames < antes  # RUNNING sí


def test_timer_agotado_con_objetivos_pendientes_es_derrota(game):
    """Si el tiempo llega a 0 sin objetivos completos → FAILURE con razón TIMEOUT."""
    from core.game import STATE_FAILURE, STATE_RUNNING
    game.interpreter.start()
    game.state = STATE_RUNNING
    game.time_remaining_frames = 1
    game.update()
    assert game.state == STATE_FAILURE
    assert game.failure_reason == "TIMEOUT"  # clave que entiende FailScreen (#54)


def test_timer_se_resetea_al_reiniciar(game):
    """R recarga el nivel y el contador vuelve a su valor inicial."""
    inicial = game.level.time_limit * settings.FPS
    game.time_remaining_frames = 5
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
    game.handle_events()
    assert game.time_remaining_frames == inicial


def test_nivel_sin_time_limit_no_falla_por_tiempo(game):
    """Con el temporizador desactivado (time_limit 0), no hay derrota por tiempo."""
    from core.game import STATE_RUNNING
    game._timer_enabled = False
    game.interpreter.start()
    game.state = STATE_RUNNING
    game.time_remaining_frames = 0
    game.update()
    assert game.state == STATE_RUNNING
