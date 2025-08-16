import logging

from .settings import settings

logging.basicConfig(level=settings.log_level)
LOGGER = logging.getLogger("calm_calatheas")
