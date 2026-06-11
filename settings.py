from pathlib import Path

# --- Rutas-=--

BASE_DIR   = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR   = BASE_DIR / "data"
LEVELS_DIR = DATA_DIR / "levels"
SAVE_PATH  = DATA_DIR / "save" / "progress.json"

# Sprites del juego (issue #11) — si falta un PNG se usa el color de respaldo
TILES_SPRITES_DIR = ASSETS_DIR / "sprites" / "tiles"
ROBOT_SPRITES_DIR = ASSETS_DIR / "sprites" / "robot"

# --- Ventana
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
WINDOW_TITLE  = "EcoBot"
FPS           = 60

# Colores
COLOR_BG      = (18, 18, 24)
COLOR_TEXT    = (235, 235, 235)

# Colores por tipo de celda (placeholders hasta integrar sprites en #11)
TILE_COLORS = {
    "FLOOR":     (94, 72, 52),    # tierra
    "WALL":      (110, 110, 115), # roca
    "DEAD_TREE": (140, 105, 60),  # tronco seco
    "TREE":      (52, 140, 70),   # árbol plantado
    "TRASH":     (180, 60, 170),  # basura
    "GOAL":      (240, 200, 70),  # meta
}
COLOR_GRID_LINE = (40, 40, 48)
COLOR_ROBOT     = (70, 170, 220)

#Grilla 
TILE_SIZE = 64
ROBOT_STEP_FRAMES =12

# Direcciones del robot
DIRECTIONS = {
    "RIGHT": ( 1,  0),
    "LEFT":  (-1,  0),
    "UP":    ( 0, -1),
    "DOWN":  ( 0,  1),
}

# Estados del juego 
STATE_MENU         = "MENU"
STATE_LEVEL_SELECT = "LEVEL_SELECT"
STATE_INTRO        = "INTRO"
STATE_LEVEL        = "LEVEL"
STATE_VICTORY      = "VICTORY"
STATE_FAILURE      = "FAILURE"