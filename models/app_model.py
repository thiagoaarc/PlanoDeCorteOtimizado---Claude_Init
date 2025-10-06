from __future__ import annotations

from dataclasses import replace
from typing import Iterable, List, Optional, Sequence
from PyQt6.QtCore import QObject, pyqtSignal

from models.chapa import Chapa
from models.peca import Peca
from models.layout import LayoutResult, OptimizationSummary


class AppModel(QObject):
    """Application state container with Qt signals for UI consumption."""

    inventory_changed = pyqtSignal()
    layout_changed = pyqtSignal()
    status_changed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._chapas: List[Chapa] = []
        self._pecas: List[Peca] = []
        self._layouts: List[LayoutResult] = []
        self._summary: Optional[OptimizationSummary] = None

    # ---------------------------------------------------------------------
    # Inventory management
    # ---------------------------------------------------------------------
    @property
    def chapas(self) -> Sequence[Chapa]:
        return tuple(self._chapas)

    def set_chapas(self, chapas: Iterable[Chapa]) -> None:
        self._chapas = list(chapas)
        self.inventory_changed.emit()

    def add_chapa(self, chapa: Chapa) -> None:
        self._chapas.append(chapa)
        self.inventory_changed.emit()

    def replace_chapa(self, index: int, updated: Chapa) -> None:
        self._chapas[index] = updated
        self.inventory_changed.emit()

    def remove_chapa(self, index: int) -> None:
        del self._chapas[index]
        self.inventory_changed.emit()

    @property
    def pecas(self) -> Sequence[Peca]:
        return tuple(self._pecas)

    def set_pecas(self, pecas: Iterable[Peca]) -> None:
        self._pecas = list(pecas)
        self.inventory_changed.emit()

    def add_peca(self, peca: Peca) -> None:
        self._pecas.append(peca)
        self.inventory_changed.emit()

    def replace_peca(self, index: int, updated: Peca) -> None:
        self._pecas[index] = updated
        self.inventory_changed.emit()

    def remove_peca(self, index: int) -> None:
        del self._pecas[index]
        self.inventory_changed.emit()

    # ---------------------------------------------------------------------
    # Layout state
    # ---------------------------------------------------------------------
    @property
    def layouts(self) -> Sequence[LayoutResult]:
        return tuple(self._layouts)

    def set_layouts(self, layouts: Iterable[LayoutResult], summary: Optional[OptimizationSummary] = None) -> None:
        self._layouts = list(layouts)
        self._summary = summary
        self.layout_changed.emit()

    def clear_layouts(self) -> None:
        self._layouts.clear()
        self._summary = None
        self.layout_changed.emit()

    @property
    def summary(self) -> Optional[OptimizationSummary]:
        return self._summary

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def clone_with_status(self, message: str) -> None:
        self.status_changed.emit(message)

    def has_inventory(self) -> bool:
        return bool(self._chapas) and bool(self._pecas)

    def total_chapa_area(self) -> float:
        return sum(chapa.area for chapa in self._chapas)

    def total_peca_area(self) -> float:
        return sum(peca.area * getattr(peca, "qtd", 1) for peca in self._pecas)
