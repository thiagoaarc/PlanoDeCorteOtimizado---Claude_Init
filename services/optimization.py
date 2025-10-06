from __future__ import annotations

import copy
import logging
import math
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from models.chapa import Chapa
from models.peca import Peca
from models.layout import LayoutResult, OptimizationSummary, Placement

logger = logging.getLogger(__name__)

Bounds = Tuple[float, float, float, float]


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------
def validate_dimensions(value: float, name: str) -> float:
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{name} must be a positive number")
    return float(value)


# ---------------------------------------------------------------------------
# Inventory expansion helpers
# ---------------------------------------------------------------------------
def expandir_pecas_por_qtd(pecas: Sequence[Peca]) -> List[Peca]:
    expanded: List[Peca] = []
    for peca in pecas:
        qty = getattr(peca, "qtd", 1)
        for index in range(qty):
            new_piece = copy.deepcopy(peca)
            if qty > 1:
                new_piece.id = f"{peca.id}_{index + 1}"
            new_piece.qtd = 1
            setattr(new_piece, "_expanded", True)
            expanded.append(new_piece)
    return expanded


def expandir_chapas_por_qtd(chapas: Sequence[Chapa]) -> List[Chapa]:
    expanded: List[Chapa] = []
    for chapa in chapas:
        qty = getattr(chapa, "qtd", 1)
        for index in range(qty):
            new_sheet = copy.deepcopy(chapa)
            if qty > 1:
                new_sheet.id = f"{chapa.id}_{index + 1}"
            new_sheet.qtd = 1
            setattr(new_sheet, "_expanded", True)
            expanded.append(new_sheet)
    return expanded


def _ensure_expanded_chapas(chapas: Sequence[Chapa]) -> List[Chapa]:
    if chapas and all(getattr(chapa, '_expanded', False) for chapa in chapas):
        return list(chapas)
    return expandir_chapas_por_qtd(chapas)


def _ensure_expanded_pecas(pecas: Sequence[Peca]) -> List[Peca]:
    if pecas and all(getattr(peca, '_expanded', False) for peca in pecas):
        return list(pecas)
    return expandir_pecas_por_qtd(pecas)


def _sort_pieces(pecas: Sequence[Peca], priority_weight: float) -> List[Peca]:

def _resolve_priority_weight(algorithm_key: str, base_weight: float, overrides: Optional[Dict[str, float]]) -> float:
    if overrides and algorithm_key in overrides:
        override_weight = overrides[algorithm_key]
        return max(0.0, override_weight)

    if base_weight <= 0:
        return 0.0

    for entry in AVAILABLE_ALGORITHMS:
        if entry['key'] == algorithm_key:
            factor = entry.get('priority_factor', 1.0)
            return max(0.0, base_weight * factor)
    return max(0.0, base_weight)

    weight = max(0.0, priority_weight)

    def sort_key(piece: Peca):
        prioridade = getattr(piece, 'prioridade', 0)
        return (-prioridade * weight, -calc_area(piece))

    return sorted(pecas, key=sort_key)
# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def overlaps(rect1: Bounds, rect2: Bounds) -> bool:
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)


def inside(rect: Bounds, chapa_w: float, chapa_h: float, defeitos: Iterable[dict] | None = None,
           kerf: float = 0.0, margin: float = 0.0) -> bool:
    x, y, w, h = rect
    safety_margin = max(0.0, margin)
    x_min = -safety_margin
    y_min = -safety_margin
    x_max = chapa_w + safety_margin
    y_max = chapa_h + safety_margin
    if x < x_min or y < y_min or x + w > x_max or y + h > y_max:
        return False
    for defect in defeitos or []:
        if defect.get("tipo") != "rect":
            continue
        params = defect.get("params", {})
        dx = params.get("x", 0.0)
        dy = params.get("y", 0.0)
        dw = params.get("w", 0.0)
        dh = params.get("h", 0.0)
        if overlaps(rect, (dx, dy, dw, dh)):
            return False
    return True


