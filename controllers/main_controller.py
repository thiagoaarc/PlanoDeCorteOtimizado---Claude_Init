from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from models.app_model import AppModel
from services.data_service import DataService

from data.version_control import VersionControl
from models import Chapa, Defeito, LayoutResult, OptimizationSummary, Peca
from services.export import export_to_pdf
from services.export_svg import export_to_svg
from services.optimization import AVAILABLE_ALGORITHMS, evaluate_algorithms, run_algorithm
from utils.logger import CustomLogger


class MainController(QObject):
    """Coordinates actions between the UI, model and domain services."""

    error_occurred = pyqtSignal(str)

    def __init__(self, model: AppModel, data_service: DataService) -> None:
        super().__init__()
        self.model = model
        self.data_service = data_service
        self._version_control = VersionControl()
        self._logger = CustomLogger().logger
        self._last_summary: Optional[OptimizationSummary] = None
        self._connect_signals()

    def _connect_signals(self):
        self.model.error_occurred.connect(self.error_occurred)

    # ------------------------------------------------------------------
    # Inventory management
    # ------------------------------------------------------------------
    def add_chapa(self, data: Dict[str, float | str | int]) -> None:
        chapa = self._build_chapa(data)
        self.model.add_chapa(chapa)
        self.model.clone_with_status(f"Sheet '{chapa.id}' added")

    def add_peca(self, data: Dict[str, object]) -> None:
        peca = self._build_peca(data)
        self.model.add_peca(peca)
        self.model.clone_with_status(f"Piece '{peca.id}' added")

    def remove_chapa(self, index: int) -> None:
        if 0 <= index < len(self.model.chapas):
            chapa = self.model.chapas[index]
            self.model.remove_chapa(index)
            self.model.clone_with_status(f"Sheet '{chapa.id}' removed")

    def remove_peca(self, index: int) -> None:
        if 0 <= index < len(self.model.pecas):
            peca = self.model.pecas[index]
            self.model.remove_peca(index)
            self.model.clone_with_status(f"Piece '{peca.id}' removed")

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save_inventory(self, destination: Optional[str | Path] = None) -> Path:
        data = {
            "chapas": [self._chapa_to_dict(chapa) for chapa in self.model.chapas],
            "pecas": [self._peca_to_dict(peca) for peca in self.model.pecas],
        }
        target = self.data_service.save_inventory(data, destination)
        try:
            self._version_control.save_version(data, description=str(Path(target).name))
        except Exception as exc:  # pragma: no cover - controle auxiliar
            self._logger.warning("Falha ao registrar versao: %s", exc)
        return target

    def load_inventory(self, source: Optional[str | Path] = None) -> None:
        payload = self.data_service.load_inventory(source)
        chapas = [self._build_chapa(item) for item in payload.get("chapas", [])]
        pecas = [self._build_peca(item) for item in payload.get("pecas", [])]
        self.model.set_chapas(chapas)
        self.model.set_pecas(pecas)
        self.model.clone_with_status("Inventory loaded")

    # ------------------------------------------------------------------
    # Optimization
    # ------------------------------------------------------------------
    def get_algorithms(self) -> List[Dict[str, str]]:
        return AVAILABLE_ALGORITHMS

    def optimize(self, algorithm_key: str, kerf: float = 0.0, margin: float = 0.0,\n                 allow_rotation: bool = True, priority_weight: float = 0.0) -> None:
        try:
            if not self.model.chapas or not self.model.pecas:
                self.model.clone_with_status("Add sheets and pieces before running optimization")
                return
            summary, layouts = run_algorithm(\n                algorithm_key,\n                self.model.chapas,\n                self.model.pecas,\n                allow_rotation=allow_rotation,\n                kerf=kerf,\n                margin=margin,\n                priority_weight=priority_weight,\n            )
            self._last_summary = summary
            self.model.set_layouts(layouts, summary)
            self.model.clone_with_status(
                f"Optimization completed using {algorithm_key.upper()} | "
                f"Utilization {summary.total_utilization:.1f}% | Coverage {summary.piece_coverage:.1f}%"
            )
        except Exception as e:
            self.error_occurred.emit(f"Erro na otimização: {str(e)}")

    def evaluate_best(self, kerf: float = 0.0, margin: float = 0.0,\n                      allow_rotation: bool = True, priority_weight: float = 0.0) -> Optional[OptimizationSummary]:
        rankings = evaluate_algorithms(\n            self.model.chapas,\n            self.model.pecas,\n            allow_rotation=allow_rotation,\n            kerf=kerf,\n            margin=margin,\n            priority_weight=priority_weight,\n        )
        best = rankings[0] if rankings else None
        if best:
            self.model.clone_with_status(
                f"Best strategy {best.algorithm.upper()} | "
                f"Utilization {best.total_utilization:.1f}% | Coverage {best.piece_coverage:.1f}%"
            )
            self.optimize(\n                best.algorithm,\n                kerf=kerf,\n                margin=margin,\n                allow_rotation=allow_rotation,\n                priority_weight=priority_weight,\n            )
        return best
    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------
    def export_pdf(self, destination: str | Path) -> bool:
        if not self.model.layouts:
            self.model.clone_with_status("No layouts to export")
            return False
        success = export_to_pdf(self.model.layouts, filename=str(destination))
        if success:
            self.model.clone_with_status(f"PDF exported to {destination}")
        else:
            self.model.clone_with_status("Failed to export PDF")
        return success
    def export_svg(self, destination: str | Path) -> bool:
        if not self.model.layouts:
            self.model.clone_with_status("No layouts to export")
            return False
        success = export_to_svg(self.model.layouts, filename=str(destination))
        if success:
            self.model.clone_with_status(f"SVG exported to {destination}")
        else:
            self.model.clone_with_status("Failed to export SVG")
        return success
    # ------------------------------------------------------------------
    # Accessors for the UI
    # ------------------------------------------------------------------
    def get_layouts(self) -> List[LayoutResult]:\n        return list(self.model.layouts)\n\n    def get_summary(self) -> Optional[OptimizationSummary]:\n        return self._last_summary or self.model.summary\n\n    def get_not_allocated(self) -> List[Peca]:\n        summary = self.get_summary()\n        return list(summary.not_allocated) if summary else []

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------
    def _build_chapa(self, data: Dict[str, object]) -> Chapa:
        defeitos_data = data.get("defeitos", [])
        defeitos: List[Defeito] = []
        for item in defeitos_data:
            if isinstance(item, Defeito):
                defeitos.append(item)
            elif isinstance(item, dict):
                defeitos.append(Defeito(tipo=str(item.get("tipo", "rect")), params=item.get("params", {})))
        return Chapa(
            id=str(data.get("id", "")),
            w=float(data.get("w") or data.get("width") or 0),
            h=float(data.get("h") or data.get("height") or 0),
            qtd=int(data.get("qtd") or data.get("quantity") or 1),
            rebarba=float(data.get("rebarba", 0) or 0),
            custo=float(data.get("custo", 0) or 0),
            defeitos=defeitos,
            cliente=str(data.get("cliente", "")),
            lote=str(data.get("lote", "")),
            cor=str(data.get("cor", "")),
            obs=str(data.get("obs", "")),
        )

    def _build_peca(self, data: Dict[str, object]) -> Peca:
        params = data.get("params")
        if not isinstance(params, dict):
            params = {
                "w": float(data.get("w", 0) or data.get("width", 0)),
                "h": float(data.get("h", 0) or data.get("height", 0)),
            }
        return Peca(
            id=str(data.get("id", "")),
            shape=str(data.get("shape", "rect")),
            params=params,
            qtd=int(data.get("qtd") or data.get("quantity") or 1),
            prioridade=int(data.get("prioridade", 0) or 0),
            cliente=str(data.get("cliente", "")),
            lote=str(data.get("lote", "")),
            cor=str(data.get("cor", "")),
            obs=str(data.get("obs", "")),
        )

    def _peca_to_dict(self, peca: Peca) -> Dict[str, object]:
        return {
            "id": peca.id,
            "shape": peca.shape,
            "params": peca.params,
            "qtd": peca.qtd,
            "prioridade": peca.prioridade,
            "cliente": peca.cliente,
            "lote": peca.lote,
            "cor": peca.cor,
            "obs": peca.obs,
        }

    def _chapa_to_dict(self, chapa: Chapa) -> Dict[str, object]:
        return {
            "id": chapa.id,
            "w": chapa.w,
            "h": chapa.h,
            "qtd": chapa.qtd,
            "rebarba": chapa.rebarba,
            "custo": chapa.custo,
            "defeitos": [
                {"tipo": defeito.tipo, "params": defeito.params}
                for defeito in getattr(chapa, "defeitos", [])
            ],
            "cliente": chapa.cliente,
            "lote": chapa.lote,
            "cor": chapa.cor,
            "obs": chapa.obs,
        }
















