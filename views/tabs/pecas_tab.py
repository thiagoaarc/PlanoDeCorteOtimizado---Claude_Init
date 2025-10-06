from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
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

from services.optimization import calc_area


class PecasTab(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.id_input = QLineEdit()
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(["rect", "circ", "poly"])
        self.width_input = QDoubleSpinBox()
        self.height_input = QDoubleSpinBox()
        self.qty_input = QSpinBox()

        self.width_input.setRange(1, 10000)
        self.height_input.setRange(1, 10000)
        self.qty_input.setRange(1, 1000)

        form.addRow("ID:", self.id_input)
        form.addRow("Formato:", self.shape_combo)
        form.addRow("Largura:", self.width_input)
        form.addRow("Altura:", self.height_input)
        form.addRow("Quantidade:", self.qty_input)

        self.add_btn = QPushButton("Adicionar")
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Formato", "Dimensões", "Qtd", "Área"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        layout.addLayout(form)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.table)

    def setup_connections(self):
        self.add_btn.clicked.connect(self.on_add)
        self.controller.model.peca_changed.connect(self.update_table)
        self.controller.error_occurred.connect(self.show_error)

    # ------------------------------------------------------------------
    def on_add(self) -> None:
        if not self.id_input.text().strip():
            QMessageBox.warning(self, "Aviso", "ID é obrigatório")
            return

        data = {
            "id": self.id_input.text(),
            "shape": self.shape_combo.currentText(),
            "params": {"w": self.width_input.value(), "h": self.height_input.value()},
            "qtd": self.qty_input.value(),
        }
        self.controller.add_peca(data)
        self.clear_form()

    def clear_form(self):
        self.id_input.clear()
        self.width_input.setValue(0)
        self.height_input.setValue(0)
        self.qty_input.setValue(1)

    def update_table(self, pecas):
        self.table.setRowCount(len(pecas))
        for i, peca in enumerate(pecas):
            self.table.setItem(i, 0, QTableWidgetItem(str(peca.id)))
            self.table.setItem(i, 1, QTableWidgetItem(str(peca.shape)))
            dims = f"{peca.params.get('w', 0)}x{peca.params.get('h', 0)}"
            self.table.setItem(i, 2, QTableWidgetItem(dims))
            self.table.setItem(i, 3, QTableWidgetItem(str(peca.qtd)))
            area = peca.params.get("w", 0) * peca.params.get("h", 0)
            self.table.setItem(i, 4, QTableWidgetItem(f"{area:.2f}"))

    def show_error(self, message):
        QMessageBox.critical(self, "Erro", message)

    # ------------------------------------------------------------------
    def reload_table(self) -> None:
        pecas = self.controller.model.pecas
        self.table.setRowCount(len(pecas))
        for row, peca in enumerate(pecas):
            params_text = str(peca.params)
            area = calc_area(peca)
            self.table.setItem(row, 0, QTableWidgetItem(peca.id))
            self.table.setItem(row, 1, QTableWidgetItem(peca.shape))
            self.table.setItem(row, 2, QTableWidgetItem(params_text))
            self.table.setItem(row, 3, QTableWidgetItem(str(peca.qtd)))
            self.table.setItem(row, 4, QTableWidgetItem(f"{area:.1f}"))
                }
            self.controller.add_peca(data)
            self._clear_inputs()
        except Exception as exc:
            QMessageBox.warning(self, "Erro", str(exc))

    def _handle_remove(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.controller.remove_peca(row)

    def _clear_inputs(self) -> None:
        self.id_input.clear()
        self.width_input.setValue(0)
        self.height_input.setValue(0)
        self.radius_input.setValue(0)
        self.side_input.setValue(0)
        self.sides_input.setValue(3)
        self.qty_input.setValue(1)
        self.priority_input.setValue(0)

    def _update_param_visibility(self, shape: str) -> None:
        is_rect = shape == "rect"
        is_circ = shape == "circ"
        is_poly = shape == "poly"
        self.width_input.setEnabled(is_rect)
        self.height_input.setEnabled(is_rect)
        self.radius_input.setEnabled(is_circ)
        self.side_input.setEnabled(is_poly)
        self.sides_input.setEnabled(is_poly)

    # ------------------------------------------------------------------
    def reload_table(self) -> None:
        pecas = self.controller.model.pecas
        self.table.setRowCount(len(pecas))
        for row, peca in enumerate(pecas):
            params_text = str(peca.params)
            area = calc_area(peca)
            self.table.setItem(row, 0, QTableWidgetItem(peca.id))
            self.table.setItem(row, 1, QTableWidgetItem(peca.shape))
            self.table.setItem(row, 2, QTableWidgetItem(params_text))
            self.table.setItem(row, 3, QTableWidgetItem(str(peca.qtd)))
            self.table.setItem(row, 4, QTableWidgetItem(f"{area:.1f}"))