def bounding_box(peca: Peca, allow_rotation: bool) -> List[Tuple[float, float, float]]:
    shape = getattr(peca, "shape", "rect")
    params = getattr(peca, "params", {})
    results: List[Tuple[float, float, float]] = []
    if shape == "rect":
        w = params.get("w", 1.0)
        h = params.get("h", 1.0)
        results.append((w, h, 0.0))
        if allow_rotation and w != h:
            results.append((h, w, 90.0))
    elif shape == "circ":
        r = params.get("raio", params.get("r", 0.0))
        d = 2 * r
        results.append((d, d, 0.0))
    elif shape == "poly":
        n = max(int(params.get("n", 3)), 3)
        lado = params.get("lado", 1.0)
        radius = lado / (2 * math.sin(math.pi / n))
        d = 2 * radius
        results.append((d, d, 0.0))
    else:
        w = params.get("w", 1.0)
        h = params.get("h", 1.0)
        results.append((w, h, 0.0))
    return results


# ---------------------------------------------------------------------------
# Heuristic algorithms
# ---------------------------------------------------------------------------
def ffd_packing(chapas: Sequence[Chapa], pecas: Sequence[Peca], *, allow_rotation: bool = True,\n                kerf: float = 0.0, margin: float = 0.0, priority_weight: float = 0.0) -> Tuple[List[List[dict]], List[Peca]]:
    chapas = _ensure_expanded_chapas(chapas)
    pecas = _ensure_expanded_pecas(pecas)
    layouts: List[List[dict]] = [[] for _ in chapas]
    unplaced: List[Peca] = []
    kerf = float(max(0.0, kerf))

    ordered_pieces = _sort_pieces(pecas, priority_weight)

    for piece in ordered_pieces:
        placed = False
        for index, chapa in enumerate(chapas):
            occupied = [(item['x'], item['y'], item['w'] + kerf, item['h'] + kerf)
                        for item in layouts[index]]
            defects = _normalize_defects(chapa)
            shapes = bounding_box(piece, allow_rotation)
            for width, height, angle in shapes:
                width_k = width + kerf
                height_k = height + kerf
                step = max(1.0, min(5.0, width_k / 4, height_k / 4))
                y = 0.0
                while y <= chapa.h - height_k + 1e-6:
                    x = 0.0
                    while x <= chapa.w - width_k + 1e-6:
                        rect = (x, y, width_k, height_k)
                        if not inside(rect, chapa.w, chapa.h, defects, kerf, margin):
                            x += step
                            continue
                        if all(not overlaps(rect, occ) for occ in occupied):
                            layouts[index].append({
                                "id": piece.id,
                                "x": x,
                                "y": y,
                                "w": width,
                                "h": height,
                                "angulo": angle,
                                "peca": piece,
                            })
                            placed = True
                            break
                        x += step
                    if placed:
                        break
                    y += step
                if placed:
                    break
            if placed:
                break
        if not placed:
            unplaced.append(piece)
    return layouts, unplaced


def guillotine_packing(chapas: Sequence[Chapa], pecas: Sequence[Peca], *, allow_rotation: bool = True,\n                       kerf: float = 0.0, margin: float = 0.0, priority_weight: float = 0.0) -> Tuple[List[List[dict]], List[Peca]]:
    chapas = _ensure_expanded_chapas(chapas)
    pecas = _ensure_expanded_pecas(pecas)
    layouts: List[List[dict]] = [[] for _ in chapas]
    remaining: List[Peca] = []

    for sheet_index, chapa in enumerate(chapas):
        free_rects: List[Bounds] = [(0.0, 0.0, chapa.w, chapa.h)]
        placed_rects: List[Bounds] = []
        defects = _normalize_defects(chapa)
        pieces_to_place = [piece for piece in pecas if not getattr(piece, "_placed", False)]
        for piece in _sort_pieces(pieces_to_place, priority_weight):
            placed = False
            for width, height, angle in bounding_box(piece, allow_rotation):
                width_k = width + kerf
                height_k = height + kerf
                for rect_index, (fx, fy, fw, fh) in enumerate(list(free_rects)):
                    if width_k <= fw and height_k <= fh:
                        candidate = (fx, fy, width_k, height_k)
                        if not inside(candidate, chapa.w, chapa.h, defects, kerf, margin):
                            continue
                        if any(overlaps(candidate, occ) for occ in placed_rects):
                            continue
                        layouts[sheet_index].append({
                            "id": piece.id,
                            "x": fx,
                            "y": fy,
                            "w": width,
                            "h": height,
                            "angulo": angle,
                            "peca": piece,
                        })
                        placed_rects.append(candidate)
                        piece._placed = True
                        placed = True
                        right_rect = (fx + width_k, fy, fw - width_k, height_k)
                        top_rect = (fx, fy + height_k, fw, fh - height_k)
                        del free_rects[rect_index]
                        if right_rect[2] > 0 and right_rect[3] > 0:
                            free_rects.append(right_rect)
                        if top_rect[2] > 0 and top_rect[3] > 0:
                            free_rects.append(top_rect)
                        break
                if placed:
                    break
            if not placed:
                remaining.append(piece)
        for piece in pecas:
            if hasattr(piece, "_placed"):
                delattr(piece, "_placed")
    return layouts, remaining


