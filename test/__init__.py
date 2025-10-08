import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

try:
    import pygame
    from unittest.mock import MagicMock

    try:
        pygame.display.init()
    except Exception:
        pass

    pygame.display.set_mode = MagicMock(side_effect=lambda *a, **k: pygame.Surface((1, 1)))
    pygame.display.set_caption = MagicMock()
    pygame.display.set_icon = MagicMock()
    pygame.display.update = MagicMock()
    pygame.display.flip = MagicMock()

    if hasattr(pygame, "mixer"):
        pygame.mixer.init = MagicMock()
        pygame.mixer.get_init = MagicMock(return_value=True)

    pygame.time.Clock = MagicMock(return_value=MagicMock(tick=MagicMock(return_value=16)))
except Exception:
    pass