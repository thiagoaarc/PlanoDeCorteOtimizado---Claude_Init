from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal


class DataService(QObject):
    """Handles persistence of inventory, layouts and automatic backups."""

    error_occurred = pyqtSignal(str)

    def __init__(self, data_dir: str | Path = "data") -> None:
        super().__init__()
        self.data_dir = Path(data_dir)
        self.backup_dir = self.data_dir / "backups"
        self.default_filename = "inventory.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Inventory persistence
    # ------------------------------------------------------------------
    def save_inventory(self, data: Dict[str, Any], destination: Optional[str | Path] = None) -> Path:
        try:
            target = self._resolve_target(destination)
            if target.exists():
                self._create_backup(target)
            with target.open("w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, ensure_ascii=False)
            return target
        except Exception as exc:  # pragma: no cover - defensive
            message = f"Failed to save inventory: {exc}"
            self.error_occurred.emit(message)
            raise

    def load_inventory(self, source: Optional[str | Path] = None) -> Dict[str, Any]:
        try:
            target = self._resolve_target(source)
            with target.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError as exc:
            message = f"Inventory not found: {exc}"
            self.error_occurred.emit(message)
            raise
        except Exception as exc:  # pragma: no cover - defensive
            message = f"Failed to load inventory: {exc}"
            self.error_occurred.emit(message)
            raise

    def list_inventories(self) -> List[Path]:
        files = sorted(self.data_dir.glob("*.json"))
        return [path for path in files if path.name != self.default_filename]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _resolve_target(self, candidate: Optional[str | Path]) -> Path:
        if candidate is None:
            return self.data_dir / self.default_filename
        candidate_path = Path(candidate)
        if candidate_path.is_dir():
            candidate_path = candidate_path / self.default_filename
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        return candidate_path

    def _create_backup(self, source: Path) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{source.stem}_{timestamp}{source.suffix}.bak"
        target = self.backup_dir / backup_name
        target.write_bytes(source.read_bytes())

