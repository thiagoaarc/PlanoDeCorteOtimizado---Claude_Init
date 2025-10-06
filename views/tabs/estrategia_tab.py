from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class EstrategiaTab(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._build_ui()
        self.update_counts()
        self.refresh_summary()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Estratégia de Otimização - Em desenvolvimento"))

        form = QFormLayout()
        self.algoritmo_combo = QComboBox()
        for entry in self.controller.get_algorithms():
            self.algoritmo_combo.addItem(entry["label"], entry["key"])

        self.kerf_spin = QDoubleSpinBox()
        self.kerf_spin.setRange(0, 50)
        self.kerf_spin.setSingleStep(0.1)
        self.kerf_spin.setValue(2.0)

        self.margem_spin = QDoubleSpinBox()
        self.margem_spin.setRange(0, 50)
        self.margem_spin.setSingleStep(0.5)
        self.margem_spin.setValue(5.0)

        self.priority_spin = QDoubleSpinBox()
        self.priority_spin.setRange(0, 10)
        self.priority_spin.setSingleStep(0.5)
        self.priority_spin.setValue(0.0)

        self.priority_mode_combo = QComboBox()
        self.priority_mode_combo.addItem("Peso unico", "global")
        self.priority_mode_combo.addItem("Dinamico (por algoritmo)", "dynamic")

        self.rotation_check = QCheckBox("Permitir rotacao")
        self.rotation_check.setChecked(True)

        form.addRow("Algoritmo", self.algoritmo_combo)
        form.addRow("Kerf (mm)", self.kerf_spin)
        form.addRow("Margem (mm)", self.margem_spin)
        form.addRow("Peso prioridade", self.priority_spin)
        form.addRow("Modo prioridade", self.priority_mode_combo)
        form.addRow("Rotacao", self.rotation_check)

        button_row = QHBoxLayout()
        self.optimize_btn = QPushButton("Otimizar")
        self.evaluate_btn = QPushButton("Comparar algoritmos")
        self.clear_btn = QPushButton("Limpar layouts")
        button_row.addWidget(self.optimize_btn)
        button_row.addWidget(self.evaluate_btn)
        button_row.addWidget(self.clear_btn)

        self.inventory_label = QLabel("Inventario: 0 chapas | 0 pecas")
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(160)

        self.not_allocated_list = QListWidget()
        self.not_allocated_list.setMinimumHeight(120)

        layout.addLayout(form)
        layout.addLayout(button_row)
        layout.addWidget(self.inventory_label)
        layout.addWidget(QLabel("Resumo da ultima otimizacao:"))
        layout.addWidget(self.summary_text)
        layout.addWidget(QLabel("Pecas nao alocadas:"))
        layout.addWidget(self.not_allocated_list)
        layout.addStretch()

        self.optimize_btn.clicked.connect(self._handle_optimize)
        self.evaluate_btn.clicked.connect(self._handle_evaluate)
        self.clear_btn.clicked.connect(self._handle_clear)

    # ------------------------------------------------------------------
    def _handle_optimize(self) -> None:
        key = self.algoritmo_combo.currentData()
        self.controller.optimize(
            algorithm_key=key,
            kerf=self.kerf_spin.value(),
            margin=self.margem_spin.value(),
            allow_rotation=self.rotation_check.isChecked(),
            priority_weight=self.priority_spin.value(),
        )
        self.refresh_summary()

    def _handle_evaluate(self) -> None:
        best = self.controller.evaluate_best(
            kerf=self.kerf_spin.value(),
            margin=self.margem_spin.value(),
            allow_rotation=self.rotation_check.isChecked(),
            priority_weight=self.priority_spin.value(),
        )
        if best:
            self.refresh_summary()
            self.summary_text.append(
                f"\nMelhor algoritmo sugerido: {best.algorithm.upper()}"
            )

    def _handle_clear(self) -> None:
        self.controller.model.clear_layouts()
        self.summary_text.append("Layouts limpos")
        self.not_allocated_list.clear()

    # ------------------------------------------------------------------
    def update_counts(self) -> None:
        chapas = len(self.controller.model.chapas)
        pecas = sum(getattr(peca, "qtd", 1) for peca in self.controller.model.pecas)
        self.inventory_label.setText(f"Inventario: {chapas} chapas | {pecas} pecas")

    def refresh_summary(self) -> None:
        summary = self.controller.get_summary()
        self.not_allocated_list.clear()
        if not summary:
            self.summary_text.setPlainText("Execute a otimizacao para ver resultados")
            return

        details = [
            f"Algoritmo: {summary.algorithm.upper()}",
            f"Cobertura pecas: {summary.piece_coverage:.1f}%",
            f"Aproveitamento total: {summary.total_utilization:.1f}%",
            f"Area desperdicada: {summary.total_waste_area:.1f} mm2",
            f"Pecas alocadas: {summary.allocated_count}",
            f"Pecas nao alocadas: {len(summary.not_allocated)}",
        ]
        meta = summary.metadata or {}
        applied_weight = meta.get("priority_weight")
        base_weight = meta.get("priority_base")
        if applied_weight is not None:
            details.append(f"Peso prioridade aplicado: {applied_weight:.2f}")
            if base_weight is not None and base_weight != applied_weight:
                details.append(f"Peso base informado: {base_weight:.2f}")
        self.summary_text.setPlainText("\n".join(details))

        for piece in summary.not_allocated:
            display = f"{piece.id} (prioridade {getattr(piece, 'prioridade', 0)})"
            item = QListWidgetItem(display)
            self.not_allocated_list.addItem(item)