def skyline_packing(chapas: Sequence[Chapa], pecas: Sequence[Peca], *, allow_rotation: bool = True,\n                    kerf: float = 0.0, margin: float = 0.0, priority_weight: float = 0.0) -> Tuple[List[List[dict]], List[Peca]]:
    chapas = _ensure_expanded_chapas(chapas)
    pecas = _ensure_expanded_pecas(pecas)
    layouts: List[List[dict]] = [[] for _ in chapas]
    unplaced: List[Peca] = []

    for sheet_index, chapa in enumerate(chapas):
        skyline: List[Tuple[float, float, float]] = [(0.0, 0.0, chapa.w)]
        placed_rects: List[Bounds] = []
        defects = _normalize_defects(chapa)
        pieces_to_place = [piece for piece in pecas if not getattr(piece, "_placed", False)]
        for piece in _sort_pieces(pieces_to_place, priority_weight):
            placed = False
            for width, height, angle in bounding_box(piece, allow_rotation):
                width_k = width + kerf
                height_k = height + kerf
                for x0, y0, available_width in list(skyline):
                    if width_k > available_width or y0 + height_k > chapa.h:
                        continue
                    candidate = (x0, y0, width_k, height_k)
                    if not inside(candidate, chapa.w, chapa.h, defects, kerf, margin):
                        continue
                    if any(overlaps(candidate, occ) for occ in placed_rects):
                        continue
                    layouts[sheet_index].append({
                        "id": piece.id,
                        "x": x0,
                        "y": y0,
                        "w": width,
                        "h": height,
                        "angulo": angle,
                        "peca": piece,
                    })
                    placed_rects.append(candidate)
                    piece._placed = True
                    placed = True
                    new_height = y0 + height_k
                    skyline.remove((x0, y0, available_width))
                    if available_width - width_k > 0:
                        skyline.append((x0 + width_k, y0, available_width - width_k))
                    skyline.append((x0, new_height, width_k))
                    break
                if placed:
                    break
            if not placed:
                unplaced.append(piece)
        for piece in pecas:
            if hasattr(piece, "_placed"):
                delattr(piece, "_placed")
    return layouts, unplaced


def shelf_packing(chapas: Sequence[Chapa], pecas: Sequence[Peca], *, allow_rotation: bool = True,\n                  kerf: float = 0.0, margin: float = 0.0, priority_weight: float = 0.0) -> Tuple[List[List[dict]], List[Peca]]:
    chapas = _ensure_expanded_chapas(chapas)
    pecas = _ensure_expanded_pecas(pecas)
    layouts: List[List[dict]] = [[] for _ in chapas]
    unplaced: List[Peca] = []

    for sheet_index, chapa in enumerate(chapas):
        x_cursor = 0.0
        y_cursor = 0.0
        shelf_height = 0.0
        placed_rects: List[Bounds] = []
        defects = _normalize_defects(chapa)
        pieces_to_place = [piece for piece in pecas if not getattr(piece, "_placed", False)]
        for piece in _sort_pieces(pieces_to_place, priority_weight):
            placed = False
            for width, height, angle in bounding_box(piece, allow_rotation):
                width_k = width + kerf
                height_k = height + kerf
                if x_cursor + width_k > chapa.w:
                    y_cursor += shelf_height
                    x_cursor = 0.0
                    shelf_height = 0.0
                if y_cursor + height_k > chapa.h:
                    continue
                candidate = (x_cursor, y_cursor, width_k, height_k)
                if not inside(candidate, chapa.w, chapa.h, defects, kerf, margin):
                    continue
                if any(overlaps(candidate, occ) for occ in placed_rects):
                    continue
                layouts[sheet_index].append({
                    "id": piece.id,
                    "x": x_cursor,
                    "y": y_cursor,
                    "w": width,
                    "h": height,
                    "angulo": angle,
                    "peca": piece,
                })
                placed_rects.append(candidate)
                piece._placed = True
                placed = True
                x_cursor += width_k
                shelf_height = max(shelf_height, height_k)
                break
            if not placed:
                unplaced.append(piece)
        for piece in pecas:
            if hasattr(piece, "_placed"):
                delattr(piece, "_placed")
    return layouts, unplaced


