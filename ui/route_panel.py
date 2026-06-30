"""Panel lateral que muestra y recibe la secuencia de flechas del jugador."""
import pygame

_DIR_SYMBOL = {"UP": "^", "DOWN": "v", "LEFT": "<", "RIGHT": ">"}
_TURNS_CW   = ["RIGHT", "DOWN", "LEFT", "UP"]


def _turns_to(current: str, target: str) -> list[str]:
    """Secuencia mínima de giros para pasar de current a target."""
    diff = (_TURNS_CW.index(target) - _TURNS_CW.index(current)) % 4
    if diff == 0:   return []
    if diff == 1:   return ["TURN_RIGHT"]
    if diff == 2:   return ["TURN_RIGHT", "TURN_RIGHT"]
    return ["TURN_LEFT"]


class RoutePanel:
    def __init__(self, max_slots: int) -> None:
        self.max_slots = max_slots
        self.steps: list[str] = []
        pygame.font.init()
        self._font       = pygame.font.SysFont(None, 36, bold=True)
        self._font_small = pygame.font.SysFont(None, 22)

    # ------------------------------------------------------------------
    # Edición de la secuencia
    # ------------------------------------------------------------------

    def add_step(self, key: int) -> None:
        if len(self.steps) >= self.max_slots:
            return
        direction = {
            pygame.K_UP: "UP", pygame.K_DOWN: "DOWN",
            pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT",
        }.get(key)
        if direction:
            self.steps.append(direction)

    def remove_last(self) -> None:
        if self.steps:
            self.steps.pop()

    def clear(self) -> None:
        self.steps.clear()

    # ------------------------------------------------------------------
    # Conversión a instrucciones del intérprete
    # ------------------------------------------------------------------

    def to_instructions(self, start_direction: str) -> list[str]:
        """Convierte la lista de direcciones a instrucciones MOVE/TURN."""
        instructions: list[str] = []
        current = start_direction
        for target in self.steps:
            instructions.extend(_turns_to(current, target))
            instructions.append("MOVE")
            current = target
        return instructions

    # ------------------------------------------------------------------
    # Renderizado
    # ------------------------------------------------------------------

    def draw(self, screen: pygame.Surface, interactive: bool = True) -> None:
        w, h = screen.get_size()

        panel_w  = 360
        panel_h  = h - 20
        panel_x  = w - panel_w - 10
        panel_y  = 10

        # Fondo semitransparente
        bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        bg.fill((15, 15, 15, 200))
        screen.blit(bg, (panel_x, panel_y))

        # Título
        title = self._font.render("Ruta de movimiento", True, (210, 210, 210))
        screen.blit(title, (panel_x + 12, panel_y + 12))

        # Contador de slots
        full   = len(self.steps) >= self.max_slots
        c_col  = (255, 90, 90) if full else (150, 150, 150)
        count  = self._font_small.render(f"{len(self.steps)} / {self.max_slots}", True, c_col)
        screen.blit(count, (panel_x + panel_w - count.get_width() - 12, panel_y + 16))

        # Grilla de celdas  (5 columnas × N filas)
        cols      = 5
        cell_size = 52
        ox        = panel_x + (panel_w - cols * cell_size) // 2
        oy        = panel_y + 52

        for i in range(self.max_slots):
            col = i % cols
            row = i // cols
            x   = ox + col * cell_size
            y   = oy + row * cell_size
            filled = i < len(self.steps)

            bg_color = (45, 85, 45) if filled else (32, 32, 32)
            pygame.draw.rect(screen, bg_color,
                             (x + 2, y + 2, cell_size - 4, cell_size - 4),
                             border_radius=5)

            if filled:
                sym  = _DIR_SYMBOL[self.steps[i]]
                surf = self._font.render(sym, True, (150, 230, 150))
                rect = surf.get_rect(
                    center=(x + cell_size // 2, y + cell_size // 2)
                )
                screen.blit(surf, rect)

        # Ayuda en la parte inferior
        if interactive:
            hints = [
                "Flechas: agregar paso",
                "Backspace: borrar último",
                "ESPACIO: ejecutar",
            ]
            hy = panel_y + panel_h - len(hints) * 18 - 8
            for line in hints:
                s = self._font_small.render(line, True, (90, 90, 90))
                screen.blit(s, (panel_x + 12, hy))
                hy += 18
