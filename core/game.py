"""Bucle principal del juego: eventos, actualización y dibujado."""
import pygame

import settings
from core.interpreter import Interpreter
from core.level import Level
from core.robot import Robot
from ui.fail_screen import FailScreen
from ui.intro_screen import IntroScreen
from ui.victory_screen import VictoryScreen

# ── Estados del juego ────────────────────────────────────────────────────────
STATE_INTRO         = "INTRO"          # Mostrando dato ambiental antes del nivel
STATE_PLANNING      = "PLANNING"       # El jugador arma la ruta (acepta flechas)
STATE_RUNNING       = "RUNNING"        # El robot ejecuta la secuencia paso a paso
STATE_ACTION_PROMPT = "ACTION_PROMPT"  # Pausa la ejecución junto a un objetivo y
                                       # espera la tecla E (QTE, #43)
STATE_VICTORY       = "VICTORY"        # Robot en GOAL y todos los objetivos cumplidos
STATE_FAILURE       = "FAILURE"        # Robot chocó o cayó

# ── Secuencia hardcodeada para level_1.json (Bosque Amazónico 7×5) ───────────
# Robot en (0,4) mirando RIGHT · DEAD_TREE en (2,2) y (4,2) · GOAL en (6,0).
# Solo MOVE/TURN: la secuencia deja al robot MIRANDO cada DEAD_TREE, y plantar
# ocurre en la ventana de acción (QTE, #43) al pulsar E. El panel de ruta (#16)
# la reemplazará por la secuencia que arme el jugador.
HARDCODED_INSTRUCTIONS: list[str] = [
    "MOVE",        # (0,4) → (1,4)
    "MOVE",        # (1,4) → (2,4)
    "TURN_LEFT",   # RIGHT → UP · mira DEAD_TREE (2,2) tras el MOVE siguiente → QTE
    "MOVE",        # (2,4) → (2,3)
    "TURN_RIGHT",  # UP → RIGHT
    "MOVE",        # (2,3) → (3,3)
    "MOVE",        # (3,3) → (4,3)
    "TURN_LEFT",   # RIGHT → UP · mira DEAD_TREE (4,2) → QTE
    "TURN_RIGHT",  # UP → RIGHT
    "MOVE",        # (4,3) → (5,3)
    "MOVE",        # (5,3) → (6,3)
    "TURN_LEFT",   # RIGHT → UP
    "MOVE",        # (6,3) → (6,2)
    "MOVE",        # (6,2) → (6,1)
    "MOVE",        # (6,1) → (6,0) ← GOAL
]