def maxrects_packing(chapas: Sequence[Chapa], pecas: Sequence[Peca], *, allow_rotation: bool = True,\n                      kerf: float = 0.0, margin: float = 0.0, priority_weight: float = 0.0) -> Tuple[List[List[dict]], List[Peca]]:
    chapas = _ensure_expanded_chapas(chapas)
    pecas = _ensure_expanded_pecas(pecas)
    layouts: List[List[dict]] = [[] for _ in chapas]
    unplaced: List[Peca] = []

    for sheet_index, chapa in enumerate(chapas):
        free_rects: List[Bounds] = [(0.0, 0.0, chapa.w, chapa.h)]
        placed: List[Bounds] = []
        defects = _normalize_defects(chapa)
        pieces_to_place = [piece for piece in pecas if not getattr(piece, "_placed", False)]
        for piece in _sort_pieces(pieces_to_place, priority_weight):
            layout_done = False
            free_rects.sort(key=lambda rect: -(rect[2] * rect[3]))
            for width, height, angle in bounding_box(piece, allow_rotation):
                width_k = width + kerf
                height_k = height + kerf
                for rect_index, (fx, fy, fw, fh) in enumerate(free_rects):
                    if width_k <= fw and height_k <= fh:
                        candidate = (fx, fy, width_k, height_k)
                        if not inside(candidate, chapa.w, chapa.h, defects, kerf, margin):
                            continue
                        if any(overlaps(candidate, occ) for occ in placed):
                            continue
                        layouts[sheet_index].append({
                            "id": piece.id,
                            "x": fx,
                            "y": fy,
                            "w": width,
                            "h": height,
                            "angulo": angle,
                            "peca": piece,
                        })
                        placed.append(candidate)
                        piece._placed = True
                        layout_done = True
                        right = (fx + width_k, fy, fw - width_k, height_k)
                        top = (fx, fy + height_k, fw, fh - height_k)
                        del free_rects[rect_index]
                        if right[2] > 0 and right[3] > 0:
                            free_rects.append(right)
                        if top[2] > 0 and top[3] > 0:
                            free_rects.append(top)
                        break
                if layout_done:
                    break
            if not layout_done:
                unplaced.append(piece)
        for piece in pecas:
            if hasattr(piece, "_placed"):
                delattr(piece, "_placed")
    return layouts, unplaced


ALGORITHM_FUNCTIONS: Dict[str, Callable[..., Tuple[List[List[dict]], List[Peca]]]] = {
    "ffd": ffd_packing,
    "guillotine": guillotine_packing,
    "skyline": skyline_packing,
    "shelf": shelf_packing,
    "maxrects": maxrects_packing,
}

AVAILABLE_ALGORITHMS: List[Dict[str, str]] = [
    {"key": "ffd", "label": "First Fit Decreasing", "description": "Greedy placement ordered by area", "priority_factor": 1.2},
    {"key": "guillotine", "label": "Guillotine", "description": "Recursive partition ensuring guillotine cuts", "priority_factor": 1.0},
    {"key": "skyline", "label": "Skyline", "description": "Shelf skyline packing ideal for varied widths", "priority_factor": 0.9},
    {"key": "shelf", "label": "Shelf", "description": "Simple horizontal shelf stacking", "priority_factor": 0.7},
    {"key": "maxrects", "label": "MaxRects", "description": "Maximal rectangle subdivision", "priority_factor": 1.4},
]


