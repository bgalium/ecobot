"""Mapa de nombres → coordenadas de tiles en los spritesheets."""

from pathlib import Path

import pygame

from utils.spritesheet import SpriteSheet

# ── Rutas ──────────────────────────────────────────────────────────────────
TILESHEET_DIR = Path("assets") / "tiles" / "forest"
TILESET_PADDED = TILESHEET_DIR / "Tileset1xPadding.png"
TILESET_PLAIN  = TILESHEET_DIR / "Tileset.png"
DECORATIONS    = TILESHEET_DIR / "Decorations.png"

CITY_DIR       = Path("assets") / "tiles" / "city"
CITY_TILESET   = CITY_DIR / "galletcity_tiles.png"

OCEAN_DIR      = Path("assets") / "tiles" / "ocean"
PUNY_TILESET   = OCEAN_DIR / "punyworld-overworld-tileset.png"

# ── Parámetros de grilla ───────────────────────────────────────────────────
TILE_W = 16
TILE_H = 16
PADDING = 1       # Tileset1xPadding.png usa 1px de padding

CITY_TILE_W = 8   # Gallet City usa tiles de 8×8
CITY_TILE_H = 8
CITY_COLS = 8     # 8 columnas en el spritesheet

# ── Posiciones de tiles en la grilla (col, row) ──────────────────────────
# Tileset1xPadding.png: 8 cols × 16 rows
#
# Rows 0-2:  Hierba / pasto (variantes para blob autotile)
# Rows 3-5:  Tierra / dirt (transición)
# Rows 6-8:  Acantilado / roca (anillo tipo wang tile)
# Row  9:    Hierba con flores / especial
# Rows 10-14: Agua / lago (anillo tipo wang tile)
# Row  15:   Vacío

# ── Hierba / Grass ─────────────────────────────────────────────────────────
GRASS_PLAIN       = (0, 0)
GRASS_VARIANT_1   = (1, 0)
GRASS_VARIANT_2   = (2, 0)
GRASS_VARIANT_3   = (3, 0)
GRASS_DARK        = (4, 0)
GRASS_DARK_2      = (5, 0)
GRASS_EDGE_1      = (0, 1)
GRASS_EDGE_2      = (1, 1)
GRASS_EDGE_3      = (2, 1)
GRASS_EDGE_4      = (3, 1)
GRASS_TRANSITION  = (4, 1)
GRASS_FLOWERS     = (5, 1)
GRASS_DRY         = (0, 2)
GRASS_DRY_2       = (1, 2)
GRASS_DRY_EDGE    = (2, 2)
GRASS_DRY_EDGE_2  = (3, 2)
GRASS_DRY_SPOT    = (4, 2)
GRASS_DRY_SPOT_2  = (5, 2)

# ── Tierra / Dirt ──────────────────────────────────────────────────────────
DIRT_LIGHT        = (0, 3)
DIRT              = (1, 3)
DIRT_DARK         = (2, 3)
DIRT_CORNER_TL    = (3, 3)   # Esquina tierra-roca
DIRT_EDGE_T       = (4, 3)
DIRT_CORNER_TR    = (5, 3)
DIRT_EDGE_L       = (0, 4)
DIRT_CENTER       = (1, 4)
DIRT_EDGE_R       = (2, 4)
DIRT_EDGE_B       = (3, 4)
DIRT_CORNER_BL    = (4, 4)
DIRT_CORNER_BR    = (5, 4)
DIRT_PATCH_1      = (0, 5)
DIRT_PATCH_2      = (1, 5)
DIRT_PATCH_3      = (2, 5)
DIRT_PATCH_4      = (3, 5)
DIRT_PATCH_5      = (4, 5)
DIRT_PATCH_6      = (5, 5)

# ── Acantilado / Roca ─────────────────────────────────────────────────────
CLIFF_CORNER_TL   = (3, 6)
CLIFF_EDGE_T      = (4, 6)
CLIFF_CORNER_TR   = (5, 6)
CLIFF_EDGE_L      = (3, 7)
CLIFF_CENTER      = (4, 7)
CLIFF_EDGE_R      = (5, 7)
CLIFF_CORNER_BL   = (3, 8)
CLIFF_EDGE_B      = (4, 8)
CLIFF_CORNER_BR   = (5, 8)
CLIFF_SOLO        = (6, 6)
CLIFF_TOP_EXTRA   = (6, 7)

# ── Agua / Water ──────────────────────────────────────────────────────────
WATER_CORNER_TL   = (0, 10)
WATER_EDGE_T      = (1, 10)
WATER_CORNER_TR   = (2, 10)
WATER_EDGE_L      = (0, 11)
WATER_CENTER      = (1, 11)
WATER_EDGE_R      = (2, 11)
WATER_CORNER_BL   = (0, 12)
WATER_EDGE_B      = (1, 12)
WATER_CORNER_BR   = (2, 12)
WATER_DEEP        = (3, 11)
WATER_PUDDLE      = (6, 10)
WATER_RIPPLE      = (6, 11)
WATER_FLOW        = (6, 12)

