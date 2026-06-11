"""EcoBot: posición y dirección en la grilla, y su dibujado en pantalla."""
import pygame

import settings
from core.transforms import apply_translation
from utils.assets import load_frames, load_image


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

        # Sprites (issue #11): si falta el PNG se dibuja el rectángulo de respaldo
        size = (settings.TILE_SIZE, settings.TILE_SIZE)
        self.sprites: dict[str, pygame.Surface | None] = {
            "idle": load_image(settings.ROBOT_SPRITES_DIR / "idle.png", size),
            "walk": load_image(settings.ROBOT_SPRITES_DIR / "walk.png", size),
        }

        # Animaciones por dirección (carpetas idle_down/, walk_right/, ...).
        # Si una no existe se cae al sprite estático y luego al rectángulo.
        self.animations: dict[tuple[str, str], list[pygame.Surface]] = {}
        for anim in ("idle", "walk"):
            for direction in settings.DIRECTIONS:
                frames = load_frames(
                    settings.ROBOT_SPRITES_DIR / f"{anim}_{direction.lower()}", size
                )
                if frames:
                    self.animations[(anim, direction)] = frames
        self.frame_index: int = 0
        self.frame_timer: int = 0

    # Movimiento

    def move_forward(self, level) -> str:
        """Avanza una celda en la dirección actual usando traslación homogénea.

        La posición es el vector [col, row, 1]ᵀ y la celda destino se obtiene
        multiplicándolo por la matriz de traslación 3×3 T(dx, dy) con NumPy
        (Unidad 4: transformaciones afines). Retorna "OK", "WALL" o "FELL".
        """
        dx, dy = settings.DIRECTIONS[self.direction]
        nueva_col, nueva_row = apply_translation(self.col, self.row, dx, dy)
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
        """Avanza el ciclo de animación e interpola pixel_x/y hacia target_x/y."""
        self.frame_timer += 1
        if self.frame_timer >= settings.ANIMATION_FRAME_TICKS:
            self.frame_timer = 0
            self.frame_index += 1

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
        """Dibuja al robot: animación de su dirección > sprite estático > rectángulo."""
        origin_x, origin_y = origin
        pos = (origin_x + int(self.pixel_x), origin_y + int(self.pixel_y))

        anim = "walk" if self.moving else "idle"
        frames = self.animations.get((anim, self.direction))
        if frames:
            surface.blit(frames[self.frame_index % len(frames)], pos)
            return

        sprite = self.sprites["walk"] if self.moving else self.sprites["idle"]
        if sprite is None:
            sprite = self.sprites["idle"] or self.sprites["walk"]
        if sprite is not None:
            surface.blit(sprite, pos)
            return

        margin = settings.TILE_SIZE // 8
        rect = pygame.Rect(
            origin_x + int(self.pixel_x) + margin,
            origin_y + int(self.pixel_y) + margin,
            settings.TILE_SIZE - 2 * margin,
            settings.TILE_SIZE - 2 * margin,
        )
        pygame.draw.rect(surface, settings.COLOR_ROBOT, rect)