# ---------------------------------------------------------------------------
# Public orchestrators
# ---------------------------------------------------------------------------
def run_algorithm(algorithm_key: str, chapas: Sequence[Chapa], pecas: Sequence[Peca], *,
                  allow_rotation: bool = True, kerf: float = 0.0, margin: float = 0.0) -> Tuple[OptimizationSummary, List[LayoutResult]]:
    algorithm = ALGORITHM_FUNCTIONS.get(algorithm_key)
    if algorithm is None:
        raise ValueError(f"Unknown algorithm '{algorithm_key}'")

    expanded_chapas = expandir_chapas_por_qtd(chapas)
    expanded_pecas = expandir_pecas_por_qtd(pecas)

    layouts_raw, not_allocated = algorithm(
        copy.deepcopy(expanded_chapas),
        copy.deepcopy(expanded_pecas),
        allow_rotation=allow_rotation,
        kerf=kerf,
        margin=margin,
    )

    layout_results = _convert_to_layout_results(expanded_chapas, layouts_raw)

    allocated_count = sum(len(result.placements) for result in layout_results)
    total_pieces = max(len(expanded_pecas), 1)
    piece_coverage = allocated_count / total_pieces * 100.0

    total_area = sum(chapa.area for chapa in expanded_chapas) or 1.0
    used_area = sum(chapa.area - result.waste_area for chapa, result in zip(expanded_chapas, layout_results))
    total_utilization = used_area / total_area * 100.0
    total_waste_area = max(total_area - used_area, 0.0)

    summary = OptimizationSummary(
        algorithm=algorithm_key,
        total_utilization=total_utilization,
        piece_coverage=piece_coverage,
        total_waste_area=total_waste_area,
        allocated_count=allocated_count,
        not_allocated=not_allocated,
        metadata={
            "kerf": kerf,
            "margin": margin,
            "allow_rotation": allow_rotation,
        },
    )

    return summary, layout_results


def evaluate_algorithms(chapas: Sequence[Chapa], pecas: Sequence[Peca], *,
                        allow_rotation: bool = True, kerf: float = 0.0, margin: float = 0.0) -> List[OptimizationSummary]:
    results: List[OptimizationSummary] = []
    for entry in AVAILABLE_ALGORITHMS:
        key = entry["key"]
        try:
            summary, _ = run_algorithm(
                key,
                chapas,
                pecas,
                allow_rotation=allow_rotation,
                kerf=kerf,
                margin=margin,
            )
            results.append(summary)
        except Exception as exc:
            logger.error("Algorithm %s failed: %s", key, exc)
    results.sort(key=lambda item: (item.piece_coverage, item.total_utilization), reverse=True)
    return results


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def calc_area(peca: Peca) -> float:
    shape = getattr(peca, "shape", "rect")
    params = getattr(peca, "params", {})
    if shape == "rect":
        return params.get("w", 0.0) * params.get("h", 0.0)
    if shape == "circ":
        radius = params.get("raio", params.get("r", 0.0))
        return math.pi * radius * radius
    if shape == "poly":
        n = max(int(params.get("n", 3)), 3)
        lado = params.get("lado", 0.0)
        return (n * lado * lado) / (4 * math.tan(math.pi / n)) if lado else 0.0
    return 0.0


def _normalize_defects(chapa: Chapa) -> List[dict]:
    normalized: List[dict] = []
    for defect in getattr(chapa, "defeitos", []) or []:
        if isinstance(defect, dict):
            normalized.append(defect)
        else:
            normalized.append({
                "tipo": getattr(defect, "tipo", "rect"),
                "params": getattr(defect, "params", {}),
            })
    return normalized


def _convert_to_layout_results(chapas: Sequence[Chapa], layouts: Sequence[List[dict]]) -> List[LayoutResult]:
    results: List[LayoutResult] = []
    for chapa, items in zip(chapas, layouts):
        placements: List[Placement] = []
        area_used = 0.0
        for item in items:
            width = float(item.get("w", 0.0))
            height = float(item.get("h", 0.0))
            area_used += width * height
            peca_obj = item.get("peca")
            placement = Placement(
                id=item.get("id", ""),
                chapa_id=chapa.id,
                peca_id=getattr(peca_obj, "id", item.get("id", "")),
                x=float(item.get("x", 0.0)),
                y=float(item.get("y", 0.0)),
                width=width,
                height=height,
                angle=float(item.get("angulo", 0.0)),
                rotation=float(item.get("angulo", 0.0)),
                metadata={
                    "shape": getattr(peca_obj, "shape", None),
                    "params": getattr(peca_obj, "params", {}),
                    "area": width * height,
                },
            )
            placements.append(placement)
        waste_area = max(chapa.area - area_used, 0.0)
        utilization = area_used / chapa.area * 100.0 if chapa.area else 0.0
        results.append(LayoutResult(
            chapa=chapa,
            placements=placements,
            utilization=utilization,
            waste_area=waste_area,
        ))
    return results



















