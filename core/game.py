"""Bucle principal del juego: eventos, actualización y dibujado."""
import pygame

import settings
from core.interpreter import Interpreter
from core.level import Level
from core.robot import Robot
from ui.intro_screen import IntroScreen

# ── Estados del juego ────────────────────────────────────────────────────────
STATE_INTRO         = "INTRO"          # Mostrando dato ambiental antes del nivel
STATE_PLANNING      = "PLANNING"       # El jugador arma la ruta (acepta flechas)
STATE_RUNNING       = "RUNNING"        # El robot ejecuta la secuencia. Timer activo.
STATE_ACTION_PROMPT = "ACTION_PROMPT"  # Sub-estado de RUNNING: pausa junto a un
                                       # objetivo, espera la tecla E
STATE_VICTORY       = "VICTORY"        # Robot en GOAL y todos los objetivos cumplidos
STATE_FAILURE       = "FAILURE"        # Robot chocó o cayó

# ── Secuencia hardcodeada para level_1.json (Bosque Amazónico 5×4) ───────────
# Robot en (0,3) mirando RIGHT · DEAD_TREE en (2,2) y (3,2) · GOAL en (4,3).
# Solución en 10 instrucciones (= max_slots): avanza por la fila de abajo y
# planta cada árbol girando hacia arriba. El panel drag & drop (#16) la
# reemplazará por la secuencia que arme el jugador.
HARDCODED_INSTRUCTIONS: list[str] = [
    "MOVE",        # (0,3) → (1,3)
    "MOVE",        # (1,3) → (2,3)
    "TURN_LEFT",   # RIGHT → UP (mira al DEAD_TREE de (2,2))
    "ACTION",      # planta → TREE
    "TURN_RIGHT",  # UP → RIGHT
    "MOVE",        # (2,3) → (3,3)
    "TURN_LEFT",   # RIGHT → UP (mira al DEAD_TREE de (3,2))
    "ACTION",      # planta → TREE
    "TURN_RIGHT",  # UP → RIGHT
    "MOVE",        # (3,3) → (4,3)  ← GOAL
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
        # Pose (col, row, dirección) donde se resolvió la última ventana de
        # acción: evita reabrirla en la misma pose, pero permite un nuevo prompt
        # si el robot gira hacia otro objetivo sin cambiar de celda (ver
        # _resolve_action_prompt).
        self._last_prompt_state: tuple[int, int, str] | None = None
        # La intro precede a PLANNING; tras pulsar ESPACIO el jugador arma la ruta.
        self.state = STATE_INTRO

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
        # Teclas globales, válidas en cualquier estado.
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
        pass

    def _handle_action_prompt_key(self, event: pygame.event.Event) -> None:
        """La tecla E resuelve la ventana de acción y reanuda la ejecución."""
        if event.key == pygame.K_e:
            self._resolve_action_prompt()

    def _handle_end_key(self, event: pygame.event.Event) -> None:
        """En victoria/derrota, ESPACIO reinicia el nivel."""
        if event.key == pygame.K_SPACE:
            self._load_level()

    # ------------------------------------------------------------------
    # Puntos de extensión para fase 2 (stubs vacíos)
    # ------------------------------------------------------------------

    def _add_route_step(self, key: int) -> None:
        """Registra un paso de ruta desde una tecla de flecha.

        El panel de ruta (#16) implementará aquí la construcción real de la
        secuencia. Por ahora es un stub que sólo recibe la pulsación.
        """

    def _should_trigger_action_prompt(self) -> bool:
        """Indica si el robot quedó junto a un objetivo y debe abrirse el QTE.

        La detección real (robot adyacente a un objetivo activo) la implementa
        la ventana de acción (#43). De momento nunca se dispara.
        """
        return False

    def _resolve_action_prompt(self) -> None:
        """Cierra la ventana de acción y reanuda la ejecución.

        El resultado del QTE (acierto/fallo) lo definirá #43; aquí sólo se
        reanuda RUNNING y se marca la pose actual como ya resuelta, para que
        update() no reabra el prompt mientras el robot no avance ni gire.
        """
        self._last_prompt_state = (self.robot.col, self.robot.row, self.robot.direction)
        self.state = STATE_RUNNING

    def update(self) -> None:
        # Animar siempre: el idle también se anima fuera de RUNNING
        self.robot.update()

        # ACTION_PROMPT pausa la ejecución hasta que el jugador pulse E.
        if self.state == STATE_ACTION_PROMPT:
            return

        if self.state != STATE_RUNNING:
            return

        # Esperar a que el robot termine de moverse
        if self.robot.moving:
            return

        # Abrir la ventana de acción si el robot quedó junto a un objetivo (#43).
        # No se reabre en la misma pose donde ya se resolvió un prompt, pero sí
        # tras girar (otra dirección = otro objetivo de frente) o avanzar.
        pose = (self.robot.col, self.robot.row, self.robot.direction)
        if pose != self._last_prompt_state and self._should_trigger_action_prompt():
            self.state = STATE_ACTION_PROMPT
            return

        # Evaluar el final recién aquí: con la última animación ya completa,
        # el robot queda quieto y centrado en su celda bajo el overlay.
        if self.interpreter.finished:
            self.state = self._evaluate_victory()
            return

        result = self.interpreter.step(self.robot, self.level)

        if result in ("WALL", "FELL"):
            self.state = STATE_FAILURE

    def _evaluate_victory(self) -> str:
        """Devuelve STATE_VICTORY o STATE_FAILURE según los objetivos."""
        current_tile = self.level.grid[self.robot.row][self.robot.col]
        if current_tile != "GOAL":
            return STATE_FAILURE
        if not self._objectives_complete():
            return STATE_FAILURE
        return STATE_VICTORY

    def _objectives_complete(self) -> bool:
        """Verifica cada objetivo del JSON del nivel.

        Sin objetivos declarados → victoria automática si hay GOAL.
        Tipo "PLANT_TREE"  → verifica grid[row][col] == "TREE".
        Tipo "COLLECT_TRASH" → verifica grid[row][col] == "FLOOR".
        """
        if not self.level.objectives:
            return True

        for obj in self.level.objectives:
            obj_type = obj.get("type")
            col, row = obj["col"], obj["row"]
            if obj_type == "PLANT_TREE" and self.level.grid[row][col] != "TREE":
                return False
            if obj_type == "COLLECT_TRASH" and self.level.grid[row][col] != "FLOOR":
                return False

        return True

    def draw(self) -> None:
        self.screen.fill(settings.COLOR_BG)
        self.level.draw(self.screen, self.grid_origin)
        self.robot.draw(self.screen, self.grid_origin)

        if self.state == STATE_INTRO:
            self.intro_screen.draw(self.screen, self.level.name,
                                   self.level.environmental_fact)
        elif self.state == STATE_VICTORY:
            self._draw_overlay("VICTORIA", "Presiona ESPACIO o R para reiniciar",
                               (50, 220, 80))
        elif self.state == STATE_FAILURE:
            self._draw_overlay("FALLASTE", "Presiona ESPACIO o R para reiniciar",
                               (220, 60, 60))
        elif self.state == STATE_ACTION_PROMPT:
            self._draw_hint("Presiona E")
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

    def _draw_hint(self, text: str) -> None:
        w, h = self.screen.get_size()
        surf = self._font_small.render(text, True, (180, 180, 180))
        self.screen.blit(surf, surf.get_rect(center=(w // 2, h - 30)))