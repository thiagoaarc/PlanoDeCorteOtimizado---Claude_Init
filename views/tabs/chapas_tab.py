from __future__ import annotations

from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ChapasTab(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Form de entrada
        form = QFormLayout()
        self.id_input = QLineEdit()
        self.width_input = QDoubleSpinBox()
        self.height_input = QDoubleSpinBox()
        self.qty_input = QSpinBox()

        self.width_input.setRange(1, 10000)
        self.height_input.setRange(1, 10000)
        self.qty_input.setRange(1, 1000)

        form.addRow("ID:", self.id_input)
        form.addRow("Largura (mm):", self.width_input)
        form.addRow("Altura (mm):", self.height_input)
        form.addRow("Quantidade:", self.qty_input)

        self.add_btn = QPushButton("Adicionar")
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Largura", "Altura", "Qtd"])

        layout.addLayout(form)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.table)

    def setup_connections(self):
        self.add_btn.clicked.connect(self.on_add)
        self.controller.model.chapa_changed.connect(self.update_table)
        self.controller.error_occurred.connect(self.show_error)

    def on_add(self):
        if not self.id_input.text().strip():
            QMessageBox.warning(self, "Aviso", "ID é obrigatório")
            return

        data = {
            "id": self.id_input.text(),
            "w": self.width_input.value(),
            "h": self.height_input.value(),
            "qtd": self.qty_input.value(),
        }
        self.controller.add_chapa(data)
        self.clear_form()

    def clear_form(self):
        self.id_input.clear()
        self.width_input.setValue(0)
        self.height_input.setValue(0)
        self.qty_input.setValue(1)

    def update_table(self, chapas):
        self.table.setRowCount(len(chapas))
        for i, chapa in enumerate(chapas):
            self.table.setItem(i, 0, QTableWidgetItem(str(chapa.id)))
            self.table.setItem(i, 1, QTableWidgetItem(str(chapa.w)))
            self.table.setItem(i, 2, QTableWidgetItem(str(chapa.h)))
            self.table.setItem(i, 3, QTableWidgetItem(str(chapa.qtd)))

    def show_error(self, message):
        QMessageBox.critical(self, "Erro", message)
    def _handle_remove(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.controller.remove_chapa(row)

    def _clear_inputs(self) -> None:
        self.id_input.clear()
        self.width_input.setValue(0)
        self.height_input.setValue(0)
        self.qty_input.setValue(1)
        self.rebarba_input.setValue(0)

    # ------------------------------------------------------------------
    def reload_table(self) -> None:
        chapas = self.controller.model.chapas
        self.table.setRowCount(len(chapas))
        for row, chapa in enumerate(chapas):
            self.table.setItem(row, 0, QTableWidgetItem(chapa.id))
            self.table.setItem(row, 1, QTableWidgetItem(f"{chapa.w:.1f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{chapa.h:.1f}"))
            self.table.setItem(row, 3, QTableWidgetItem(str(chapa.qtd)))
            self.table.setItem(row, 4, QTableWidgetItem(f"{chapa.rebarba:.1f}"))

