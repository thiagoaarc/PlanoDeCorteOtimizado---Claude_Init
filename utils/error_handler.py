from functools import wraps

from utils.logger import CustomLogger

logger = CustomLogger().logger


class OptimizationError(Exception):
    """Erro de negocio para a camada de otimizacao."""


def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as exc:
            logger.error("Erro de validacao em %s: %s", func.__name__, exc)
            raise OptimizationError(f"Erro de validacao: {exc}") from exc
        except Exception as exc:  # pragma: no cover - guarda-chuva defensivo
            logger.error("Erro inesperado em %s: %s", func.__name__, exc)
            raise OptimizationError(f"Erro inesperado: {exc}") from exc

    return wrapper
