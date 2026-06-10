"""Nivel del juego: carga el JSON, conoce la grilla y la dibuja."""
import json
from pathlib import Path

import pygame

import settings

# Tipos de celda sobre los que el robot puede pararse
WALKABLE_TILES = {"FLOOR", "GOAL"}


class Level:
    """Representa un nivel cargado desde data/levels/*.json."""

    def __init__(self, path: str | Path) -> None:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        self.name: str = data["name"]
        self.environmental_fact: str = data["environmental_fact"]
        self.max_slots: int = data["max_slots"]
        self.available_instructions: list[str] = data["available_instructions"]
        self.objectives: list[dict] = data["objectives"]
        self.grid: list[list[str]] = data["grid"]

        self.robot_start_col: int = data["robot_start"]["col"]
        self.robot_start_row: int = data["robot_start"]["row"]
        self.robot_start_direction: str = data["robot_start"]["direction"]

        self.rows: int = len(self.grid)
        self.cols: int = len(self.grid[0])

    def is_walkable(self, col: int, row: int) -> bool:
        """Indica si el robot puede pararse en la celda (col, row)."""
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return False
        return self.grid[row][col] in WALKABLE_TILES

    def draw(self, surface: pygame.Surface, origin: tuple[int, int]) -> None:
        """Dibuja la grilla celda por celda con un color por tipo de celda."""
        origin_x, origin_y = origin
        for row in range(self.rows):
            for col in range(self.cols):
                tile_type = self.grid[row][col]
                color = settings.TILE_COLORS.get(tile_type, settings.COLOR_BG)
                rect = pygame.Rect(
                    origin_x + col * settings.TILE_SIZE,
                    origin_y + row * settings.TILE_SIZE,
                    settings.TILE_SIZE,
                    settings.TILE_SIZE,
                )
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, settings.COLOR_GRID_LINE, rect, width=1)
