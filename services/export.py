from __future__ import annotations

from typing import Sequence

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from models.layout import LayoutResult


def export_to_pdf(layouts: Sequence[LayoutResult], filename: str = "plano_corte.pdf") -> bool:
    try:
        doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=18,
            spaceAfter=24,
        )
        elements.append(Paragraph("Plano de Corte - Relatorio", title_style))

        for result in layouts:
            sheet = result.chapa
            elements.append(Paragraph(
                f"Chapa {sheet.id} ({sheet.w:.0f} x {sheet.h:.0f} mm)",
                styles["Heading2"],
            ))
            elements.append(Paragraph(
                f"Aproveitamento: {result.utilization:.1f}% | Sobra: {result.waste_area:.1f} mm2",
                styles["Normal"],
            ))

            data = [["ID", "Peca", "Largura", "Altura", "Posicao", "Angulo"]]
            for placement in result.placements:
                data.append([
                    placement.id,
                    placement.peca_id,
                    f"{placement.width:.1f}",
                    f"{placement.height:.1f}",
                    f"({placement.x:.1f}, {placement.y:.1f})",
                    f"{placement.angle:.0f}?",
                ])

            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
            ]))
            elements.append(table)
        doc.build(elements)
        return True
    except Exception:
        return False

