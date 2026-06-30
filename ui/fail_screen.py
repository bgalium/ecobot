"""Pantalla de derrota: mensaje según causa y botón reintentar."""
import pygame

import settings


REASON_MESSAGES = {
    "WALL":    "El robot chocó contra un obstáculo.",
    "FELL":    "El robot cayó fuera del mapa.",
    "TIMEOUT": "¡Se acabó el tiempo! No completaste los objetivos a tiempo.",
}


class FailScreen:
    def __init__(self) -> None:
        pygame.font.init()
        self._font_title  = pygame.font.SysFont(None, 72, bold=True)
        self._font_reason = pygame.font.SysFont(None, 36)
        self._font_button = pygame.font.SysFont(None, 40, bold=True)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                return "retry"
        return None

    def draw(self, screen: pygame.Surface, reason: str) -> None:
        w, h = screen.get_size()

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        title_surf = self._font_title.render("Fallaste", True, (220, 60, 60))
        screen.blit(title_surf, title_surf.get_rect(center=(w // 2, h // 2 - 60)))

        msg = REASON_MESSAGES.get(reason, "No se completaron todos los objetivos.")
        reason_surf = self._font_reason.render(msg, True, (220, 220, 220))
        screen.blit(reason_surf, reason_surf.get_rect(center=(w // 2, h // 2 + 10)))

        btn_surf = self._font_button.render("Reintentar", True, (220, 80, 80))
        screen.blit(btn_surf, btn_surf.get_rect(center=(w // 2, h - 90)))
