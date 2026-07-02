"""Nivel del juego: carga el JSON, conoce la grilla y la dibuja."""
import json
from pathlib import Path

import pygame

import settings
from utils.assets import load_image
from utils.tile_atlas import init_atlas, get_tile, get_ocean_tile, get_city_tile, get_decoration

# Tipos de celda sobre los que el robot puede pararse
WALKABLE_TILES = {"FLOOR", "GOAL", "WATER", "CITY_FLOOR"}

# (col, row, padding) dentro de Tileset1xPadding.png — 16x16 tiles, 1px padding.
# (1,1) = pasto sólido limpio (centro del blob autotile, filas 0-2).
# (6,9) = tierra/dirt casi sólida con leve textura.
# (1,12) = agua sólida limpia (fila 12 es agua lisa completa).
# Las filas 4-8 y 10-11 son anillos tipo autotile (sin centro sólido),
# por lo que WALL, TREE y GOAL se resuelven con Decorations.png.
TILE_TO_SPRITESHEET: dict[str, tuple[int, int, int]] = {
    "FLOOR":       (1, 1, 1),   # pasto sólido limpio
    "DEAD_TREE":   (6, 9, 1),   # tierra/dirt -> sendero
    "TRASH":       (6, 9, 1),   # mismo tono tierra
    "SMOG":        (1, 1, 1),
}

# (col, row) dentro de punyworld-overworld-tileset.png — 16×16 tiles sin padding.
OCEAN_TILE_POSITIONS: dict[str, tuple[int, int]] = {
    "WATER":     (4, 11),  # agua oceánica azul profundo
    "ROCK":      (10, 26), # roca gris
    "CORAL":     (14, 33), # coral rojo/naranja
    "OIL_SPILL": (4, 11), # misma base agua + overlay oscuro
    "PLASTIC":   (4, 11), # misma base agua + overlay botella
}

# (row, col) dentro de galletcity_tiles.png — 8×8 tiles sin padding.
CITY_TILE_POSITIONS: dict[str, tuple[int, int]] = {
    "CITY_FLOOR":  (4, 0),   # sidewalk beige (posición más común)
    "BUILDING":    (17, 3),  # techo/edificio marrón
}

# Decoraciones (Decorations.png) como overlay sobre el tile base
TILE_TO_DECORATION: dict[str, str] = {
    "WALL":      "sprite_10",  # arbusto/roca compacta
    "TREE":      "sprite_16",  # arbusto verde mediano
    "DEAD_TREE": "sprite_1",   # tronco caído sobre tierra
    "GOAL":      "sprite_12",  # planta alta (marcador)
}

# Tipos cuyo gráfico final es 100% la decoración (no se pisa el tile de fondo)
DECORATION_IS_FULL_TILE: set[str] = {"WALL", "TREE", "GOAL"}


