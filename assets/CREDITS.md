# Créditos y licencias de assets

Assets base descargados de itch.io para EcoBot (issue #6, fase-0).

## Tiles del bosque — `assets/tiles/forest/`
- **Pack:** Free Topdown Fantasy - Forest
- **Autor:** aamatniekss
- **Fuente:** https://aamatniekss.itch.io/topdown-fantasy-forest
- **Licencia:** Uso libre comercial y no comercial. Se permite modificar.
  No exige crédito (pero el autor lo agradece). Prohibido revender los
  assets por separado.
- **Formato:** PNG, tiles de **16×16 px**.
  - `Tileset.png` — tileset principal (césped, tierra, acantilado/muro, agua).
  - `Tileset1xPadding.png` — misma hoja con 1 px de padding por tile (evita
    bleeding al escalar).
  - `Decorations.png` — árboles, tronco caído, arbustos, rocas, setas, juncos.
  - `mockups/` — imágenes de ejemplo del autor (solo referencia, no usar en build).
- **Cobertura de la issue #15:** este pack aporta `suelo` (césped/tierra),
  `árbol plantado` (árboles), `árbol muerto` (tronco caído / tocón) y `muro`
  (acantilado/roca). **NO incluye `meta` ni `basura`** (son propios de EcoBot):
  habrá que dibujarlos a mano o buscarlos aparte al hacer la #15.

## Personaje base EcoBot — `assets/sprites/ecobot/`
- **Pack:** Pixel top down Character Pack (4 directions)
- **Autor:** aztrakatze
- **Fuente:** https://aztrakatze.itch.io/top-down-character-pack-4-directions
- **Licencia:** Free to use.
- **Formato:** GIF animado, sprites recortados al contenido y de **tamaño
  variable** (~23–31 × 32–35 px según variante/frame). Ver
  `assets/sprites/ecobot/README.md` para convención de nombres, direcciones y
  el paso de conversión a spritesheet PNG (issue #14).
- **Nota:** son personajes humanos placeholder; se reskinearán a robot (EcoBot)
  en la issue #14.

## Sprites del juego (derivados) — `assets/sprites/tiles/` y `assets/sprites/robot/` (issue #11)

PNGs de **64×64 px** que el juego carga en `core/level.py` y `core/robot.py`
(con fallback a color si faltan). Derivados de los packs de arriba:

| Archivo | Origen | Derivación |
|---|---|---|
| `tiles/floor.png` | Tileset.png (aamatniekss) | tile de césped escalado ×4 |
| `tiles/wall.png` | Decorations.png (aamatniekss) | pilas de roca sobre césped |
| `tiles/dead_tree.png` | Decorations.png (aamatniekss) | tronco caído sobre césped |
| `tiles/tree.png` | Decorations.png (aamatniekss) | árbol sobre césped |
| `tiles/trash.png` | **elaboración propia** | bolsa de basura dibujada, sobre césped del pack |
| `tiles/goal.png` | **elaboración propia** | bandera a cuadros dibujada, sobre césped del pack |
| `robot/idle.png`, `walk.png` | GIFs variante 3 (aztrakatze) | primer frame, fallback estático 64×64 |
| `robot/idle_{down,left,right,up}/` | GIFs `3.M idle` (aztrakatze) | 4 frames/dirección: extraídos con `-coalesce`, lienzo normalizado 32×36 y escalados a 64×64 |
| `robot/walk_{down,left,right,up}/` | GIFs `3.M run` (aztrakatze) | 6 frames/dirección: ídem |

Las licencias de los packs originales (uso libre, modificación permitida) cubren
estos derivados.

## Nivel 2 — Océano (`assets/tiles/ocean/`)
- **16x16 Puny World Tileset** por Shade (CC0)
  Seawater tiles para WATER y elevación/roca para ROCK.
  Fuente: https://opengameart.org/content/16x16-puny-world-tileset
- **Pixel Art Lake Assets** por AmberFallStudio (CC0)
  Trash flotante (bottle2idle.png) para PLASTIC.
  Fuente: https://opengameart.org/content/pixel-art-lake-assets
- **Trawler Tileset** (incluido en el pack anterior) — tileset de laguna 16×16.
- Tile de OIL_SPILL y CORAL: modificaciones propias sobre tiles CC0.

## Nivel 3 — Ciudad (`assets/tiles/city/`)
- **Gallet City** por Adam Saltsman (Dominio Público) — `galletcity_tiles.png`
  Tileset de ciudad top-down 8×8 con 166 tiles (calles, veredas, edificios).
  Tile 32 (vereda) → CITY_FLOOR, Tile 139 (techo) → BUILDING.
  Fuente: https://adamatomic.itch.io/gallet-city
- **Fog Animation** por AntumDeluge (CC0) — `fog.png`
  Capa de niebla/smog tileable con canal alpha para superponer sobre la ciudad.
  Fuente: https://opengameart.org/content/fog-animation
