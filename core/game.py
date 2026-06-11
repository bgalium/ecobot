"""Bucle principal del juego: eventos, actualización y dibujado."""
import pygame

import settings
from core.interpreter import Interpreter
from core.level import Level
from core.robot import Robot

# ── Estados del juego ────────────────────────────────────────────────────────
STATE_IDLE    = "IDLE"      # Esperando que el jugador pulse ESPACIO
STATE_RUNNING = "RUNNING"   # Ejecutando instrucciones
STATE_VICTORY = "VICTORY"   # Robot en GOAL y todos los objetivos cumplidos
STATE_FAILURE = "FAILURE"   # Robot chocó o cayó

# ── Secuencia hardcodeada para level_1.json ───────────────────────────────────
# Mapa 3×3 · robot en (col=0, row=0) mirando RIGHT · GOAL en (col=2, row=2)
# Ruta: →→ ↓↓
HARDCODED_INSTRUCTIONS: list[str] = [
    "MOVE",        # (0,0) → (1,0)
    "MOVE",        # (1,0) → (2,0)
    "TURN_RIGHT",  # RIGHT → DOWN
    "MOVE",        # (2,0) → (2,1)
    "MOVE",        # (2,1) → (2,2)  ← GOAL
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
        self.state = STATE_IDLE

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

                elif event.key == pygame.K_SPACE:
                    if self.state == STATE_IDLE:
                        self.interpreter.start()
                        self.state = STATE_RUNNING
                    elif self.state in (STATE_VICTORY, STATE_FAILURE):
                        self._load_level()

                elif event.key == pygame.K_r:
                    self._load_level()

    def update(self) -> None:
        if self.state != STATE_RUNNING:
            return

        # Animar siempre
        self.robot.update()

        # Esperar a que el robot termine de moverse
        if self.robot.moving:
            return

        result = self.interpreter.step(self.robot, self.level)

        if result in ("WALL", "FELL"):
            self.state = STATE_FAILURE
            return

        if self.interpreter.finished:
            self.state = self._evaluate_victory()

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

        if self.state == STATE_VICTORY:
            self._draw_overlay("VICTORIA", "Presiona ESPACIO o R para reiniciar",
                               (50, 220, 80))
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