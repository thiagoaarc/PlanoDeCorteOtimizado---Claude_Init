import logging
import os
from datetime import datetime


class CustomLogger:
    def __init__(self):
        self.logger = logging.getLogger("PlanoCorte")
        if self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            return

        self.logger.setLevel(logging.INFO)

        log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
        os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(
            os.path.join(log_dir, f"plano_corte_{datetime.now():%Y%m%d}.log")
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
