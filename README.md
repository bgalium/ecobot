# EcoBot 

Juego educativo de pensamiento computacional  con temática ambiental. El jugador no controla al robot directamente - arma una secuencia de instrucciones y EcoBot las ejecuta para limpiar ecosistemas destruidos.

Desarrollado para el curso de Computación Gráfica - UNI 2026

---

## ¿Cómo se juega?

1. Observas el escenario: EcoBot al inicio, objetivos en el mapa y una meta.
2. Arrastras tarjetas de instrucciones (AVANZAR, GIRAR, ACCIÓN...) a un panel.
3. Presionas **EJECUTAR** y EcoBot sigue exactamente lo que programaste.
4. Si completa todos los objetivos y llega a la meta -> victoria.
5. Si choca, cae o se queda sin instrucciones -> fallo, reintentar.

El reto está en encontrar la secuencia más eficiente. Hacerlo con menos instrucciones da más estrellas.

## Instalación

**Requisitos:** Python 3.11 o superior, Git

```bash
git clone https://github.com/bgalium/ecobot
cd ecobot
python3 -m venv .venv
source .venv/bin/activate      
pip install -r requirements.txt
python main.py
```
---

## Tecnologías

| Libreria | Uso en el proyecto |
|----------|--------------------|
| PyGame 2.x | Motor del juego: ventana, sprites, animaciones, audio, input |
| NumPy | Puente entre superficies de PyGame y arrays de OpenCV |
| OpenCV | Filtro Sobel aplicado sobre el frame real del juego en el Nivel 3 |


---

## Estructura del proyecto

```
ecobot/
├── core/           Motor: robot, niveles, interprete de instrucciones
├── ui/             Pantallas: menu, panel de instrucciones, victoria
├── filters/        Filtro Sobel con OpenCV (Nivel 3)
├── utils/          Puente PyGame - NumPy
├── data/levels/    Niveles en formato JSON
├── assets/         Sprites, tiles, musica y fuentes
├── main.py         Punto de entrada
└── settings.py     Constantes globales del juego
```

---

## Niveles

| N | Ecosistema | Mecanica nueva |
|---|------------|----------------|
| 1 | Bosque Amazonico | AVANZAR, GIRAR, ACCION - nivel tutorial |
| 2 | Oceano Contaminado | SALTAR, REPETIR(n) |
| 3 | Ciudad con Smog | VISION - filtro Sobel sobre zona oscura |

---

## Cobertura del silabo

| Unidad | Tema | Implementacion |
|--------|------|----------------|
| U4 | PyGame, colliders, mecanicas | Motor completo del juego |
| U4 | Transformaciones afines, coordenadas homogeneas | Movimiento del robot con matrices 3x3 |
| U1 | Filtros espaciales, deteccion de bordes | Filtro Sobel en Nivel 3 |
| U1 | Modelos de color HSV | Indicador de salud del ecosistema |

---

## Roadmap

- [x] Fase 0 - Setup del repositorio
- [x] Fase 1 - Motor base + Nivel 1
- [ ] Fase 2 - UI completa + Nivel 2
- [ ] Fase 3 - Filtro Sobel + Nivel 3
- [ ] Fase 4 - Pulido y entrega

---

## Equipo

| Integrante |
|------------|
| Aaron Davila Santos |
| Max Serrano Arostegui | 
| Walter Poma Navarro | 