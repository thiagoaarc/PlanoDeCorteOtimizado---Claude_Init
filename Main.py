import sys
import os

# Adiciona o diretório raiz ao Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMessageBox
from controllers.main_controller import MainController
from views.main_window import MainWindow
from models.app_model import AppModel
from services.data_service import DataService


def main():
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        # Inicialização do MVC
        model = AppModel()
        data_service = DataService()
        controller = MainController(model, data_service)

        window = MainWindow(controller)
        window.show()

        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, "Erro Fatal", f"Erro ao iniciar aplicação: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
