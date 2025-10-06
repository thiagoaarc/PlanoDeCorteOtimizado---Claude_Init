from .chapas_tab import ChapasTab
from .pecas_tab import PecasTab
from .estrategia_tab import EstrategiaTab
from .editor_tab import EditorTab

__all__ = ['ChapasTab', 'PecasTab', 'EstrategiaTab', 'EditorTab']
    __all__ = ["ChapasTab", "PecasTab", "EstrategiaTab", "EditorTab"]
except ImportError as exc:  # pragma: no cover - fallback
    print(f"Erro ao importar modulos das tabs: {exc}")
    __all__ = []
