from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QPalette
from PyQt6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from views.tabs.chapas_tab import ChapasTab
from views.tabs.editor_tab import EditorTab
from views.tabs.estrategia_tab import EstrategiaTab
from views.tabs.pecas_tab import PecasTab


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Plano de Corte Otimizado")
        self.setGeometry(100, 100, 1120, 720)
        self._setup_palette()
        self._init_ui()
        self._connect_signals()

    # ------------------------------------------------------------------
    def _init_ui(self) -> None:
        central_widget = QWidget(self)
        layout = QVBoxLayout()

        self.toolbar = self._build_toolbar()
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.tab_widget = QTabWidget()
        self.chapas_tab = ChapasTab(self.controller)
        self.pecas_tab = PecasTab(self.controller)
        self.estrategia_tab = EstrategiaTab(self.controller)
        self.editor_tab = EditorTab(self.controller)

        self.tab_widget.addTab(self.chapas_tab, "Chapas")
        self.tab_widget.addTab(self.pecas_tab, "Pecas")
        self.tab_widget.addTab(self.estrategia_tab, "Estrategia")
        self.tab_widget.addTab(self.editor_tab, "Visualizacao")

        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto para iniciar")

    def _build_toolbar(self) -> QToolBar:
        toolbar = QToolBar("Acoes")
        toolbar.setMovable(False)

        load_action = QAction("Carregar", self)
        load_action.triggered.connect(self._load_inventory_dialog)
        toolbar.addAction(load_action)

        save_action = QAction("Salvar", self)
        save_action.triggered.connect(self._save_inventory_dialog)
        toolbar.addAction(save_action)

        export_pdf_action = QAction("Exportar PDF", self)
        export_pdf_action.triggered.connect(self._export_pdf_dialog)
        toolbar.addAction(export_pdf_action)

        export_svg_action = QAction("Exportar SVG", self)
        export_svg_action.triggered.connect(self._export_svg_dialog)
        toolbar.addAction(export_svg_action)

        return toolbar

    def _setup_palette(self) -> None:
        palette = QPalette()
        base_color = QColor(32, 33, 36)
        accent = QColor(55, 155, 255)
        text = QColor(245, 245, 245)
        palette.setColor(QPalette.ColorRole.Window, base_color)
        palette.setColor(QPalette.ColorRole.WindowText, text)
        palette.setColor(QPalette.ColorRole.Base, QColor(45, 46, 48))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(56, 57, 62))
        palette.setColor(QPalette.ColorRole.ToolTipBase, text)
        palette.setColor(QPalette.ColorRole.ToolTipText, base_color)
        palette.setColor(QPalette.ColorRole.Text, text)
        palette.setColor(QPalette.ColorRole.Button, QColor(50, 51, 56))
        palette.setColor(QPalette.ColorRole.ButtonText, text)
        palette.setColor(QPalette.ColorRole.Highlight, accent)
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(12, 12, 12))
        self.setPalette(palette)
        self.setStyleSheet(
            "QToolBar { spacing: 8px; padding: 6px; border: none; }"
            "QStatusBar { color: #f5f5f5; background: #202124; }"
            "QTabWidget::pane { border: 0; }"
        )

    def _connect_signals(self) -> None:
        self.controller.model.status_changed.connect(self.status_bar.showMessage)
        self.controller.model.inventory_changed.connect(self._on_inventory_changed)
        self.controller.model.layout_changed.connect(self.editor_tab.update_view)
        self.controller.model.layout_changed.connect(self.estrategia_tab.refresh_summary)

    # ------------------------------------------------------------------
    # Toolbar actions
    # ------------------------------------------------------------------
    def _load_inventory_dialog(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Carregar inventario", str(Path("data")), "JSON (*.json)")
        if filename:
            try:
                self.controller.load_inventory(filename)
            except Exception as exc:
                QMessageBox.warning(self, "Erro", f"Falha ao carregar inventario: {exc}")

    def _save_inventory_dialog(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Salvar inventario", str(Path("data") / "inventory.json"), "JSON (*.json)")
        if filename:
            try:
                self.controller.save_inventory(filename)
            except Exception as exc:
                QMessageBox.warning(self, "Erro", f"Falha ao salvar inventario: {exc}")

    def _export_pdf_dialog(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Exportar PDF", "plano_corte.pdf", "PDF (*.pdf)")
        if filename:
            if not self.controller.export_pdf(filename):
                QMessageBox.warning(self, "Erro", "Falha ao exportar PDF")

    def _export_svg_dialog(self) -> None:
        filename, _ = QFileDialog.getSaveFileName(self, "Exportar SVG", "plano_corte.svg", "SVG (*.svg)")
        if filename:
            if not self.controller.export_svg(filename):
                QMessageBox.warning(self, "Erro", "Falha ao exportar SVG")

    # ------------------------------------------------------------------
    def _on_inventory_changed(self) -> None:
        self.chapas_tab.reload_table()
        self.pecas_tab.reload_table()
        self.estrategia_tab.update_counts()