# ── Especiales / Decoración en grilla ─────────────────────────────────────
FLOWER_RED        = (0, 9)
FLOWER_YELLOW     = (1, 9)
FLOWER_WHITE      = (2, 9)
DEAD_GRASS        = (3, 9)
MOSS              = (4, 9)
FALLEN_LEAVES     = (5, 9)
STONE_LIGHT       = (6, 9)
STONE_DARK        = (7, 9)

# ── Ciudad (Gallet City — 8×8 tiles, spritesheet de 168 tiles) ────────────
# Tile 32 (row 4, col 0) = vereda beige claro → CITY_FLOOR
# Tile 139 (row 17, col 3) = techo/edificio marrón → BUILDING
# Tile 46 (row 5, col 6) = asfalto gris claro → variante CITY_FLOOR
CITY_FLOOR_TILE = (4, 0)   # sidewalk pavement
BUILDING_TILE   = (17, 3)  # brown roof/building

# ── Decoraciones (recortes libres desde Decorations.png) ──────────────────
# Detectadas automáticamente por tools/extract_decorations.py.
# Valores por defecto: (x, y, w, h) — se sobreescriben al cargar el JSON.
DECORATION_RECTS: dict[str, tuple[int, int, int, int]] = {
    "TREE_LARGE_1":     (11, 143, 70, 98),
    "TREE_LARGE_2":     (88, 143, 70, 94),
    "TREE_MEDIUM_1":    (163, 163, 38, 74),
    "TREE_MEDIUM_2":    (211, 163, 38, 70),
    "TREE_SMALL_1":     (75, 0, 40, 32),
    "TREE_SMALL_2":     (75, 32, 39, 30),
    "BUSH_LARGE_1":     (68, 67, 24, 27),
    "BUSH_LARGE_2":     (100, 67, 24, 27),
    "BUSH_SMALL_1":     (136, 9, 16, 14),
    "BUSH_SMALL_2":     (136, 41, 16, 13),
    "FLOWER_TALL_1":    (8, 70, 14, 22),
    "FLOWER_TALL_2":    (40, 70, 14, 22),
    "FLOWER_SHORT_1":   (8, 102, 14, 20),
    "FLOWER_SHORT_2":   (40, 102, 14, 20),
    "MUSHROOM_RED_1":   (204, 8, 12, 14),
    "MUSHROOM_RED_2":   (204, 40, 12, 12),
    "MUSHROOM_RED_3":   (204, 71, 12, 14),
    "ROCK_CLUSTER_1":   (163, 133, 26, 22),
    "ROCK_CLUSTER_2":   (194, 133, 27, 23),
    "ROCK_CLUSTER_3":   (228, 133, 22, 21),
    "ROCK_SMALL_1":     (173, 10, 10, 12),
    "ROCK_SMALL_2":     (173, 42, 9, 11),
    "ROCK_SMALL_3":     (173, 73, 10, 12),
    "GRASS_TUFT_1":     (169, 109, 15, 11),
    "GRASS_TUFT_2":     (200, 109, 16, 12),
    "GRASS_TUFT_3":     (234, 109, 12, 10),
    "LOG":              (13, 4, 35, 27),
    "LOG_SHORT":        (15, 35, 31, 25),
}

# ── Caché global ──────────────────────────────────────────────────────────
_sheets: dict[str, SpriteSheet] = {}
_scaled_tiles: dict[tuple, pygame.Surface] = {}
_loaded_rects: dict[str, tuple[int, int, int, int]] = {}

TILE_SCALE: int | None = None  # Lo setea init_atlas() según settings.TILE_SIZE


def init_atlas(tile_size: int) -> None:
    """Inicializa el atlas. Llama una vez al arrancar el juego."""
    global TILE_SCALE
    TILE_SCALE = tile_size // TILE_W  # ej: 64/16 = 4

    _sheets["main"] = SpriteSheet(TILESET_PADDED)
    _sheets["decorations"] = SpriteSheet(DECORATIONS)
    _sheets["city"] = SpriteSheet(CITY_TILESET)
    _sheets["ocean"] = SpriteSheet(PUNY_TILESET)

    # Cargar rects de decoraciones desde JSON si existe
    json_path = TILESHEET_DIR / "_decoration_rects.json"
    if json_path.is_file():
        import json
        with open(json_path) as f:
            data = json.load(f)
        _loaded_rects.update(data)


def get_tile(col: int, row: int, padding: int = PADDING) -> pygame.Surface | None:
    """Obtiene un tile de la grilla, escalado a TILE_SIZE."""
    key = (col, row, padding)
    if key not in _scaled_tiles:
        sheet = _sheets["main"]
        tile = sheet.get_tile(col, row, TILE_W, TILE_H, padding)
        if tile is None:
            _scaled_tiles[key] = None
        else:
            if TILE_SCALE and TILE_SCALE != 1:
                tile = pygame.transform.scale(
                    tile, (TILE_W * TILE_SCALE, TILE_H * TILE_SCALE)
                )
            _scaled_tiles[key] = tile
    return _scaled_tiles[key]


