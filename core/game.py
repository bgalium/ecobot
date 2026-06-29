"""Bucle principal del juego: eventos, actualización y dibujado."""
import pygame

import settings
from core.interpreter import Interpreter
from core.level import Level
from core.robot import Robot
from ui.intro_screen import IntroScreen
from ui.victory_screen import VictoryScreen

# ── Estados del juego ────────────────────────────────────────────────────────
STATE_INTRO   = "INTRO"     # Mostrando dato ambiental antes del nivel
STATE_IDLE    = "IDLE"      # Esperando que el jugador pulse ESPACIO
STATE_RUNNING = "RUNNING"   # Ejecutando instrucciones
STATE_VICTORY = "VICTORY"   # Robot en GOAL y todos los objetivos cumplidos
STATE_FAILURE = "FAILURE"   # Robot chocó o cayó

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
        self.victory_screen = VictoryScreen()
        self.failure_reason: str | None = None
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
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if event.key == pygame.K_r:
                    self._load_level()

                elif self.state == STATE_INTRO and event.key == pygame.K_SPACE:
                    self.state = STATE_IDLE

                elif self.state == STATE_IDLE and event.key == pygame.K_SPACE:
                    self.interpreter.start()
                    self.state = STATE_RUNNING

                elif self.state == STATE_VICTORY:
                    action = self.victory_screen.handle_event(event)
                    if action in ("next", "retry"):
                        self._load_level()

                elif self.state == STATE_FAILURE and event.key in (
                        pygame.K_SPACE, pygame.K_r):
                    self._load_level()

    def update(self) -> None:
        # Animar siempre: el idle también se anima fuera de RUNNING
        self.robot.update()

        if self.state != STATE_RUNNING:
            return

        # Esperar a que el robot termine de moverse
        if self.robot.moving:
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
            self.victory_screen.draw(
                self.screen, self.level.name, self.level.environmental_fact,
                self.interpreter.steps_used, self.level.max_slots,
            )
        elif self.state == STATE_FAILURE:
            self._draw_overlay("FALLASTE", "Presiona ESPACIO o R para reiniciar",
                               (220, 60, 60))
        elif self.state == STATE_IDLE:
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