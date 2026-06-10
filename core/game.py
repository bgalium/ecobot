"""Bucle principal del juego: eventos, actualización y dibujado."""
import pygame

import settings
from core.level import Level
from core.robot import Robot


class Game:
    """Orquesta el nivel y el robot dentro del bucle principal."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.level = Level(settings.LEVELS_DIR / "level_1.json")
        self.robot = Robot(
            col=self.level.robot_start_col,
            row=self.level.robot_start_row,
            direction=self.level.robot_start_direction,
        )
        # Origen de la grilla en píxeles, centrada en la pantalla
        self.grid_origin = (
            (settings.SCREEN_WIDTH - self.level.cols * settings.TILE_SIZE) // 2,
            (settings.SCREEN_HEIGHT - self.level.rows * settings.TILE_SIZE) // 2,
        )
        self.running = True

    def run(self) -> None:
        """Bucle principal: corre hasta que el jugador cierra el juego."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(settings.FPS)

    def handle_events(self) -> None:
        """Cierra el juego con ESC o con la X de la ventana."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def update(self) -> None:
        """Sin lógica por ahora: el movimiento llega en el issue #8."""

    def draw(self) -> None:
        """Limpia la pantalla, dibuja el nivel y el robot, y actualiza el display."""
        self.screen.fill(settings.COLOR_BG)
        self.level.draw(self.screen, self.grid_origin)
        self.robot.draw(self.screen, self.grid_origin)
        pygame.display.flip()
