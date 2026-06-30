"""Escanea Decorations.png y detecta sprites por contigüidad de alpha > 0.

Genera un JSON con bounding boxes para cargar en tile_atlas.py.
Uso: python tools/extract_decorations.py
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image


def find_sprites(path: str | Path, min_size: int = 8) -> list[dict]:
    """Encuentra bounding boxes de sprites no transparentes en una imagen.

    Args:
        path: Ruta a la imagen PNG.
        min_size: Tamaño mínimo (ancho o alto) para filtrar ruido.

    Returns:
        Lista de dicts: {"name": f"sprite_{i}", "rect": [x, y, w, h]}
        ordenados por fila (top-to-bottom), luego columna (left-to-right).
    """
    img = Image.open(path).convert("RGBA")
    arr = np.array(img)
    alpha = arr[:, :, 3]

    visited = np.zeros_like(alpha, dtype=bool)
    sprites: list[dict] = []

    for y in range(alpha.shape[0]):
        for x in range(alpha.shape[1]):
            if alpha[y, x] == 0 or visited[y, x]:
                continue

            # Flood-fill para encontrar el sprite completo
            stack = [(y, x)]
            min_y, max_y = y, y
            min_x, max_x = x, x

            while stack:
                cy, cx = stack.pop()
                if cy < 0 or cy >= alpha.shape[0] or cx < 0 or cx >= alpha.shape[1]:
                    continue
                if visited[cy, cx] or alpha[cy, cx] == 0:
                    continue
                visited[cy, cx] = True
                min_y, max_y = min(min_y, cy), max(max_y, cy)
                min_x, max_x = min(min_x, cx), max(max_x, cx)
                stack.extend([(cy - 1, cx), (cy + 1, cx),
                              (cy, cx - 1), (cy, cx + 1)])

            w = max_x - min_x + 1
            h = max_y - min_y + 1
            if w >= min_size and h >= min_size:
                sprites.append({
                    "name": f"sprite_{len(sprites)}",
                    "rect": [int(min_x), int(min_y), int(w), int(h)],
                })

    # Ordenar top-to-bottom, left-to-right
    sprites.sort(key=lambda s: (s["rect"][1], s["rect"][0]))
    return sprites


def main() -> None:
    assets_dir = Path("assets") / "tiles" / "forest"
    deco_path = assets_dir / "Decorations.png"

    if not deco_path.is_file():
        print(f"ERROR: no se encuentra {deco_path}")
        return

    print(f"Escaneando {deco_path} …")
    sprites = find_sprites(deco_path)

    out_path = assets_dir / "_decoration_rects.json"
    with open(out_path, "w") as f:
        json.dump({s["name"]: s["rect"] for s in sprites}, f, indent=2)

    print(f"Detectados {len(sprites)} sprites -> {out_path}")
    print()
    print("REVISIÓN MANUAL REQUERIDA:")
    print("  Abre assets/tiles/forest/Decorations.png y asigna nombres")
    print("  significativos editando el JSON o tile_atlas.py")
    print()
    for s in sprites:
        print(f"  {s['name']:15s} -> rect={s['rect']}")


if __name__ == "__main__":
    main()