class Level:
    """Representa un nivel cargado desde data/levels/*.json."""

    def __init__(self, path: str | Path) -> None:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        self.name: str = data["name"]
        self.environmental_fact: str = data["environmental_fact"]
        self.max_slots: int = data["max_slots"]
        # Tiempo límite en segundos (#42). 0 o ausente = temporizador desactivado.
        self.time_limit: int = data.get("time_limit", 0)
        # Duración en segundos de la ventana de acción / QTE (#43). Ausente = 2.0.
        self.action_window: float = data.get("action_window", 2.0)
        self.available_instructions: list[str] = data["available_instructions"]
        self.objectives: list[dict] = data["objectives"]
        self.grid: list[list[str]] = data["grid"]

        self.robot_start_col: int = data["robot_start"]["col"]
        self.robot_start_row: int = data["robot_start"]["row"]
        self.robot_start_direction: str = data["robot_start"]["direction"]

        self.rows: int = len(self.grid)
        self.cols: int = len(self.grid[0])

        # Inicializar atlas global (una sola vez)
        init_atlas(settings.TILE_SIZE)

        # Cargar tiles desde spritesheet + fallback a PNG individuales
        size = (settings.TILE_SIZE, settings.TILE_SIZE)
        self.tile_images: dict[str, pygame.Surface] = {}
        for tile_type in settings.TILE_COLORS:
            # 0. Océano: spritesheet Puny World (16×16 sin padding)
            ocean_pos = OCEAN_TILE_POSITIONS.get(tile_type)
            if ocean_pos is not None:
                col, row = ocean_pos
                self.tile_images[tile_type] = get_ocean_tile(col, row)
                continue
            # 1. Ciudad: spritesheet Gallet City (8×8)
            city_pos = CITY_TILE_POSITIONS.get(tile_type)
            if city_pos is not None:
                row, col = city_pos
                self.tile_images[tile_type] = get_city_tile(row, col)
                continue
            # 2. Bosque: spritesheet Tileset1xPadding (16×16 con padding)
            sheet_pos = TILE_TO_SPRITESHEET.get(tile_type)
            if sheet_pos is not None:
                col, row, padding = sheet_pos
                self.tile_images[tile_type] = get_tile(col, row, padding)
                continue
            # 3. Fallback a PNG individual
            img = load_image(settings.TILES_SPRITES_DIR / f"{tile_type.lower()}.png", size)
            if img is not None:
                self.tile_images[tile_type] = img

        # Cargar decoraciones (overlays) desde Decorations.png
        self.decoration_images: dict[str, pygame.Surface] = {}
        for tile_type, sprite_name in TILE_TO_DECORATION.items():
            surf = get_decoration(sprite_name)
            if surf is None:
                continue
            w, h = surf.get_size()
            scale = settings.TILE_SIZE / max(w, h)
            new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
            self.decoration_images[tile_type] = pygame.transform.smoothscale(surf, new_size)

        # PLASTIC: overlay de botella flotando (bottle2idle.png, primer frame 32×32)
        bottle_path = settings.ASSETS_DIR / "tiles" / "ocean" / "bottle2idle.png"
        bottle_raw = load_image(bottle_path)
        if bottle_raw is not None:
            bw, bh = bottle_raw.get_size()
            frame = bottle_raw.subsurface((0, 0, min(32, bw), min(32, bh)))
            scale = settings.TILE_SIZE / max(frame.get_width(), frame.get_height())
            new_size = (max(1, int(frame.get_width() * scale)),
                        max(1, int(frame.get_height() * scale)))
            self.decoration_images["PLASTIC"] = pygame.transform.smoothscale(frame, new_size)

    def is_walkable(self, col: int, row: int) -> bool:
        """Indica si el robot puede pararse en la celda (col, row)"""
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return False
        return self.grid[row][col] in WALKABLE_TILES

    def get_cell(self, col: int, row: int) -> str | None:
        """Retorna el tipo de celda en (col, row), o None si está fuera de límites"""
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return None
        return self.grid[row][col]

    def set_cell(self, col: int, row: int, tile_type: str) -> None:
        """Cambia el tipo de celda en (col, row)."""
        self.grid[row][col] = tile_type

    def draw(self, surface: pygame.Surface, origin: tuple[int, int]) -> None:
        """Dibuja la grilla: tile base del spritesheet + overlay de decoración."""
        origin_x, origin_y = origin
        for row in range(self.rows):
            for col in range(self.cols):
                tile_type = self.grid[row][col]
                rect = pygame.Rect(
                    origin_x + col * settings.TILE_SIZE,
                    origin_y + row * settings.TILE_SIZE,
                    settings.TILE_SIZE,
                    settings.TILE_SIZE,
                )
                # Tile base: si es decoración pura, dibujar FLOOR atrás
                base_type = tile_type if tile_type not in DECORATION_IS_FULL_TILE else "FLOOR"
                image = self.tile_images.get(base_type)
                if image is not None:
                    surface.blit(image, rect)
                else:
                    color = settings.TILE_COLORS.get(base_type, settings.COLOR_BG)
                    pygame.draw.rect(surface, color, rect)

                # Overlay: decoración centrada sobre el tile base
                deco_img = self.decoration_images.get(tile_type)
                if deco_img is not None:
                    dw, dh = deco_img.get_size()
                    dx = origin_x + col * settings.TILE_SIZE + (settings.TILE_SIZE - dw) // 2
                    dy = origin_y + row * settings.TILE_SIZE + settings.TILE_SIZE - dh
                    surface.blit(deco_img, (dx, dy))

                # OIL_SPILL: capa oscura semitransparente (mancha de petróleo)
                if tile_type == "OIL_SPILL":
                    oil = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA)
                    oil.fill((15, 10, 8, 180))
                    surface.blit(oil, rect)

                # SMOG: capa semitransparente grisácea sobre el tile
                if tile_type == "SMOG":
                    smog = pygame.Surface((settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA)
                    smog.fill((120, 120, 100, 140))
                    surface.blit(smog, rect)

                pygame.draw.rect(surface, settings.COLOR_GRID_LINE, rect, width=1)
