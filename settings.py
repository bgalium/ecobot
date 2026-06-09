from pathlib import Path

# --- Rutas-=--

BASE_DIR   = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR   = BASE_DIR / "data"
LEVELS_DIR = DATA_DIR / "levels"
SAVE_PATH  = DATA_DIR / "save" / "progress.json"

# --- Ventana
SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
WINDOW_TITLE  = "EcoBot"
FPS           = 60

# Colores
COLOR_BG      = (18, 18, 24)
COLOR_TEXT    = (235, 235, 235)

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