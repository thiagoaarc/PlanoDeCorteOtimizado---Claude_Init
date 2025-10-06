#!/usr/bin/env python3
"""Script simples para testar os principais componentes da aplicacao."""

import sys

from PyQt6.QtWidgets import QApplication

from controllers.main_controller import MainController
from views.main_window import MainWindow


def test_app() -> bool:
    """Executa uma bateria minima de smoke tests sem abrir a janela."""
    print(">> Testando componentes da aplicacao...")

    try:
        controller = MainController()
        print("OK - Controller criado")
    except Exception as exc:  # pragma: no cover - script manual
        print(f"ERRO - Falha ao criar controller: {exc}")
        return False

    try:
        app = QApplication(sys.argv if sys.argv else [])
        print("OK - QApplication criado")
    except Exception as exc:
        print(f"ERRO - Falha ao criar QApplication: {exc}")
        return False

    try:
        window = MainWindow(controller)
        window.close()
        print("OK - MainWindow criado")
    except Exception as exc:
        print(f"ERRO - Falha ao criar MainWindow: {exc}")
        return False

    try:
        from models.chapa import Chapa
        from models.peca import Peca

        chapa = Chapa(id="C1", w=1000, h=800, qtd=1)
        peca = Peca(id="P1", shape="rect", params={"w": 100, "h": 200}, qtd=2)
        print(f"OK - Chapa criada: {chapa.id} ({chapa.w}x{chapa.h} mm)")
        print(f"OK - Peca criada: {peca.id} ({peca.shape}, area {peca.area} mm2)")
    except Exception as exc:
        print(f"ERRO - Falha ao criar modelos: {exc}")
        return False

    print("\n>>> SUCESSO! Todos os testes passaram!")
    print(">>> A aplicacao esta pronta para uso.")
    print("\n>>> Para executar a aplicacao completa:")
    print("    python Main.py")

    return True


if __name__ == "__main__":
    success = test_app()
    sys.exit(0 if success else 1)
