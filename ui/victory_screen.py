"""Pantalla de victoria: estrellas, dato ambiental y botones."""
import math

import pygame

import settings


class VictoryScreen:
    def __init__(self) -> None:
        pygame.font.init()
        self._font_title  = pygame.font.SysFont(None, 72, bold=True)
        self._font_fact   = pygame.font.SysFont(None, 36)
        self._font_info   = pygame.font.SysFont(None, 30)
        self._font_button = pygame.font.SysFont(None, 40, bold=True)
        self._selected = 0

    def reset(self) -> None:
        self._selected = 0

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self._selected = 1 - self._selected
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                return "next" if self._selected == 0 else "retry"
        return None

    def draw(self, screen: pygame.Surface, level_name: str, fact: str,
             steps: int, max_slots: int) -> None:
        w, h = screen.get_size()

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        title_surf = self._font_title.render("¡Victoria!", True, (80, 220, 80))
        screen.blit(title_surf, title_surf.get_rect(center=(w // 2, h // 2 - 120)))

        name_surf = self._font_info.render(level_name, True, (220, 220, 220))
        screen.blit(name_surf, name_surf.get_rect(center=(w // 2, h // 2 - 70)))

        stars_count = self._calculate_stars(steps, max_slots)
        self._draw_stars(screen, w // 2, h // 2 - 5, stars_count)

        info_surf = self._font_info.render(
            f"Pasos usados: {steps}  /  {max_slots}", True, (180, 180, 180)
        )
        screen.blit(info_surf, info_surf.get_rect(center=(w // 2, h // 2 + 40)))

        lines = self._wrap_text(fact, self._font_fact, w - 200)
        y = h // 2 + 80
        for line in lines:
            fact_surf = self._font_fact.render(line, True, (180, 255, 180))
            screen.blit(fact_surf, fact_surf.get_rect(center=(w // 2, y)))
            y += 40

        buttons = ["Siguiente nivel", "Reintentar"]
        btn_w = 220
        gap = 40
        total_w = btn_w * 2 + gap
        bx = (w - total_w) // 2
        by = h - 90
        for i, label in enumerate(buttons):
            color = (50, 200, 80) if i == self._selected else (140, 140, 140)
            label_surf = self._font_button.render(label, True, color)
            lx = bx + i * (btn_w + gap)
            screen.blit(label_surf, label_surf.get_rect(center=(lx + btn_w // 2, by)))

    # ------------------------------------------------------------------
    # Estrellas dibujadas con pygame.draw (evita Unicode mal renderizado)
    # ------------------------------------------------------------------

    @staticmethod
    def _star_points(cx: float, cy: float, outer_r: float) -> list[tuple[float, float]]:
        inner_r = outer_r * 0.4
        pts: list[tuple[float, float]] = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            r = outer_r if i % 2 == 0 else inner_r
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        return pts

    def _draw_stars(self, screen: pygame.Surface, cx: int, cy: int,
                    count: int) -> None:
        r = 22
        gap = r * 3
        start_x = cx - gap
        for i in range(3):
            x = start_x + i * gap
            color = (255, 220, 50) if i < count else (80, 80, 80)
            pts = self._star_points(x, cy, r)
            pygame.draw.polygon(screen, color, pts)

    @staticmethod
    def _calculate_stars(steps: int, max_slots: int) -> int:
        ratio = steps / max_slots
        if ratio <= 0.7:
            return 3
        elif ratio <= 1.0:
            return 2
        return 1

    @staticmethod
    def _wrap_text(text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if font.size(test)[0] > max_width and current:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)
        return lines
