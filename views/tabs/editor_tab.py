from __future__ import annotations

from typing import Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QFileDialog,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from models.layout import LayoutResult, Placement


class EditorTab(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Editor Visual - Em desenvolvimento"))

        self.status_label = QLabel("Carregue dados, execute a otimizacao e visualize o layout")
        self.status_label.setStyleSheet("color: #a0a0a0; font-style: italic;")

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setMinimumHeight(420)
        self.view.setBackgroundBrush(QColor(30, 31, 35))

        control_row = QHBoxLayout()
        self.zoom_in_btn = QPushButton("Zoom +")
        self.zoom_out_btn = QPushButton("Zoom -")
        self.fit_btn = QPushButton("Ajustar")
        self.refresh_btn = QPushButton("Atualizar")
        control_row.addWidget(self.zoom_in_btn)
        control_row.addWidget(self.zoom_out_btn)
        control_row.addWidget(self.fit_btn)
        control_row.addWidget(self.refresh_btn)
        control_row.addStretch()

        export_row = QHBoxLayout()
        self.export_pdf_btn = QPushButton("Exportar PDF")
        self.export_svg_btn = QPushButton("Exportar SVG")
        export_row.addWidget(self.export_pdf_btn)
        export_row.addWidget(self.export_svg_btn)
        export_row.addStretch()

        layout.addWidget(self.status_label)
        layout.addWidget(self.view)
        layout.addLayout(control_row)
        layout.addLayout(export_row)

        self.zoom_in_btn.clicked.connect(lambda: self.view.scale(1.2, 1.2))
        self.zoom_out_btn.clicked.connect(lambda: self.view.scale(0.8, 0.8))
        self.fit_btn.clicked.connect(self.fit_in_view)
        self.refresh_btn.clicked.connect(self.update_view)
        self.export_pdf_btn.clicked.connect(self._export_pdf)
        self.export_svg_btn.clicked.connect(self._export_svg)

    # ------------------------------------------------------------------
    def update_view(self) -> None:
        layouts = self.controller.get_layouts()
        self._plot_layouts(layouts)

    def fit_in_view(self) -> None:
        if not self.scene.items():
            return
        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _plot_layouts(self, layouts: Sequence[LayoutResult]) -> None:
        self.scene.clear()
        if not layouts:
            self.status_label.setText("Nenhum layout disponivel. Execute a otimizacao primeiro.")
            return

        self.status_label.setText(f"Visualizando {len(layouts)} layout(s)")
        offset_x = 0.0
        padding = 40.0

        for index, result in enumerate(layouts):
            chapa = result.chapa
            board_item = QGraphicsRectItem(offset_x, 0, chapa.w, chapa.h)
            board_item.setPen(QPen(QColor("#f5f5f5"), 2))
            board_item.setBrush(QColor(54, 55, 60))
            self.scene.addItem(board_item)

            header = QGraphicsSimpleTextItem(
                f"Chapa {chapa.id} | Utilizacao {result.utilization:.1f}%"
            )
            header.setBrush(QColor("#f0f0f0"))
            header.setPos(offset_x, -24)
            self.scene.addItem(header)

            for placement in result.placements:
                self._draw_piece(offset_x, placement)

            offset_x += chapa.w + padding

        self.fit_in_view()

    def _draw_piece(self, offset_x: float, placement: Placement) -> None:
        seed = abs(hash(placement.peca_id)) % 255
        color = QColor(80 + seed % 120, 140, 220, 180)
        rect = QGraphicsRectItem(
            offset_x + placement.x,
            placement.y,
            placement.width,
            placement.height,
        )
        rect.setPen(QPen(QColor(20, 20, 24), 1))
        rect.setBrush(color)
        self.scene.addItem(rect)

        label = QGraphicsSimpleTextItem(placement.peca_id)
        label.setBrush(QColor("#111"))
        label.setPos(offset_x + placement.x + 4, placement.y + 4)
        self.scene.addItem(label)

    # ------------------------------------------------------------------
    def _export_pdf(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Exportar PDF", "plano_corte.pdf", "PDF (*.pdf)")
        if filename:
            if not self.controller.export_pdf(filename):
                QMessageBox.warning(self, "Erro", "Falha ao exportar PDF")

    def _export_svg(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Exportar SVG", "plano_corte.svg", "SVG (*.svg)")
        if filename:
            if not self.controller.export_svg(filename):
                QMessageBox.warning(self, "Erro", "Falha ao exportar SVG")

