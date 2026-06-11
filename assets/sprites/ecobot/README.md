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
- **M** = dirección (⚠️ corregido tras verificar visualmente la variante 3 —
  la versión anterior de esta tabla tenía izquierda/derecha invertidas):
  - `1` = abajo (frente)
  - `2` = derecha
  - `3` = izquierda
  - `4` = arriba (espalda)

Las variantes **3 y 6** traen las 4 direcciones; el resto trae 3 (les falta
`4` = arriba). Para EcoBot conviene partir de la variante **3** o **6**, o
completar la dirección "arriba" a mano.

## Pendiente para issue #14
Los assets vienen como **GIF animado**. Dos cosas a tener en cuenta:

- PyGame (`pygame.image.load`) solo lee el **primer frame** de un GIF → hay que
  extraer los frames a PNG.
- Cada GIF está **recortado a su contenido**, así que el lienzo varía entre
  archivos e incluso entre frames del mismo GIF (~23–31 × 32–35 px). Para
  animar sin "saltos" hay que **normalizar todos los frames a un tamaño de
  frame fijo** (con padding centrado).

Pasos sugeridos:
1. Extraer y aplanar los frames de cada GIF (`-coalesce`).
2. Rellenar cada frame a un lienzo común (p. ej. 32×40) centrado.
3. Componer un **spritesheet PNG** por animación/dirección (o frames sueltos).
4. Definir tamaño de frame y fps en `settings.py`.

Ejemplo con ImageMagick (extrae + normaliza a 32×40 centrado):
```bash
convert "idle/3.1idle.gif" -coalesce -background none -gravity center \
        -extent 32x40 "ecobot_idle_down_%02d.png"
```
