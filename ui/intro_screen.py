"""Pantalla introductoria que muestra el dato ambiental antes del nivel."""
import pygame

import settings


class IntroScreen:
    """Muestra el nombre del nivel y la trivia ambiental."""

    def __init__(self) -> None:
        pygame.font.init()
        self._font_name = pygame.font.SysFont(None, 72, bold=True)
        self._font_fact = pygame.font.SysFont(None, 36)
        self._font_hint = pygame.font.SysFont(None, 30)

    def draw(self, screen: pygame.Surface, level_name: str, fact: str) -> None:
        w, h = screen.get_size()

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        name_surf = self._font_name.render(level_name, True, (255, 255, 255))
        screen.blit(name_surf, name_surf.get_rect(center=(w // 2, h // 2 - 80)))

        lines = self._wrap_text(fact, self._font_fact, w - 200)
        y = h // 2 - 20
        for line in lines:
            fact_surf = self._font_fact.render(line, True, (180, 255, 180))
            screen.blit(fact_surf, fact_surf.get_rect(center=(w // 2, y)))
            y += 40

        hint_surf = self._font_hint.render(
            "Presiona ESPACIO para continuar", True, (180, 180, 180)
        )
        screen.blit(hint_surf, hint_surf.get_rect(center=(w // 2, h - 60)))

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
