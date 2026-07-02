"""HUD: temporizador, lista de objetivos e indicador de slots durante el juego."""
import pygame

_OBJ_LABELS: dict[str, str] = {
    "PLANT_TREE":    "Plantar arbol",
    "COLLECT_TRASH": "Recoger basura",
}

PANEL_X = 10
PANEL_Y = 10
PANEL_W = 220


def _obj_done(obj: dict, grid: list[list[str]]) -> bool:
    col, row, t = obj["col"], obj["row"], obj.get("type")
    cell = grid[row][col]
    return (t == "PLANT_TREE" and cell == "TREE") or \
           (t == "COLLECT_TRASH" and cell == "FLOOR")


class HUD:
    def __init__(self) -> None:
        pygame.font.init()
        self._font_title = pygame.font.SysFont(None, 28, bold=True)
        self._font_body  = pygame.font.SysFont(None, 24)
        self._font_timer = pygame.font.SysFont(None, 70, bold=True)

    # ------------------------------------------------------------------
    # Pantalla de planificación
    # ------------------------------------------------------------------

    def draw_planning(self, screen: pygame.Surface, level) -> None:
        """Panel izquierdo en STATE_PLANNING: objetivos + max_slots."""
        n = len(level.objectives)
        h = 16 + 26 + n * 26 + 10 + 1 + 10 + 22 + 10
        self._bg(screen, h)

        x, y = PANEL_X + 10, PANEL_Y + 10
        y = self._title(screen, x, y, "Objetivos")
        for obj in level.objectives:
            y = self._obj_row(screen, x, y, obj, level.grid, done_override=False)

        y += 4
        pygame.draw.line(screen, (55, 55, 55), (x, y), (x + PANEL_W - 20, y))
        y += 8

        slots_surf = self._font_body.render(
            f"Pasos disponibles: {level.max_slots}", True, (120, 120, 120)
        )
        screen.blit(slots_surf, (x, y))

    # ------------------------------------------------------------------
    # Pantalla de ejecución (también ACTION_PROMPT)
    # ------------------------------------------------------------------

    def draw_running(self, screen: pygame.Surface, level,
                     time_remaining: float) -> None:
        """Panel izquierdo en STATE_RUNNING / ACTION_PROMPT."""
        has_timer = level.time_limit > 0
        n = len(level.objectives)
        timer_h = 68 + 16 if has_timer else 0
        h = timer_h + 16 + 26 + n * 26 + 10
        self._bg(screen, h)

        x, y = PANEL_X + 10, PANEL_Y + 10

        if has_timer:
            y = self._timer(screen, x, y, time_remaining, level.time_limit)
            y += 8

        y = self._title(screen, x, y, "Objetivos")
        for obj in level.objectives:
            y = self._obj_row(screen, x, y, obj, level.grid)

    # ------------------------------------------------------------------
    # Primitivas internas
    # ------------------------------------------------------------------

    def _bg(self, screen: pygame.Surface, height: int) -> None:
        bg = pygame.Surface((PANEL_W, height), pygame.SRCALPHA)
        bg.fill((10, 10, 10, 190))
        screen.blit(bg, (PANEL_X, PANEL_Y))

    def _title(self, screen: pygame.Surface, x: int, y: int,
               text: str) -> int:
        surf = self._font_title.render(text, True, (200, 200, 200))
        screen.blit(surf, (x, y))
        return y + surf.get_height() + 4

    def _obj_row(self, screen: pygame.Surface, x: int, y: int,
                 obj: dict, grid: list[list[str]],
                 done_override: bool | None = None) -> int:
        done  = _obj_done(obj, grid) if done_override is None else done_override
        color = (75, 210, 75) if done else (180, 180, 180)
        label = _OBJ_LABELS.get(obj.get("type", ""), obj.get("type", ""))

        cy = y + 9
        if done:
            pygame.draw.circle(screen, color, (x + 5, cy), 5)
        else:
            pygame.draw.circle(screen, color, (x + 5, cy), 5, 1)

        surf = self._font_body.render(label, True, color)
        screen.blit(surf, (x + 16, y))
        return y + 26

    def _timer(self, screen: pygame.Surface, x: int, y: int,
               remaining: float, total: int) -> int:
        ratio = remaining / total if total > 0 else 0
        color = (75, 210, 75) if ratio > 0.5 else \
                (255, 200, 50) if ratio > 0.25 else (255, 75, 75)

        secs_surf = self._font_timer.render(f"{int(remaining)}s", True, color)
        cx = PANEL_X + PANEL_W // 2
        screen.blit(secs_surf, secs_surf.get_rect(centerx=cx, y=y))
        y += secs_surf.get_height() + 4

        bar_w = PANEL_W - 20
        pygame.draw.rect(screen, (45, 45, 45), (x, y, bar_w, 8), border_radius=4)
        fill = max(0, int(bar_w * ratio))
        if fill:
            pygame.draw.rect(screen, color, (x, y, fill, 8), border_radius=4)
        return y + 8 + 8