class Game:
    """Orquesta el nivel y el robot dentro del bucle principal."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        pygame.font.init()
        self._font_big   = pygame.font.SysFont(None, 80, bold=True)
        self._font_small = pygame.font.SysFont(None, 36)
        self._load_level()
        self.running = True

    # ------------------------------------------------------------------
    # Configuración / reinicio
    # ------------------------------------------------------------------

    def _load_level(self) -> None:
        """Carga el nivel, recrea el robot y el intérprete."""
        self.level = Level(settings.LEVELS_DIR / "level_1.json")
        self.robot = Robot(
            col=self.level.robot_start_col,
            row=self.level.robot_start_row,
            direction=self.level.robot_start_direction,
        )
        self.grid_origin = (
            (settings.SCREEN_WIDTH  - self.level.cols * settings.TILE_SIZE) // 2,
            (settings.SCREEN_HEIGHT - self.level.rows * settings.TILE_SIZE) // 2,
        )
        self.interpreter = Interpreter(HARDCODED_INSTRUCTIONS)
        self.intro_screen = IntroScreen()
        self.victory_screen = VictoryScreen()
        self.fail_screen = FailScreen()
        self.failure_reason: str | None = None
        # Temporizador del nivel (#42): cuenta regresiva en frames, sólo durante
        # RUNNING. time_limit 0 = sin límite. El HUD (#17) lee time_remaining_seconds.
        self._timer_enabled: bool = self.level.time_limit > 0
        self.time_remaining_frames: int = self.level.time_limit * settings.FPS
        # Frames restantes de la ventana de acción / QTE (#43). Se arma al abrir
        # STATE_ACTION_PROMPT y se consume cada frame; 0 fuera del prompt.
        self.action_frames_remaining: int = 0
        # Pose (col, row, dirección) donde se resolvió la última ventana de
        # acción: evita reabrirla en la misma pose, pero permite un nuevo prompt
        # si el robot gira hacia otro objetivo sin cambiar de celda (ver
        # _resolve_action_prompt).
        self._last_prompt_state: tuple[int, int, str] | None = None
        # La intro precede a PLANNING; tras pulsar ESPACIO el jugador arma la ruta.
        self.state = STATE_INTRO

    @property
    def time_remaining_seconds(self) -> float:
        """Segundos restantes del temporizador (para el HUD, #17)."""
        return max(0, self.time_remaining_frames) / settings.FPS

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(settings.FPS)


    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event)

    def _handle_key(self, event: pygame.event.Event) -> None:
        """Despacha la tecla al manejador del estado actual."""
        if event.key == pygame.K_ESCAPE:
            self.running = False
            return
        if event.key == pygame.K_r:
            self._load_level()
            return

        if self.state == STATE_INTRO:
            self._handle_intro_key(event)
        elif self.state == STATE_PLANNING:
            self._handle_planning_key(event)
        elif self.state == STATE_RUNNING:
            self._handle_running_key(event)
        elif self.state == STATE_ACTION_PROMPT:
            self._handle_action_prompt_key(event)
        elif self.state in (STATE_VICTORY, STATE_FAILURE):
            self._handle_end_key(event)

    def _handle_intro_key(self, event: pygame.event.Event) -> None:
        """En la intro, ESPACIO pasa a la fase de planificación."""
        if event.key == pygame.K_SPACE:
            self.state = STATE_PLANNING

    def _handle_planning_key(self, event: pygame.event.Event) -> None:
        """El jugador arma la ruta; ESPACIO la ejecuta."""
        if event.key == pygame.K_SPACE:
            self.interpreter.start()
            self.state = STATE_RUNNING
        elif event.key in (pygame.K_UP, pygame.K_DOWN,
                           pygame.K_LEFT, pygame.K_RIGHT):
            self._add_route_step(event.key)

    def _handle_running_key(self, event: pygame.event.Event) -> None:
        """Durante la ejecución no se acepta input de ruta (stub).

        El control de velocidad (#45) se enganchará aquí.
        """

    def _handle_action_prompt_key(self, event: pygame.event.Event) -> None:
        """La tecla E resuelve la ventana de acción y reanuda la ejecución."""
        if event.key == pygame.K_e:
            self._resolve_action_prompt()

    def _handle_end_key(self, event: pygame.event.Event) -> None:
        """Delega el evento a la pantalla de victoria o derrota."""
        if self.state == STATE_VICTORY:
            action = self.victory_screen.handle_event(event)
            if action in ("next", "retry"):
                self._load_level()
        elif self.state == STATE_FAILURE:
            action = self.fail_screen.handle_event(event)
            if action == "retry":
                self._load_level()

    # ------------------------------------------------------------------
    # Puntos de extensión para fase 2 (stubs vacíos)
    # ------------------------------------------------------------------

    def _add_route_step(self, key: int) -> None:
        """Registra un paso de ruta desde una tecla de flecha.

        El panel de ruta (#16) implementará aquí la construcción real de la
        secuencia. Por ahora es un stub que sólo recibe la pulsación.
        """

    def _front_cell(self) -> tuple[int, int]:
        """Celda (col, row) que el robot tiene de frente según su dirección."""
        dx, dy = settings.DIRECTIONS[self.robot.direction]
        return self.robot.col + dx, self.robot.row + dy

    def _objective_done(self, obj: dict) -> bool:
        """Indica si un objetivo del nivel ya está cumplido según el grid."""
        col, row = obj["col"], obj["row"]
        obj_type = obj.get("type")
        if obj_type == "PLANT_TREE":
            return self.level.grid[row][col] == "TREE"
        if obj_type == "COLLECT_TRASH":
            return self.level.grid[row][col] == "FLOOR"
        return True

    def _should_trigger_action_prompt(self) -> bool:
        """True si el robot mira una celda con un objetivo activo (aún sin cumplir).

        La acción del robot opera sobre la celda de enfrente (#43), así que el
        QTE se abre exactamente cuando esa celda es un objetivo pendiente.
        """
        front = self._front_cell()
        for obj in self.level.objectives:
            if (obj["col"], obj["row"]) == front and not self._objective_done(obj):
                return True
        return False

    def _resolve_action_prompt(self) -> None:
        """Resuelve el QTE con éxito: ejecuta la acción y reanuda la ejecución.

        Ejecuta robot.action() (planta/recoge/limpia la celda de enfrente) y
        marca la pose actual como resuelta para que update() no reabra el prompt
        mientras el robot no avance ni gire hacia otro objetivo.
        """
        self.robot.action(self.level)
        self._last_prompt_state = (self.robot.col, self.robot.row, self.robot.direction)
        self.state = STATE_RUNNING

    def update(self) -> None:
        # Animar siempre: la animación idle también corre fuera de RUNNING
        self.robot.update()

        # ACTION_PROMPT pausa la ejecución y corre la ventana del QTE (#43): si se
        # agota sin pulsar E, el objetivo se pierde y el robot retoma la ruta.
        if self.state == STATE_ACTION_PROMPT:
            self.action_frames_remaining -= 1
            if self.action_frames_remaining <= 0:
                self._last_prompt_state = (
                    self.robot.col, self.robot.row, self.robot.direction,
                )
                self.state = STATE_RUNNING
            return

        if self.state != STATE_RUNNING:
            return

        # Temporizador (#42): corre sólo en RUNNING, cada frame (incluso mientras
        # el robot se mueve). Si se agota sin completar los objetivos → derrota.
        if self._timer_enabled:
            self.time_remaining_frames -= 1
            if self.time_remaining_frames <= 0 and not self._objectives_complete():
                self.failure_reason = "TIMEOUT"  # clave de REASON_MESSAGES (#54)
                self.state = STATE_FAILURE
                return

        # Esperar a que el robot termine de moverse
        if self.robot.moving:
            return

        # Abrir la ventana de acción si el robot quedó junto a un objetivo (#43).
        # Disparo POSICIONAL: depende solo de la pose del robot, no de si la
        # próxima instrucción del intérprete es ACTION (la detección la implementa
        # #43). No se reabre en la misma pose donde ya se resolvió un prompt, pero
        # sí tras girar (otra dirección = otro objetivo de frente) o avanzar.
        pose = (self.robot.col, self.robot.row, self.robot.direction)
        if pose != self._last_prompt_state and self._should_trigger_action_prompt():
            self.action_frames_remaining = int(self.level.action_window * settings.FPS)
            self.state = STATE_ACTION_PROMPT
            return

        # Evaluar el final recién aquí: con la última animación ya completa,
        # el robot queda quieto y centrado en su celda bajo el overlay.
        if self.interpreter.finished:
            self.state = self._evaluate_victory()
            return

        result = self.interpreter.step(self.robot, self.level)

        if result in ("WALL", "FELL"):
            self.failure_reason = result
            self.state = STATE_FAILURE

    def _evaluate_victory(self) -> str:
        """Devuelve STATE_VICTORY o STATE_FAILURE según los objetivos."""
        current_tile = self.level.grid[self.robot.row][self.robot.col]
        if current_tile != "GOAL":
            self.failure_reason = "OBJECTIVES_INCOMPLETE"
            return STATE_FAILURE
        if not self._objectives_complete():
            self.failure_reason = "OBJECTIVES_INCOMPLETE"
            return STATE_FAILURE
        return STATE_VICTORY

    def _objectives_complete(self) -> bool:
        """Verifica cada objetivo del JSON del nivel.

        Sin objetivos declarados → victoria automática si hay GOAL.
        Tipo "PLANT_TREE"  → verifica grid[row][col] == "TREE".
        Tipo "COLLECT_TRASH" → verifica grid[row][col] == "FLOOR".
        """
        return all(self._objective_done(obj) for obj in self.level.objectives)

    def draw(self) -> None:
        self.screen.fill(settings.COLOR_BG)
        self.level.draw(self.screen, self.grid_origin)
        self.robot.draw(self.screen, self.grid_origin)

        if self.state == STATE_INTRO:
            self.intro_screen.draw(self.screen, self.level.name,
                                   self.level.environmental_fact)
        elif self.state == STATE_VICTORY:
            self.victory_screen.draw(
                self.screen, self.level.name, self.level.environmental_fact,
                self.interpreter.steps_used, self.level.max_slots,
            )
        elif self.state == STATE_FAILURE:
            self.fail_screen.draw(self.screen,
                                  self.failure_reason or "OBJECTIVES_INCOMPLETE")
        elif self.state == STATE_ACTION_PROMPT:
            self._draw_action_prompt()
        elif self.state == STATE_PLANNING:
            self._draw_hint("Presiona ESPACIO para iniciar")

        pygame.display.flip()

    def _draw_overlay(self, main_text: str, sub_text: str,
                      main_color: tuple[int, int, int]) -> None:
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        main_surf = self._font_big.render(main_text, True, main_color)
        self.screen.blit(main_surf, main_surf.get_rect(center=(w // 2, h // 2 - 30)))

        sub_surf = self._font_small.render(sub_text, True, (220, 220, 220))
        self.screen.blit(sub_surf, sub_surf.get_rect(center=(w // 2, h // 2 + 40)))

    def _draw_action_prompt(self) -> None:
        """Indicador del QTE (#43): tecla E + barra de tiempo que se consume."""
        self._draw_hint("Presiona E")
        total = max(1, int(self.level.action_window * settings.FPS))
        frac = max(0.0, min(1.0, self.action_frames_remaining / total))
        w, h = self.screen.get_size()
        bar_w, bar_h = 240, 12
        x, y = (w - bar_w) // 2, h - 60
        pygame.draw.rect(self.screen, (60, 60, 60), (x, y, bar_w, bar_h))
        pygame.draw.rect(self.screen, (90, 200, 90), (x, y, int(bar_w * frac), bar_h))

    def _draw_hint(self, text: str) -> None:
        w, h = self.screen.get_size()
        surf = self._font_small.render(text, True, (180, 180, 180))
        self.screen.blit(surf, surf.get_rect(center=(w // 2, h - 30)))