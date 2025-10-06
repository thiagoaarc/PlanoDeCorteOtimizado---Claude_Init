from __future__ import annotations

from typing import Sequence

import svgwrite

from models.layout import LayoutResult, Placement


COLOR_PALETTE = [
    ("#8ecae6", "#219ebc"),
    ("#ffb703", "#fb8500"),
    ("#bde0fe", "#023047"),
    ("#cddafd", "#3f37c9"),
]


def export_to_svg(layouts: Sequence[LayoutResult], filename: str = "plano_corte.svg") -> bool:
    try:
        dwg = svgwrite.Drawing(filename, profile="tiny", size=("1200px", "1600px"))
        y_offset = 60

        dwg.add(dwg.text("Legenda", insert=(20, 30), font_size="18px", font_weight="bold"))
        legend_items = [
            ("#8ecae6", "#219ebc", "Retangular"),
            ("#90be6d", "#2d6a4f", "Circular"),
            ("#ffc8dd", "#ff7096", "Poligonal"),
        ]
        legend_x = 20
        for fill, stroke, label in legend_items:
            dwg.add(dwg.rect((legend_x, 40), (24, 16), fill=fill, stroke=stroke))
            dwg.add(dwg.text(label, insert=(legend_x + 30, 52), font_size="12px"))
            legend_x += 140

        for index, result in enumerate(layouts):
            sheet = result.chapa
            x0, y0 = 40, y_offset
            dwg.add(dwg.rect((x0, y0), (sheet.w, sheet.h), fill="#f5f5f5", stroke="#222", stroke_width=2))
            dwg.add(dwg.text(
                f"Chapa {sheet.id} ({sheet.w:.0f} x {sheet.h:.0f} mm)",
                insert=(x0, y0 - 12),
                font_size="14px",
                font_weight="bold",
            ))
            for placement in result.placements:
                _draw_piece(dwg, placement, offset=(x0, y0))
            y_offset += sheet.h + 80
        dwg.save()
        return True
    except Exception:
        return False


def _draw_piece(dwg: svgwrite.Drawing, placement: Placement, offset: tuple[float, float]) -> None:
    ox, oy = offset
    shape = placement.metadata.get("shape")
    params = placement.metadata.get("params", {})
    fill, stroke = COLOR_PALETTE[hash(placement.peca_id) % len(COLOR_PALETTE)]

    if shape == "circ":
        radius = params.get("raio", params.get("r", placement.width / 2))
        dwg.add(dwg.circle(
            center=(ox + placement.x + radius, oy + placement.y + radius),
            r=radius,
            fill=fill,
            stroke=stroke,
        ))
    else:
        dwg.add(dwg.rect(
            (ox + placement.x, oy + placement.y),
            (placement.width, placement.height),
            fill=fill,
            stroke=stroke,
        ))
    dwg.add(dwg.text(
        placement.peca_id,
        insert=(ox + placement.x + 4, oy + placement.y + 14),
        font_size="11px",
        fill="#1b1b1b",
    ))

