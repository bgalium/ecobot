"""EcoBot: posición y dirección en la grilla, y su dibujado en pantalla."""
import pygame

import settings


class Robot:
    """Estado del robot: posición en grilla, dirección y animación de movimiento."""

    def __init__(self, col: int, row: int, direction: str) -> None:
        self.col = col
        self.row = row
        self.direction = direction
        self.pixel_x: float = col * settings.TILE_SIZE
        self.pixel_y: float = row * settings.TILE_SIZE
        self.target_x: float = self.pixel_x
        self.target_y: float = self.pixel_y
        self.moving: bool = False

    # Movimiento

    def move_forward(self, level) -> str:
        """Avanza una celda en la dirección actual usando traslación.

        Aplica T(dx, dy) sobre el vector posición [col, row, 1]:
        resultado = [col+dx, row+dy, 1] 
        Retorna "OK", "WALL" o "FELL"
        """
        dx, dy = settings.DIRECTIONS[self.direction]
        nueva_col = self.col + dx
        nueva_row = self.row + dy
        if not (0 <= nueva_col < level.cols and 0 <= nueva_row < level.rows):
            return "FELL"
        if not level.is_walkable(nueva_col, nueva_row):
            return "WALL"
        self.col = nueva_col
        self.row = nueva_row
        self.target_x = self.col * settings.TILE_SIZE
        self.target_y = self.row * settings.TILE_SIZE
        self.moving = True
        return "OK"

    def turn_left(self) -> str:
        """Gira 90° a la izquierda sin moverse"""
        order = ["RIGHT", "UP", "LEFT", "DOWN"]
        self.direction = order[(order.index(self.direction) + 1) % 4]
        return "OK"

    def turn_right(self) -> str:
        """Gira 90° a la derecha sin moverse """
        order = ["RIGHT", "DOWN", "LEFT", "UP"]
        self.direction = order[(order.index(self.direction) + 1) % 4]
        return "OK"

    def action(self, level) -> str:
        """Actúa sobre la celda frente al robot.

        Retorna "PLANTED", "COLLECTED" o "NOTHING".
        """
        dx, dy = settings.DIRECTIONS[self.direction]
        front_col = self.col + dx
        front_row = self.row + dy
        cell = level.get_cell(front_col, front_row)
        if cell == "DEAD_TREE":
            level.set_cell(front_col, front_row, "TREE")
            return "PLANTED"
        if cell == "TRASH":
            level.set_cell(front_col, front_row, "FLOOR")
            return "COLLECTED"
        return "NOTHING"

    
    # Animación y dibujo
    

    def update(self) -> None:
        """Interpola pixel_x/y hacia target_x/y para animar el movimiento."""
        if not self.moving:
            return
        speed = settings.TILE_SIZE / settings.ROBOT_STEP_FRAMES
        if self.pixel_x < self.target_x:
            self.pixel_x = min(self.pixel_x + speed, self.target_x)
        elif self.pixel_x > self.target_x:
            self.pixel_x = max(self.pixel_x - speed, self.target_x)
        if self.pixel_y < self.target_y:
            self.pixel_y = min(self.pixel_y + speed, self.target_y)
        elif self.pixel_y > self.target_y:
            self.pixel_y = max(self.pixel_y - speed, self.target_y)
        if self.pixel_x == self.target_x and self.pixel_y == self.target_y:
            self.moving = False

    def draw(self, surface: pygame.Surface, origin: tuple[int, int]) -> None:
        """Dibuja al robot en su posición visual actual."""
        origin_x, origin_y = origin
        margin = settings.TILE_SIZE // 8
        rect = pygame.Rect(
            origin_x + int(self.pixel_x) + margin,
            origin_y + int(self.pixel_y) + margin,
            settings.TILE_SIZE - 2 * margin,
            settings.TILE_SIZE - 2 * margin,
        )
        pygame.draw.rect(surface, settings.COLOR_ROBOT, rect)