def get_city_tile(row: int, col: int) -> pygame.Surface | None:
    """Obtiene un tile de 8×8 del spritesheet de Gallet City, escalado a TILE_SIZE."""
    key = ("city", row, col)
    if key not in _scaled_tiles:
        sheet = _sheets["city"]
        tile = sheet.get_tile(col, row, CITY_TILE_W, CITY_TILE_H, 0)
        if tile is None:
            _scaled_tiles[key] = None
        else:
            city_scale = (TILE_SCALE * TILE_W) // CITY_TILE_W if TILE_SCALE else 1
            tile = pygame.transform.scale(
                tile, (CITY_TILE_W * city_scale, CITY_TILE_H * city_scale)
            )
            _scaled_tiles[key] = tile
    return _scaled_tiles[key]


def get_ocean_tile(col: int, row: int) -> pygame.Surface | None:
    """Obtiene un tile de 16×16 del spritesheet Puny World, escalado a TILE_SIZE."""
    key = ("ocean", col, row)
    if key not in _scaled_tiles:
        sheet = _sheets["ocean"]
        tile = sheet.get_tile(col, row, TILE_W, TILE_H, 0)
        if tile is None:
            _scaled_tiles[key] = None
        else:
            if TILE_SCALE and TILE_SCALE != 1:
                tile = pygame.transform.scale(
                    tile, (TILE_W * TILE_SCALE, TILE_H * TILE_SCALE)
                )
            _scaled_tiles[key] = tile
    return _scaled_tiles[key]


def get_tile_by_name(name: str) -> pygame.Surface | None:
    """Obtiene un tile por su nombre (ej: 'GRASS_PLAIN')."""
    coords = _TILE_NAMES.get(name)
    if coords is None:
        return None
    return get_tile(*coords)


def get_decoration(name: str) -> pygame.Surface | None:
    """Obtiene un sprite de decoración escalado a TILE_SIZE."""
    rect = _loaded_rects.get(name) or DECORATION_RECTS.get(name)
    if rect is None:
        return None
    x, y, w, h = rect
    sheet = _sheets["decorations"]
    sprite = sheet.get_sprite(x, y, w, h)
    if sprite is None:
        return None
    if TILE_SCALE and TILE_SCALE != 1:
        sprite = pygame.transform.scale(
            sprite, (w * TILE_SCALE, h * TILE_SCALE)
        )
    return sprite


# Mapa inverso nombre → (col, row)
_TILE_NAMES: dict[str, tuple[int, int]] = {
    "GRASS_PLAIN":      GRASS_PLAIN,
    "GRASS_VARIANT_1":  GRASS_VARIANT_1,
    "GRASS_VARIANT_2":  GRASS_VARIANT_2,
    "GRASS_VARIANT_3":  GRASS_VARIANT_3,
    "GRASS_DARK":       GRASS_DARK,
    "GRASS_DARK_2":     GRASS_DARK_2,
    "GRASS_EDGE_1":     GRASS_EDGE_1,
    "GRASS_EDGE_2":     GRASS_EDGE_2,
    "GRASS_EDGE_3":     GRASS_EDGE_3,
    "GRASS_EDGE_4":     GRASS_EDGE_4,
    "GRASS_DRY":        GRASS_DRY,
    "GRASS_DRY_2":      GRASS_DRY_2,
    "GRASS_DRY_EDGE":   GRASS_DRY_EDGE,
    "GRASS_DRY_EDGE_2": GRASS_DRY_EDGE_2,
    "DIRT":             DIRT,
    "DIRT_LIGHT":       DIRT_LIGHT,
    "DIRT_DARK":        DIRT_DARK,
    "DIRT_CENTER":      DIRT_CENTER,
    "CLIFF_CORNER_TL":  CLIFF_CORNER_TL,
    "CLIFF_EDGE_T":     CLIFF_EDGE_T,
    "CLIFF_CORNER_TR":  CLIFF_CORNER_TR,
    "CLIFF_EDGE_L":     CLIFF_EDGE_L,
    "CLIFF_CENTER":     CLIFF_CENTER,
    "CLIFF_EDGE_R":     CLIFF_EDGE_R,
    "CLIFF_CORNER_BL":  CLIFF_CORNER_BL,
    "CLIFF_EDGE_B":     CLIFF_EDGE_B,
    "CLIFF_CORNER_BR":  CLIFF_CORNER_BR,
    "WATER_CENTER":     WATER_CENTER,
    "WATER_DEEP":       WATER_DEEP,
    "FLOWER_RED":       FLOWER_RED,
    "FLOWER_YELLOW":    FLOWER_YELLOW,
}
