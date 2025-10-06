from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from models.chapa import Chapa
    from models.peca import Peca


@dataclass
class Placement:
    """Represents a single piece placement over a sheet."""

    id: str
    chapa_id: str
    peca_id: str
    x: float
    y: float
    width: float
    height: float
    angle: float = 0.0
    rotation: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LayoutResult:
    """Aggregates all placements for a single sheet along with metrics."""

    chapa: "Chapa"
    placements: List[Placement] = field(default_factory=list)
    utilization: float = 0.0
    waste_area: float = 0.0
    notes: Optional[str] = None


@dataclass
class OptimizationSummary:
    """High-level summary of an optimization run."""

    algorithm: str
    total_utilization: float
    piece_coverage: float
    total_waste_area: float
    allocated_count: int
    not_allocated: List["Peca"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
