"""Bucle principal del juego: eventos, actualización y dibujado."""
import pygame

import settings
from core.interpreter import Interpreter
from core.level import Level
from core.robot import Robot

# ── Estados del juego ────────────────────────────────────────────────────────
STATE_IDLE = "IDLE"          # Esperando que el jugador pulse ESPACIO
STATE_RUNNING = "RUNNING"    # Ejecutando instrucciones
STATE_VICTORY = "VICTORY"    # Todos los objetivos cumplidos y robot en GOAL
STATE_FAILURE = "FAILURE"    # El robot chocó contra una pared o cayó al vacío

# ── Secuencia hardcodeada para level_1.json ──────────────────────────────────
# Mapa 3×3, robot empieza en (col=0, row=0) mirando RIGHT, meta en (col=2, row=2)
# Ruta: →→ ↓↓  (MOVE×2 hacia la derecha, MOVE×2 hacia abajo)
HARDCODED_INSTRUCTIONS: list[str] = [
    "MOVE",        # (0,0)→(1,0)
    "MOVE",        # (1,0)→(2,0)
    "TURN_RIGHT",  # RIGHT→DOWN
    "MOVE",        # (2,0)→(2,1)
    "MOVE",        # (2,1)→(2,2)  ← celda GOAL
]


class Game:
    """Orquesta el nivel y el robot dentro del bucle principal."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        self._load_level()
        self.state: str = STATE_IDLE

        # Fuente para los overlays de victoria/derrota
        pygame.font.init()
        self._font_big = pygame.font.SysFont(None, 80, bold=True)
        self._font_small = pygame.font.SysFont(None, 36)

        self.running = True

    def _load_level(self) -> None:
        """Carga el nivel y recrea el robot y el intérprete."""
        self.level = Level(settings.LEVELS_DIR / "level_1.json")
        self.robot = Robot(
            col=self.level.robot_start_col,
            row=self.level.robot_start_row,
            direction=self.level.robot_start_direction,
        )
        self.grid_origin = (
            (settings.SCREEN_WIDTH - self.level.cols * settings.TILE_SIZE) // 2,
            (settings.SCREEN_HEIGHT - self.level.rows * settings.TILE_SIZE) // 2,
        )
        self.interpreter = Interpreter(HARDCODED_INSTRUCTIONS)


    def run(self) -> None:
        """Corre hasta que el jugador cierra el juego."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(settings.FPS)

    def handle_events(self) -> None:
        """Gestiona entrada del teclado."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_SPACE:
                    if self.state == STATE_IDLE:
                        # Iniciar ejecución
                        self.interpreter.start()
                        self.state = STATE_RUNNING

                    elif self.state in (STATE_VICTORY, STATE_FAILURE):
                        # Reiniciar el nivel con R o SPACE
                        self._load_level()
                        self.state = STATE_IDLE

                elif event.key == pygame.K_r:
                    # Reinicio en cualquier estado
                    self._load_level()
                    self.state = STATE_IDLE

    def update(self) -> None:
        """Avanza la animación del robot y ejecuta la siguiente instrucción."""
        if self.state != STATE_RUNNING:
            return

        # Siempre actualizamos la animación visual
        self.robot.update()

        # Sólo avanzamos cuando el robot terminó de moverse
        if not self.robot.is_idle():
            return

        result = self.interpreter.step(self.robot, self.level)

        if result in ("WALL", "FELL"):
            self.state = STATE_FAILURE
            return

        # ¿Terminaron todas las instrucciones?
        if self.interpreter.finished:
            self.state = self._evaluate_victory()

    def _evaluate_victoria(self) -> str:
        """Alias en español mantenido por compatibilidad interna."""
        return self._evaluate_victory()

    def _evaluate_victory(self) -> str:
        """Devuelve STATE_VICTORY o STATE_FAILURE según los objetivos."""
        # 1. El robot debe estar parado en una celda GOAL
        current_tile = self.level.grid[self.robot.row][self.robot.col]
        if current_tile != "GOAL":
            return STATE_FAILURE

        # 2. Todos los objetivos del nivel deben estar completados
        if not self._objectives_complete():
            return STATE_FAILURE

        return STATE_VICTORY

    def _objectives_complete(self) -> bool:
        """Verifica cada objetivo declarado en el JSON del nivel.

        Soporta:
          • Sin objetivos declarados → victoria automática si hay GOAL.
          • Tipo "PLANT_TREE" con posición → verifica que grid[row][col] == "TREE".
        """
        if not self.level.objectives:
            return True  # level_1.json no tiene objetivos todavía

        for obj in self.level.objectives:
            obj_type = obj.get("type")
            if obj_type == "PLANT_TREE":
                col = obj["col"]
                row = obj["row"]
                if self.level.grid[row][col] != "TREE":
                    return False
            # Otros tipos de objetivo se añadirán en futuras fases

        return True

    # ------------------------------------------------------------------
    # Dibujado
    # ------------------------------------------------------------------

    def draw(self) -> None:
        """Limpia la pantalla, dibuja el nivel y el robot, y los overlays."""
        self.screen.fill(settings.COLOR_BG)
        self.level.draw(self.screen, self.grid_origin)
        self.robot.draw(self.screen, self.grid_origin)

        if self.state == STATE_VICTORY:
            self._draw_overlay(
                main_text="VICTORIA",
                sub_text="Presiona ESPACIO o R para reiniciar",
                main_color=(50, 220, 80),
            )
        elif self.state == STATE_FAILURE:
            self._draw_overlay(
                main_text="FALLASTE",
                sub_text="Presiona ESPACIO o R para reiniciar",
                main_color=(220, 60, 60),
            )
        elif self.state == STATE_IDLE:
            self._draw_hint("Presiona ESPACIO para iniciar")

        pygame.display.flip()

    def _draw_overlay(
        self,
        main_text: str,
        sub_text: str,
        main_color: tuple[int, int, int],
    ) -> None:
        """Dibuja un panel semitransparente con el mensaje principal y el subtítulo."""
        w, h = self.screen.get_size()
        # Fondo semitransparente
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        # Texto principal
        main_surf = self._font_big.render(main_text, True, main_color)
        main_rect = main_surf.get_rect(center=(w // 2, h // 2 - 30))
        self.screen.blit(main_surf, main_rect)
        # Subtítulo
        sub_surf = self._font_small.render(sub_text, True, (220, 220, 220))
        sub_rect = sub_surf.get_rect(center=(w // 2, h // 2 + 40))
        self.screen.blit(sub_surf, sub_rect)

    def _draw_hint(self, text: str) -> None:
        """Dibuja un pequeño texto de ayuda en la parte inferior de la pantalla."""
        w, h = self.screen.get_size()
        surf = self._font_small.render(text, True, (180, 180, 180))
        rect = surf.get_rect(center=(w // 2, h - 30))
        self.screen.blit(surf, rect)