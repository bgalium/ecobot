# Sprites base de EcoBot

Pack base descargado de itch.io (aztrakatze, "Top Down Character Pack - 4
directions", licencia *free to use*). Ver `assets/CREDITS.md`.

Son placeholders humanos: se **reskinean a robot** (EcoBot) en la issue #14.

## Contenido
- `idle/` — animación de reposo.
- `run/` — animación de caminar/correr.

## Convención de nombres
Archivos `N.M<anim>.gif`:
- **N** = variante de personaje (1–6).
- **M** = dirección:
  - `1` = abajo (frente)
  - `2` = izquierda
  - `3` = derecha
  - `4` = arriba (espalda)

Las variantes **3 y 6** traen las 4 direcciones; el resto trae 3 (les falta
`4` = arriba). Para EcoBot conviene partir de la variante **3** o **6**, o
completar la dirección "arriba" a mano.

## Pendiente para issue #14
Los assets vienen como **GIF animado** (~29×33 px). PyGame (`pygame.image.load`)
solo lee el primer frame de un GIF, así que hay que:
1. Extraer los frames de cada GIF a PNG.
2. Componer un **spritesheet PNG** por animación/dirección (o frames sueltos).
3. Definir el tamaño de frame y fps en `settings.py`.

Ejemplo de extracción de frames con ImageMagick:
```bash
convert "idle/3.1idle.gif" -coalesce "ecobot_idle_down_%02d.png"
```
